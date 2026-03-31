"""
Map Intelligence Route
- Accepts lat/lon
- Returns real village-level geocoding, live weather from Open-Meteo, and AI crop recommendations
"""
from fastapi import APIRouter
from pydantic import BaseModel
import requests
import json

router = APIRouter(prefix="/api/map", tags=["Map Intelligence"])

class LocationRequest(BaseModel):
    lat: float
    lon: float

# ─── Soil type estimates based on world geography ────────────────────────────
# Since SoilGrids has CORS issues and is slow for real-time use, we use a
# curated soil classification based on country + climate region.
COUNTRY_SOIL_MAP = {
    "India": {
        "default": "Alluvial Soil (Fluvisol) / Red Soil (Acrisol)",
        "by_state": {
            "Andhra Pradesh": "Alluvial + Red & Black Soil (Vertisol + Acrisol)",
            "Punjab": "Alluvial Soil (Fluvisol) — highly fertile",
            "Rajasthan": "Arid Desert Soil (Aridisol / Arenosol)",
            "Maharashtra": "Black Cotton Soil (Vertisol)",
            "Karnataka": "Red Laterite Soil (Acrisol / Ferralsol)",
            "Telangana": "Black Soil (Vertisol) + Red Soil (Acrisol)",
            "Tamil Nadu": "Red Loamy Soil (Acrisol) + Alluvial",
            "Kerala": "Laterite Soil (Plinthosol)",
            "Uttar Pradesh": "Alluvial Soil (Fluvisol)",
            "West Bengal": "Alluvial Delta Soil (Fluvisol)",
            "Gujarat": "Black Soil (Vertisol) + Saline Soils",
            "Bihar": "Alluvial Soil (Fluvisol)",
            "Odisha": "Red & Laterite Soil (Acrisol)",
            "Madhya Pradesh": "Black Cotton Soil (Vertisol)",
            "Haryana": "Alluvial Soil (Fluvisol)",
            "Jharkhand": "Red Laterite Soil (Plinthosol)",
            "Himachal Pradesh": "Mountain Brown Forest Soil (Cambisol)",
            "Uttarakhand": "Mountain Alluvial Soil (Inceptisol)",
            "Assam": "Alluvial + Laterite (Fluvisol + Plinthosol)",
        }
    },
    "China": "Loess Soil (Cambisol) / Paddy Soil (Gleysol)",
    "United States of America": "Mollisol (Prairie) / Sandy Loam",
    "United States": "Mollisol (Prairie) / Sandy Loam",
    "Brazil": "Oxisol (Ferralsol) — deep red weathered",
    "Russia": "Chernozem (Black Earth) / Podzol",
    "Australia": "Vertisol + Aridisol (Desert Sandy)",
    "France": "Cambisol / Luvisol — Brown Forest Soil",
    "Germany": "Cambisol / Luvisol",
    "Japan": "Andosol (Volcanic Ash Soil)",
    "Indonesia": "Oxisol / Inceptisol (Tropical Weathered)",
    "Pakistan": "Alluvial Soil (Fluvisol)",
    "Bangladesh": "Deltaic Alluvial Soil (Fluvisol)",
    "Vietnam": "Acrisol / Gleysol (Paddy Soils)",
    "Nigeria": "Alfisol / Oxisol",
    "Ethiopia": "Vertisol / Alfisol (Highland)",
    "Egypt": "Alluvial Nile Soil (Fluvisol) / Desert Sand",
    "Ukraine": "Chernozem — World's most fertile Black Earth",
    "Argentina": "Mollisol (Pampas) — very fertile",
    "Canada": "Chernozem / Luvisol / Cryosol (North)",
    "South Africa": "Calcisol / Vertisol",
    "Kenya": "Nitisol / Vertisol (Highland)",
    "Mexico": "Vertisol / Phaeozem",
    "Spain": "Calcisol / Cambisol (Mediterranean)",
    "Italy": "Cambisol / Vertisol",
    "Turkey": "Vertisol / Cambisol",
    "Thailand": "Acrisol / Gleysol (Paddy)",
}


