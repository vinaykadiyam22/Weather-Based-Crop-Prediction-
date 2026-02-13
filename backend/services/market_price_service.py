"""
Market price service - Andhra Pradesh focused.
Season and location aware crop prices. Uses data.gov.in API when key is set.
"""
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import get_settings

settings = get_settings()

# Default state: Andhra Pradesh (app is AP-focused)
DEFAULT_STATE = "Andhra Pradesh"

# Andhra Pradesh districts/cities
AP_LOCATIONS = {
    "vijayawada": "Andhra Pradesh", "visakhapatnam": "Andhra Pradesh", "vizag": "Andhra Pradesh",
    "guntur": "Andhra Pradesh", "kurnool": "Andhra Pradesh", "nellore": "Andhra Pradesh",
    "rajahmundry": "Andhra Pradesh", "tirupati": "Andhra Pradesh", "kadapa": "Andhra Pradesh",
    "anantapur": "Andhra Pradesh", "eluru": "Andhra Pradesh", "ongole": "Andhra Pradesh",
    "kakinada": "Andhra Pradesh", "adoni": "Andhra Pradesh", "anakapalli": "Andhra Pradesh",
    "vizianagaram": "Andhra Pradesh", "srikakulam": "Andhra Pradesh", "chittoor": "Andhra Pradesh",
    "andhra": "Andhra Pradesh", "andhra pradesh": "Andhra Pradesh", "ap": "Andhra Pradesh",
}

# AP-specific mandis/markets (for fallback price display)
AP_MARKETS = [
    "Guntur Chilli Yard", "Vijayawada Rythu Bazar", "Kurnool APMC", "Rajahmundry Mandi",
    "Visakhapatnam Market", "Tirupati APMC", "Nellore Mandi", "Kakinada Port Market",
    "Anantapur APMC", "Eluru Rythu Bazar", "Ongole Groundnut Yard",
]

# City/region to state mapping (India) - AP locations first
LOCATION_TO_STATE = {
    **AP_LOCATIONS,
    "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra",
    "delhi": "NCT of Delhi", "bangalore": "Karnataka", "bengaluru": "Karnataka",
    "chennai": "Tamil Nadu", "madras": "Tamil Nadu",
    "hyderabad": "Telangana", "kolkata": "West Bengal", "calcutta": "West Bengal",
    "ahmedabad": "Gujarat", "surat": "Gujarat", "vadodara": "Gujarat",
    "jaipur": "Rajasthan", "lucknow": "Uttar Pradesh", "kanpur": "Uttar Pradesh",
    "chandigarh": "Punjab", "ludhiana": "Punjab", "amritsar": "Punjab",
    "patna": "Bihar", "indore": "Madhya Pradesh", "bhopal": "Madhya Pradesh",
    "bhubaneswar": "Odisha", "coimbatore": "Tamil Nadu", "kochi": "Kerala",
    "thiruvananthapuram": "Kerala",
}

# India crop seasons by month (1=Jan, 2=Feb, ...)
# Kharif: Jun-Oct (6-10), Rabi: Nov-Mar (11,12,1,2,3), Summer: Apr-May (4,5)
def get_current_season() -> str:
    m = datetime.now().month
    if 6 <= m <= 10:
        return "Kharif"
    if m in (11, 12, 1, 2, 3):
        return "Rabi"
    return "Summer"


def _resolve_state(location: str) -> str:
    """Resolve user location (city/state) to state name. Default: Andhra Pradesh."""
    if not location or not location.strip():
        return DEFAULT_STATE
    loc = location.strip().lower()
    if loc in LOCATION_TO_STATE:
        return LOCATION_TO_STATE[loc]
    for city, state in LOCATION_TO_STATE.items():
        if city in loc or loc in city:
            return state
    # Check if it's already a state (from crops.json)
    states = [
        "Punjab", "Haryana", "Maharashtra", "Gujarat", "Andhra Pradesh",
        "Karnataka", "Tamil Nadu", "West Bengal", "Uttar Pradesh", "Madhya Pradesh",
        "Rajasthan", "Telangana", "Bihar", "Kerala", "Odisha"
    ]
    for s in states:
        if s.lower() in loc or loc in s.lower():
            return s
    return DEFAULT_STATE  # default: Andhra Pradesh


