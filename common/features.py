import numpy as np
import pandas as pd

def add_time_features(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    hour = df["timestamp"].dt.hour
    day_of_year = df["timestamp"].dt.dayofyear

    df["hour_sin"] = np.sin(2 * np.pi * hour / 24)
    df["hour_cos"] = np.cos(2 * np.pi * hour / 24)

    df["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365)
    df["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365)

    return df

def add_weather_features(df):
    # Simple normalization
    df["temp_norm"] = df["temperature_2m"] / 40.0
    df["humidity_norm"] = df["relative_humidity_2m"] / 100.0
    
    # Real-time-feature (current condition)
    df["cloud_trend"] = df.groupby("city")["cloud_cover"].diff()
    
    # Aggregated / Rolling-window feature
    df["cloud_mean_3h"] = (
        df.groupby("city")["cloud_cover"]
        .rolling(3)
        .mean()
        .reset_index(level=0, drop=True)
    )

    return df


def add_location_features(df):
    df["is_hot_region"] = df["lat"].abs() < 30
    df["is_northern"] = (df["lat"] > 0).astype(int)

    return df


def add_labels(df):
    df = df.sort_values(["city", "timestamp"])

    # predict UV one step ahead (next hour / next sample)
    df["uv_future"] = df.groupby("city")["uv_index"].shift(-1)

    # classification target: high UV risk
    df["uv_high_next"] = (df["uv_future"] >= 6).astype(int)

    # drop uv_future used as scaffolding for label uv_high_next, avoid dataleaks (!)
    df = df.drop(columns=["uv_future"])

    return df

def add_features(df):
    df = add_time_features(df)
    df = add_weather_features(df)
    df = add_location_features(df)

    return df

def prep_features_ingest(df):
    df = df.sort_values(["city", "timestamp"])

    df = add_features(df)
    df = add_labels(df)
    
    df = df.dropna()

    return df

def prep_features_inference(df):
    df = df.sort_values(["city", "timestamp"])

    df = add_features(df)
    
    return df