def get_soil_description(country: str, state: str = None) -> str:
    entry = COUNTRY_SOIL_MAP.get(country)
    if entry is None:
        return "Mixed Soil Types (varied topography)"
    if isinstance(entry, dict):
        if state and state in entry.get("by_state", {}):
            return entry["by_state"][state]
        return entry.get("default", "Alluvial / Mixed Soil")
    return entry


def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch real weather from Open-Meteo (free, no API key)."""
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "hourly": "relativehumidity_2m,precipitation",
                "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                "timezone": "auto",
            },
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        cw = data.get("current_weather", {})
        hourly = data.get("hourly", {})
        daily = data.get("daily", {})

        humidity = 65
        if hourly.get("relativehumidity_2m"):
            humidity = hourly["relativehumidity_2m"][min(12, len(hourly["relativehumidity_2m"]) - 1)]

        rainfall = 0.0
        if daily.get("precipitation_sum"):
            rainfall = daily["precipitation_sum"][0] or 0.0

        temp_max = daily.get("temperature_2m_max", [None])[0]
        temp_min = daily.get("temperature_2m_min", [None])[0]
        temp = cw.get("temperature", 28.0)

        # Weather code → description
        code = cw.get("weathercode", 0)
        WMO = {0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
               45: "Foggy", 51: "Light Drizzle", 61: "Rain", 63: "Moderate Rain",
               65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"}
        condition = WMO.get(code, "Clear")

        return {
            "temp": round(temp, 1),
            "temp_max": round(temp_max, 1) if temp_max is not None else None,
            "temp_min": round(temp_min, 1) if temp_min is not None else None,
            "humidity": humidity,
            "rainfall": round(rainfall, 1),
            "wind_speed": round(cw.get("windspeed", 0), 1),
            "condition": condition,
            "success": True,
        }
    except Exception as e:
        print(f"[MAP] Weather fetch error: {e}")
        return {"success": False}


def recommend_crops_ai(soil: str, weather: dict, country: str, state: str) -> list:
    """Use Gemini AI to intelligently recommend crops based on real soil + weather."""
    try:
        from config import get_settings
        import google.generativeai as genai

        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        temp = weather.get("temp", 28)
        humidity = weather.get("humidity", 65)
        rainfall = weather.get("rainfall", 0)
        condition = weather.get("condition", "Clear")

        prompt = f"""You are an expert agricultural scientist.
Based on the following real-time data, recommend EXACTLY 4 best crops to grow.

Location: {state or ''}, {country}
Soil Type: {soil}
Current Temperature: {temp}°C
Humidity: {humidity}%
Daily Rainfall: {rainfall}mm
Weather: {condition}

