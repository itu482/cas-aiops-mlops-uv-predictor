import pandas as pd
import joblib
import os
import hashlib
import json

from config import HOPSWORKS_MODEL_NAME

cache = {}

def make_cache_key(raw):
    normalized = json.dumps(raw, sort_keys=True, default=str)
    return hashlib.md5(normalized.encode()).hexdigest()

def load_model_from_dir(model_dir):
    files = os.listdir(model_dir)

    for f in files:
        if f.endswith(".pkl"):
            return joblib.load(os.path.join(model_dir, f))

    raise FileNotFoundError(f"No .pkl model found in {model_dir}")

def load_best_model(project):
    mr = project.get_model_registry()

    best_model = mr.get_best_model(
        HOPSWORKS_MODEL_NAME,
        "recall",
        "max"
    )

    model_dir = best_model.download()
    return load_model_from_dir(model_dir)

def predict_weather(model, raw):
    df = pd.DataFrame([raw])

    X = df.drop(columns=["uv_high_next", "timestamp"], errors="ignore")

    pred = int(model.predict(X)[0])

    return pred