def get_season_crops_for_location(location: str) -> List[Dict]:
    """Get crops suitable for current season and user's location from crops.json."""
    state = _resolve_state(location)
    season = get_current_season()

    crops_file = Path(__file__).parent.parent / "data" / "crops.json"
    try:
        with open(crops_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            crops = data.get("crops", [])
    except Exception:
        return []

    result = []
    for c in crops:
        seasons = c.get("seasons", [])
        states = c.get("states", [])
        if (season in seasons or "Year-round" in seasons) and (
            state in states or not states
        ):
            result.append({
                "name": c["name"],
                "local_name": c.get("local_name", ""),
                "season": season,
                "states": states,
            })
    return result


# Realistic price ranges (₹/quintal) - Andhra Pradesh market rates
# AP is major producer of: Chilli (Guntur), Rice, Groundnut, Cotton, Tobacco
CROP_BASE_PRICES = {
    "Rice": (1800, 3200), "Wheat": (2000, 2800), "Cotton": (5500, 7500),
    "Groundnut": (4500, 6500), "Sugarcane": (300, 350), "Maize": (1800, 2400),
    "Pulses (Tur)": (8000, 12000), "Jowar (Sorghum)": (1800, 2200),
    "Pearl Millet (Bajra)": (1500, 2200), "Tomato": (800, 4000),
    "Potato": (800, 1800), "Onion": (1000, 3500),
    "Chilli": (12000, 22000), "Tobacco": (8000, 15000), "Turmeric": (6000, 12000),
}


def _fetch_from_datagov(commodity: str, state: str) -> Optional[List[Dict]]:
    """Fetch from data.gov.in API if key is set."""
    api_key = getattr(settings, "data_gov_in_api_key", None) or ""
    if not api_key or api_key == "your_datagov_key":
        return None
    try:
        # Resource ID for agricultural prices (may need update)
        url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0060"
        params = {
            "api-key": api_key,
            "format": "json",
            "limit": 50,
            "filters[state]": state,
            "filters[commodity]": commodity,
        }
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        records = data.get("records", [])
        if not records:
            return None
        out = []
        for rec in records[:20]:
            pr = rec.get("modal_price") or rec.get("max_price") or rec.get("min_price")
            if pr:
                try:
                    price = float(pr)
                except (TypeError, ValueError):
                    continue
                out.append({
                    "state": rec.get("state", state),
                    "market": rec.get("market", "Mandi"),
                    "price": price,
                    "date": rec.get("date", datetime.now().date().isoformat()),
                })
        return out if out else None
    except Exception as e:
        print(f"Market price API error: {e}")
        return None


def _generate_fallback_prices(crop_name: str, state: str) -> List[Dict]:
    """Generate realistic fallback prices when API unavailable."""
    base_range = CROP_BASE_PRICES.get(crop_name, (1500, 3000))
    markets = AP_MARKETS if state == "Andhra Pradesh" else ["APMC Market", "Mandi", "Rythu Bazar", "Local Market"]
    prices = []
    import random
    for i in range(30):
        date = datetime.now().date() - timedelta(days=i)
        base = (base_range[0] + base_range[1]) / 2
        var = random.uniform(-0.15, 0.15)
        price = round(base * (1 + var), 2)
        prices.append({
            "state": state,
            "market": random.choice(markets),
            "price": price,
            "date": date.isoformat(),
        })
    return prices


def get_season_prices_for_location(
    location: str,
) -> Dict:
    """
    Get market prices for season crops in user's location.
    Returns dict with crops array, each with name, prices, trend, etc.
    """
    state = _resolve_state(location)
    season = get_current_season()
    crops = get_season_crops_for_location(location)

    if not crops:
        # Fallback to popular crops
        crops = [{"name": n} for n in ["Rice", "Wheat", "Potato", "Onion", "Tomato"]]

    result = {
        "location": location,
        "state": state,
        "season": season,
        "crops": [],
    }

    for c in crops[:8]:  # Max 8 crops
        name = c["name"]
        api_prices = _fetch_from_datagov(name, state)
        if api_prices:
            price_list = api_prices
        else:
            price_list = _generate_fallback_prices(name, state)

        if not price_list:
            continue

        latest = price_list[0]["price"]
        older = price_list[-1]["price"] if len(price_list) > 1 else latest
        trend = "up" if latest > older else "down" if latest < older else "stable"
        change = ((latest - older) / older * 100) if older > 0 else 0

        result["crops"].append({
            "crop_name": name,
            "latest_price": latest,
            "trend": trend,
            "change_percent": round(change, 2),
            "prices": price_list[:10],
            "prices_count": len(price_list),
        })

    return result


def get_crop_prices_for_location(
    crop_name: str,
    location: str,
    days: int = 30,
) -> Dict:
    """Get prices for a specific crop in user's location."""
    state = _resolve_state(location)
    api_prices = _fetch_from_datagov(crop_name, state)
    if api_prices:
        price_list = api_prices
    else:
        price_list = _generate_fallback_prices(crop_name, state)

    if not price_list:
        return {"crop_name": crop_name, "prices": [], "latest_price": None, "trend": "stable", "change_percent": 0}

    latest = price_list[0]["price"]
    older = price_list[-1]["price"] if len(price_list) > 1 else latest
    trend = "up" if latest > older else "down" if latest < older else "stable"
    change = ((latest - older) / older * 100) if older > 0 else 0

    return {
        "crop_name": crop_name,
        "prices": [
            {"state": p["state"], "market": p["market"], "price": p["price"], "date": p["date"]}
            for p in price_list[:20]
        ],
        "count": len(price_list),
        "trend": trend,
        "change_percent": round(change, 2),
        "latest_price": latest,
    }
