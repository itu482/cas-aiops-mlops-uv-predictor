import requests
import pandas as pd
from common import CITIES, build_open_meteo_url_historic, parse_open_meteo_response

def fetch_weather(lat, lon):
    url = build_open_meteo_url_historic(lat, lon)
    return requests.get(url).json()

def fetch_city_data(city_name, lat, lon):
    data = fetch_weather(lat, lon)

    df = parse_open_meteo_response(data, city_name, lat, lon)

    return df

def fetch_uv_data_all_cities():
    dfs = []

    for city, (lat, lon) in CITIES.items():
        df = fetch_city_data(city, lat, lon)
        dfs.append(df)

    result = pd.concat(dfs, ignore_index=True)
    
    return result