Rules:
- Only recommend crops that grow well in this SPECIFIC soil type AND weather combination
- Consider the climate zone, temperature range, and moisture levels
- Be geographically accurate
- Return ONLY a JSON list, no explanation. Example: ["Rice", "Wheat", "Cotton", "Sorghum"]
- Exactly 4 crops, each a simple crop name"""

        response = model.generate_content(prompt)
        text = response.text.strip()
        # Parse JSON from response
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end > start:
            crops = json.loads(text[start:end])
            return [str(c).strip() for c in crops[:4] if c]
    except Exception as e:
        print(f"[MAP] Gemini crop recommendation error: {e}")

    # Fallback: rule-based
    return rule_based_crops(soil, weather)


def rule_based_crops(soil: str, weather: dict) -> list:
    """Deterministic fallback based on soil + weather rules."""
    soil_l = soil.lower()
    temp = weather.get("temp", 28)
    humidity = weather.get("humidity", 65)
    rainfall = weather.get("rainfall", 0)

    high_water = humidity > 72 or rainfall > 5
    low_water = humidity < 48 and rainfall == 0 and temp > 30
    hot = temp > 34
    cool = temp < 18

    if "vertisol" in soil_l or "black" in soil_l:
        return ["Cotton", "Sorghum", "Bengal Gram", "Sunflower"] if not high_water else ["Soybean", "Cotton", "Sugarcane", "Maize"]
    if "fluvisol" in soil_l or "alluvial" in soil_l:
        return ["Rice", "Sugarcane", "Banana", "Jute"] if high_water else ["Wheat", "Maize", "Mustard", "Vegetables"]
    if "acrisol" in soil_l or "red" in soil_l:
        return ["Groundnut", "Ragi", "Red Gram", "Sesame"] if not high_water else ["Rubber", "Cashew", "Mango", "Tea"]
    if "ferralsol" in soil_l or "laterite" in soil_l or "plinthosol" in soil_l:
        return ["Cashew", "Coconut", "Rubber", "Pineapple"] if high_water else ["Groundnut", "Cassava", "Mango", "Millet"]
    if "arenosol" in soil_l or "sandy" in soil_l or "arid" in soil_l:
        return ["Pearl Millet", "Groundnut", "Sesame", "Cowpea"]
    if "gleysol" in soil_l or "paddy" in soil_l:
        return ["Rice", "Taro", "Lotus", "Sugarcane"]
    if "chernozem" in soil_l or "mollisol" in soil_l or "pampas" in soil_l:
        return ["Wheat", "Maize", "Sunflower", "Sugar Beet"] if not hot else ["Soybean", "Maize", "Sorghum", "Sunflower"]
    if "cambisol" in soil_l or "brown" in soil_l:
        return ["Potatoes", "Barley", "Oilseed Rape", "Sugar Beet"] if cool else ["Wheat", "Barley", "Maize", "Vegetables"]
    if "calcisol" in soil_l or "limestone" in soil_l:
        return ["Olives", "Grapes", "Wheat", "Pistachios"] if not hot else ["Date Palm", "Figs", "Sorghum", "Alfalfa"]
    if "andosol" in soil_l or "volcanic" in soil_l:
        return ["Tea", "Coffee", "Potatoes", "Vegetables"]

    # Generic fallback by weather
    if high_water and hot: return ["Rice", "Sugarcane", "Banana", "Coconut"]
    if low_water: return ["Pearl Millet", "Groundnut", "Sesame", "Sorghum"]
    if cool: return ["Wheat", "Barley", "Potatoes", "Mustard"]
    return ["Maize", "Wheat", "Sorgum", "Vegetables"]


@router.post("/intelligence")
async def get_location_intelligence(req: LocationRequest):
    """
    All-in-one map intelligence endpoint:
    - Real weather from Open-Meteo
    - Soil description for the country/state
    - AI crop recommendation via Gemini (fallback to rules if unavailable)
    """
    lat, lon = req.lat, req.lon

    # 1. Reverse geocode using Nominatim
    try:
        geo_r = requests.get(
            f"https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "zoom": 18, "addressdetails": 1},
            headers={"Accept-Language": "en", "User-Agent": "CropAdvisorySystem/1.0"},
            timeout=8,
        )
        geo = geo_r.json()
        addr = geo.get("address", {})
        village = addr.get("village") or addr.get("hamlet") or addr.get("town") or addr.get("suburb") or addr.get("neighbourhood")
        mandal = addr.get("county") or addr.get("subdistrict") or addr.get("municipality")
        district = addr.get("district") or addr.get("city")
        state = addr.get("state") or addr.get("region")
        country = addr.get("country", "Unknown")
    except Exception as e:
        print(f"[MAP] Geocoding error: {e}")
        village = mandal = district = state = None
        country = "Unknown"

    # 2. Fetch real weather
    weather = fetch_weather(lat, lon)

    # 3. Determine soil type
    soil = get_soil_description(country, state)

    # 4. Get AI crop recommendations
    crops = recommend_crops_ai(soil, weather, country, state)

    return {
        "location": {
            "village": village,
            "mandal": mandal,
            "district": district,
            "state": state,
            "country": country,
            "lat": lat,
            "lon": lon,
        },
        "weather": weather,
        "soil": soil,
        "crops": crops,
    }
