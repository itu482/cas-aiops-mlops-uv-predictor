import requests
import pandas as pd
import datetime

from common import CITIES, build_open_meteo_url, parse_open_meteo_response, prep_features_inference

def fetch_weather_latest_hour(city: str):
    lat, lon = CITIES[city]

    url = build_open_meteo_url(lat, lon)

    data = requests.get(url).json()
    
    df = parse_open_meteo_response(data, city, lat, lon)
    df = prep_features_inference(df)
    
    now_hour = pd.Timestamp.now(datetime.timezone.utc).floor("h")

    latest_row = df.iloc[(df["timestamp"] - now_hour).abs().argsort()[0]]
    latest = latest_row.to_dict()
    latest["timestamp"] = now_hour
    
    print(latest)

    return latest