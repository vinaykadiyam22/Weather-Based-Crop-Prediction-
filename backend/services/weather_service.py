"""
Weather service - Andhra Pradesh focused.
Uses Open-Meteo API (free, no API key required) for live weather.
"""
import requests
from config import get_settings
from datetime import datetime, timedelta

settings = get_settings()

# Andhra Pradesh: location to city for weather (Open-Meteo geocoding)
# When user enters "Andhra Pradesh" or AP district, resolve to nearest major city
AP_WEATHER_CITIES = {
    "andhra pradesh": "Vijayawada", "andhra": "Vijayawada", "ap": "Vijayawada",
    "vijayawada": "Vijayawada", "vizag": "Visakhapatnam", "visakhapatnam": "Visakhapatnam",
    "guntur": "Guntur", "kurnool": "Kurnool", "nellore": "Nellore",
    "rajahmundry": "Rajahmundry", "tirupati": "Tirupati", "kadapa": "Kadapa",
    "anantapur": "Anantapur", "eluru": "Eluru", "ongole": "Ongole",
    "kakinada": "Kakinada", "vizianagaram": "Vizianagaram", "srikakulam": "Srikakulam",
}
DEFAULT_WEATHER_CITY = "Vijayawada"  # Andhra Pradesh capital region

# Open-Meteo WMO weather code to description mapping
WEATHER_CODES = {
    0: ("Clear", "clear sky"),
    1: ("Clear", "mainly clear"),
    2: ("Clouds", "partly cloudy"),
    3: ("Clouds", "overcast"),
    45: ("Mist", "foggy"),
    48: ("Mist", "depositing rime fog"),
    51: ("Drizzle", "light drizzle"),
    53: ("Drizzle", "moderate drizzle"),
    55: ("Drizzle", "dense drizzle"),
    61: ("Rain", "slight rain"),
    63: ("Rain", "moderate rain"),
    65: ("Rain", "heavy rain"),
    66: ("Rain", "light freezing rain"),
    67: ("Rain", "heavy freezing rain"),
    71: ("Snow", "slight snow"),
    73: ("Snow", "moderate snow"),
    75: ("Snow", "heavy snow"),
    77: ("Snow", "snow grains"),
    80: ("Rain", "slight rain showers"),
    81: ("Rain", "moderate rain showers"),
    82: ("Rain", "violent rain showers"),
    85: ("Snow", "slight snow showers"),
    86: ("Snow", "heavy snow showers"),
    95: ("Thunderstorm", "thunderstorm"),
    96: ("Thunderstorm", "thunderstorm with hail"),
    99: ("Thunderstorm", "thunderstorm with heavy hail"),
}


