"""
Gemini API service - Uses google-genai SDK (matches reference implementation).
Optimized for FREE tier with strict quota protection.
"""
from google import genai
from google.genai import types
from config import get_settings
import time
import hashlib
import threading
from typing import Dict, Optional

settings = get_settings()

# Initialize client with API key (same pattern as reference)
_api_key = settings.gemini_api_key or ""
_client = None
_client_lock = threading.Lock()


def _get_client():
    """Get or create Gemini client; uses GEMINI_API_KEY from env if not in settings."""
    global _client
    with _client_lock:
        if _client is not None:
            return _client
        api_key = _api_key or ""
        if not api_key:
            import os
            api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            print("[GEMINI] ERROR: No API key. Set GEMINI_API_KEY in .env")
            return None
        try:
            _client = genai.Client(api_key=api_key)
            print("[GEMINI] Client initialized successfully")
            return _client
        except Exception as e:
            print(f"[GEMINI] Failed to create client: {e}")
            return None


# ===== FREE TIER PROTECTION =====

_api_lock = threading.Lock()
_response_cache: Dict[str, tuple] = {}
CACHE_DURATION_SEC = 60
_last_request_time = 0
MIN_REQUEST_INTERVAL = 2.0


def _get_cache_key(prompt: str, temperature: float) -> str:
    return hashlib.md5(f"{prompt}_{temperature}".encode()).hexdigest()


def _get_cached(cache_key: str) -> Optional[str]:
    now = time.time()
    if cache_key in _response_cache:
        text, stored_at = _response_cache[cache_key]
        if now - stored_at < CACHE_DURATION_SEC:
            print("[CACHE] Hit - saved API quota")
            return text
        del _response_cache[cache_key]
    return None


def _save_to_cache(cache_key: str, text: str):
    _response_cache[cache_key] = (text, time.time())
    now = time.time()
    to_remove = [k for k, (_, t) in _response_cache.items() if now - t >= CACHE_DURATION_SEC]
    for k in to_remove:
        del _response_cache[k]


def _wait_rate_limit():
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        wait = MIN_REQUEST_INTERVAL - elapsed
        print(f"[RATE] Waiting {wait:.1f}s before next request")
        time.sleep(wait)
    _last_request_time = time.time()


def get_gemini_response(prompt: str, temperature: float = 0.7, use_cache: bool = True) -> str:
    """
    Get Gemini response using google-genai SDK (matches reference implementation).
    client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    """
    cache_key = _get_cache_key(prompt, temperature)

    if use_cache:
        cached = _get_cached(cache_key)
        if cached:
            return cached

    with _api_lock:
        if use_cache:
            cached = _get_cached(cache_key)
            if cached:
                return cached

        _wait_rate_limit()

        client = _get_client()
        if not client:
            return "Advisory generation temporarily unavailable. Please set GEMINI_API_KEY in .env and restart."

        print("[API] Gemini request")
        try:
            # Match reference: client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature),
            )
            result = response.text.strip() if response.text else ""

            if use_cache:
                _save_to_cache(cache_key, result)
            return result

        except Exception as e:
            print(f"[GEMINI] API error: {type(e).__name__}: {e}")
            return "Advisory generation temporarily unavailable. Please try again later."


# Shared format instructions for all advisories (UI-ready, structured)
_FORMAT_RULES = """
OUTPUT FORMAT (STRICT):
- Use markdown headings (##) and bullet points.
- Start with a 2–3 line Summary. No greetings (no "Namaste", "Dear farmer", etc.).
- Keep sentences short. No long paragraphs or storytelling.
- Be direct, practical, and farmer-friendly.
"""

# CRITICAL: Prevents blind/generic recommendations. Must stay in all prompts.
_CONTROL_SENTENCE = (
    "Do not generate generic recommendations. Base suggestions strictly on the provided "
    "analysis parameters and explain reasoning explicitly."
)


LANG_NAMES = {"en": "English", "hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati"}

# Native script examples for stronger translation enforcement
LANG_SCRIPTS = {
    "hi": "हिन्दी",
    "ta": "தமிழ்",
    "te": "తెలుగు",
    "bn": "বাংলা",
    "mr": "मराठी",
    "gu": "ગુજરાતી",
}


def _lang_instruction(language: str) -> str:
    """Returns strong, explicit language instruction for Gemini to output in the requested language."""
    if not language or language == "en":
        return ""
    lang_name = LANG_NAMES.get(language, language)
    script = LANG_SCRIPTS.get(language, "")
    script_part = f" ({script})" if script else ""
    return (
        f"\n\nCRITICAL LANGUAGE RULE: Generate the ENTIRE response ONLY in {lang_name}{script_part}. "
        f"Every heading, bullet point, and sentence must be in {lang_name}. Do NOT use English or any other language. "
        f"Use {lang_name} script and vocabulary appropriate for Indian farmers."
    )


def generate_disease_advisory(
    disease_name: str,
    confidence: float,
    crop_name: str = "crop",
    crop_type: str = None,
    language: str = "en",
) -> str:
    """Generate disease advisory: explanation, severity, treatment. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    crop = crop_name or crop_type or "crop"
    prompt = f"""Generate a structured advisory for DISEASE DETECTION module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Crop: {crop}
- Identified condition: {disease_name}
- Confidence: {confidence:.1%}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: what was detected, severity level, key implication)

## Analysis
- What this condition means for {crop}
- How it affects the plant
- Typical severity and spread

## Treatment
- Immediate actions (bullet list)
- Recommended products/methods if applicable

## Prevention
- Steps to avoid recurrence
- Best practices

