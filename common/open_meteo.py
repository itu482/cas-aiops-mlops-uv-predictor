from common.config import OPEN_METEO_API_BASE_URL, OPEN_METEO_API_HOURLY_VARS, OPEN_METEO_API_PAST_DAYS, TIMEZONE
from urllib.parse import urlencode
import pandas as pd

def build_open_meteo_url(lat: float, lon: float, past_days: int|None = 1):
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": OPEN_METEO_API_HOURLY_VARS,
        "timezone": TIMEZONE,
        "forecast_days": 1,
        "past_days": past_days
    }
    
    url = f"{OPEN_METEO_API_BASE_URL}?{urlencode(params)}"

    print(url)

    return url

def build_open_meteo_url_historic(lat: float, lon: float):
    return build_open_meteo_url(lat, lon, past_days=OPEN_METEO_API_PAST_DAYS)

def parse_open_meteo_response(data: dict, city: str, lat: float, lon: float) -> pd.DataFrame:
    n = len(data["hourly"]["time"])

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(data["hourly"]["time"], utc=True),
        "uv_index": data["hourly"]["uv_index"],
        "cloud_cover": data["hourly"]["cloud_cover"],
        "temperature_2m": data["hourly"]["temperature_2m"],
        "relative_humidity_2m": data["hourly"]["relative_humidity_2m"],
        "city": [city] * n,
        "lat": [lat] * n,
        "lon": [lon] * n,
    })

    return df