class WeatherService:
    OPEN_METEO_GEO = "https://geocoding-api.open-meteo.com/v1/search"
    OPEN_METEO_WEATHER = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.openweather_api_key = getattr(settings, "openweather_api_key", "") or ""

    def _geocode(self, city: str) -> tuple:
        """Convert city/state name to lat, lon. Andhra Pradesh focused."""
        if not city or not city.strip():
            city = DEFAULT_WEATHER_CITY
        loc = city.strip().lower()
        search_city = AP_WEATHER_CITIES.get(loc, city)
        try:
            r = requests.get(
                self.OPEN_METEO_GEO,
                params={"name": search_city, "count": 1, "language": "en", "country": "India"},
                timeout=10,
            )
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            if results:
                return results[0]["latitude"], results[0]["longitude"]
        except Exception as e:
            print(f"Geocoding error: {e}")
        return None, None

    def _fetch_openmeteo(self, lat: float, lon: float) -> dict:
        """Fetch weather and forecast from Open-Meteo (free, no key)."""
        try:
            r = requests.get(
                self.OPEN_METEO_WEATHER,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": "true",
                    "hourly": "temperature_2m,relativehumidity_2m,precipitation",
                    "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min",
                    "timezone": "auto",
                },
                timeout=10,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Open-Meteo API error: {e}")
            return {}

    def _openmeteo_to_current(self, data: dict) -> dict:
        """Map Open-Meteo response to our expected current weather format."""
        if not data or "current_weather" not in data:
            return self._get_mock_weather()

        cw = data["current_weather"]
        code = cw.get("weathercode", 0)
        main_name, desc = WEATHER_CODES.get(code, ("Clear", "clear sky"))

        # Get humidity from hourly (current hour index)
        humidity = 70
        if "hourly" in data and "relativehumidity_2m" in data["hourly"]:
            hums = data["hourly"]["relativehumidity_2m"]
            if hums:
                humidity = hums[min(24, len(hums) - 1)]

        # Wind: Open-Meteo uses km/h, our code expects m/s (climate_alert does * 3.6)
        wind_kmh = cw.get("windspeed", 0)
        wind_ms = wind_kmh / 3.6

        return {
            "main": {
                "temp": cw.get("temperature", 25),
                "feels_like": cw.get("temperature", 25),
                "humidity": humidity,
                "pressure": 1012,
            },
            "weather": [{"main": main_name, "description": desc}],
            "wind": {"speed": wind_ms},
            "clouds": {"all": 20 if code in (2, 3) else 0},
        }

    def _openmeteo_to_forecast(self, data: dict) -> dict:
        """Map Open-Meteo daily data to our forecast list format."""
        if not data or "daily" not in data:
            return self._get_mock_forecast()

        daily = data["daily"]
        times = daily.get("time", [])
        precip = daily.get("precipitation_sum", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])

        forecast_list = []
        for i in range(min(5, len(times))):
            dt_txt = f"{times[i]} 12:00:00" if i < len(times) else ""
            # precipitation_sum is mm/day; pass as rain for heavy-rain alert check
            rain_mm = precip[i] if i < len(precip) else 0
            forecast_list.append({
                "dt_txt": dt_txt,
                "main": {
                    "temp": (temp_max[i] + temp_min[i]) / 2 if i < len(temp_max) else 28,
                    "humidity": 65,
                },
                "weather": [{"main": "Clear", "description": "clear sky"}],
                "rain": {"3h": rain_mm},
            })
        return {"list": forecast_list}

    def get_current_weather(self, city: str = None, lat: float = None, lon: float = None):
        """Get live current weather. Default: Vijayawada (Andhra Pradesh)."""
        if not lat or not lon:
            lat, lon = self._geocode(city or DEFAULT_WEATHER_CITY)

        if not lat or not lon:
            return self._get_mock_weather()

        # Use Open-Meteo (free, no key)
        data = self._fetch_openmeteo(lat, lon)
        return self._openmeteo_to_current(data)

    def get_forecast(self, city: str = None, lat: float = None, lon: float = None, days: int = 5):
        """Get live weather forecast. Default: Vijayawada (Andhra Pradesh)."""
        if not lat or not lon:
            lat, lon = self._geocode(city or DEFAULT_WEATHER_CITY)
        if not lat or not lon:
            return self._get_mock_forecast()

        data = self._fetch_openmeteo(lat, lon)
        return self._openmeteo_to_forecast(data)

    def _get_mock_weather(self):
        """Fallback mock weather (used only on API failure)."""
        return {
            "main": {"temp": 28.5, "feels_like": 30.2, "humidity": 65, "pressure": 1012},
            "weather": [{"main": "Clear", "description": "clear sky"}],
            "wind": {"speed": 3.5},
            "clouds": {"all": 20},
        }

    def _get_mock_forecast(self):
        """Fallback mock forecast (used only on API failure)."""
        return {
            "list": [
                {
                    "dt_txt": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d 12:00:00"),
                    "main": {"temp": 28 + i, "humidity": 60 + i},
                    "weather": [{"main": "Clear", "description": "clear sky"}],
                    "rain": {"3h": 0},
                }
                for i in range(5)
            ]
        }


weather_service = WeatherService()