## Key Actions
- List 3–5 short, actionable items
- When to consult an expert{lang_instruction}"""
    use_cache = (language or "en") == "en"
    return get_gemini_response(prompt, temperature=0.6, use_cache=use_cache)


def generate_climate_advisory(event_type: str, severity: str, location: str, weather_data: dict, language: str = "en") -> str:
    """Generate climate advisory: risk, timeline, preventive measures. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    prompt = f"""Generate a structured advisory for CLIMATE ALERTS module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Location: {location}
- Event: {event_type}
- Severity: {severity}
- Weather: {weather_data}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: what is happening, when, and main risk)

## Risk Explanation
- What this event means for crops
- Which crops are most at risk
- Expected timeline

## Preventive Measures
- Immediate protective actions (bullet list)
- Short-term precautions

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    return get_gemini_response(prompt, temperature=0.5, use_cache=use_cache)


def generate_crop_recommendation_explanation(
    recommended_crops: list,
    soil_type: str,
    season: str,
    location: str,
    language: str = "en",
    soil_analysis: dict = None,
    weather_forecast: dict = None,
    market_data: dict = None,
    climate_alerts: list = None,
) -> str:
    """
    Generate crop recommendation advisory from STRUCTURED ANALYSIS DATA.
    Workflow: Data Analysis → Structured Parameters → Gemini → Formatted Advisory.
    Gemini must NOT invent; it explains based on provided data only.
    """
    lang_instruction = _lang_instruction(language)
    crops_list = ", ".join(c.get("name", c) if isinstance(c, dict) else c for c in recommended_crops)

    data_parts = [
        f"Location: {location}",
        f"Soil Type: {soil_type}",
        f"Season: {season}",
        f"Recommended Crops (pre-filtered by analysis): {crops_list}",
    ]
    if soil_analysis:
        data_parts.append(f"Soil Analysis: {soil_analysis}")
    if weather_forecast:
        data_parts.append(f"Weather Forecast: {weather_forecast}")
    if market_data:
        data_parts.append(f"Market Data (prices, trends): {market_data}")
    if climate_alerts:
        data_parts.append(f"Active Climate Alerts: {climate_alerts}")

    data_block = "\n".join(f"- {p}" for p in data_parts)

    prompt = f"""Generate a structured advisory for CROP RECOMMENDATION module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent or assume):
{data_block}

{_CONTROL_SENTENCE}

For each recommended crop, explain: why suitable for soil and climate; expected benefits and economic advantage; basic cultivation guidance; precautions if risks exist (e.g. from climate alerts or market).

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: why these crops suit the analyzed conditions; reference concrete data)

## Suitability
- Why each crop fits soil and season (cite parameters)
- Compatibility with {location}

## Benefits
- Expected benefits per crop
- Market/demand context if provided
- Growing duration (brief)

## Care Steps
- Basic requirements for success
- Key cultivation tips

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    return get_gemini_response(prompt, use_cache=use_cache)


def generate_soil_analysis_explanation(soil_params: dict, fertilizer_recommendations: list, language: str = "en") -> str:
    """Generate soil analysis advisory: nutrients, condition, fertilizer guidance. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    fertilizer_str = ", ".join(fertilizer_recommendations)
    prompt = f"""Generate a structured advisory for SOIL ANALYSIS module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Soil Parameters: {soil_params}
- Recommended Fertilizers: {fertilizer_str}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: soil condition overview, main finding)

## Nutrient Analysis
- What each parameter indicates
- Strengths and deficiencies

## Fertilizer Guidance
- Why each recommended fertilizer
- Application doses and timing

## Precautions
- Application guidelines
- Safety and mixing notes

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    return get_gemini_response(prompt, use_cache=use_cache)


def generate_soil_type_explanation(soil_type: str, characteristics: dict, language: str = "en") -> str:
    """Generate soil type advisory: nutrients, condition, suitability. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    prompt = f"""Generate a structured advisory for SOIL TYPE (manual selection) module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Soil Type: {soil_type}
- Characteristics: {characteristics}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: what this soil type means for farming)

## Soil Condition
- Strengths
- Limitations to be aware of

## Best Crops
- Crops well-suited to this soil
- Why they perform well

## Improvement Tips
- How to improve soil health
- Practical steps

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    return get_gemini_response(prompt, use_cache=use_cache)


def generate_market_advisory(
    crop_name: str,
    trend: str,
    change_percent: float,
    latest_price: float,
    location: str = None,
    language: str = "en",
) -> str:
    """Generate market advisory: price trend insight and action suggestions. UI-ready format."""
    lang_instruction = _lang_instruction(language)
    loc_str = f"Location: {location}" if location else ""
    prompt = f"""Generate a structured advisory for MARKET ADVISORY module.
{_FORMAT_RULES}

ANALYSIS DATA (use ONLY this — do not invent):
- Crop: {crop_name}
- Price Trend: {trend}
- Change: {change_percent}%
- Latest Price: ₹{latest_price}/quintal
{loc_str}

{_CONTROL_SENTENCE}

OUTPUT STRUCTURE (use these exact headings):
## Summary
(2–3 lines: price trend, current level, main implication)

## Price Insight
- What the trend indicates
- Typical factors affecting this crop

## Action Suggestions
- When to sell (if applicable)
- When to hold or wait
- Market timing tips

## Key Actions
- List 3–5 short, actionable items{lang_instruction}"""
    use_cache = (language or "en") == "en"
    return get_gemini_response(prompt, use_cache=use_cache)


def clear_cache():
    global _response_cache
    _response_cache.clear()
    print("[OK] Cache cleared")


def get_cache_stats() -> dict:
    now = time.time()
    valid = sum(1 for _, (_, t) in _response_cache.items() if now - t < CACHE_DURATION_SEC)
    return {
        "total_cached": len(_response_cache),
        "valid_cached": valid,
        "cache_duration_sec": CACHE_DURATION_SEC,
    }
