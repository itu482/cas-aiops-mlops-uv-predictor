from fastapi import FastAPI
from fastapi import BackgroundTasks
from fastapi.responses import HTMLResponse

import hashlib
import json
import pandas as pd
import datetime

from common import CITIES, get_project

from load_inference_data import fetch_weather_latest_hour
from predict import predict_weather, load_best_model
from save_realtime import save_realtime_features


hopsworks_project = get_project()
model = load_best_model(hopsworks_project) 

cache = {}

def make_cache_key(raw):
    normalized = json.dumps(raw, sort_keys=True, default=str)
    return hashlib.md5(normalized.encode()).hexdigest()
app = FastAPI()

def make_message(pred: int):
    if pred == 1:
        return "⚠️ High UV expected soon. Apply sunscreen and avoid midday sun."
    return "☀️ Low UV risk. Normal outdoor conditions."


@app.get("/predict")
def predict(city: str, background_tasks: BackgroundTasks):
    key = make_cache_key((city, pd.Timestamp.now(datetime.timezone.utc).floor("h")))
    
    if key in cache:
        return {
            "city": city,
            "uv_high_next": int(cache[key]),
            "message": make_message(cache[key])
        } 
    raw = fetch_weather_latest_hour(city)
    pred = predict_weather(model, raw)
    cache[key] = pred
    background_tasks.add_task(save_realtime_features, raw, pred, hopsworks_project)

    return {
        "city": city,
        "uv_high_next": int(pred),
        "message": make_message(pred)
    }

@app.get("/", response_class=HTMLResponse)
def ui():
    options = "\n".join(
        f'<option value="{city}">{city.capitalize()}</option>'
        for city in CITIES.keys()
    )

    return f"""
    <html>
        <head>
            <title>UV Predictor</title>

            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: Arial, sans-serif;
                }}

                body {{
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;

                    background: linear-gradient(
                        135deg,
                        #0f172a,
                        #1e293b,
                        #334155
                    );

                    color: white;
                }}

                .card {{
                    width: 420px;
                    padding: 40px;

                    border-radius: 24px;

                    background: rgba(255,255,255,0.08);

                    backdrop-filter: blur(14px);

                    box-shadow:
                        0 8px 32px rgba(0,0,0,0.35);

                    text-align: center;
                }}

                h1 {{
                    font-size: 2rem;
                    margin-bottom: 10px;
                }}

                p {{
                    color: #cbd5e1;
                    margin-bottom: 30px;
                }}

                select {{
                    width: 100%;
                    padding: 14px;

                    border: none;
                    border-radius: 12px;

                    background: #1e293b;
                    color: white;

                    font-size: 1rem;

                    margin-bottom: 20px;
                }}

                button {{
                    width: 100%;
                    padding: 14px;

                    border: none;
                    border-radius: 12px;

                    background: linear-gradient(
                        90deg,
                        #f59e0b,
                        #ef4444
                    );

                    color: white;
                    font-size: 1rem;
                    font-weight: bold;

                    cursor: pointer;

                    transition: all 0.25s ease;
                }}

                button:hover {{
                    transform: translateY(-2px);
                    opacity: 0.92;

                    box-shadow:
                        0 6px 20px rgba(239,68,68,0.4);
                }}

                #result {{
                    margin-top: 28px;

                    font-size: 1.15rem;
                    line-height: 1.6;
                }}

                .spinner {{
                    display: inline-block;
                    width: 18px;
                    height: 18px;

                    border: 3px solid rgba(255,255,255,0.3);
                    border-top: 3px solid white;

                    border-radius: 50%;

                    animation: spin 1s linear infinite;

                    vertical-align: middle;
                    margin-right: 8px;
                }}

                @keyframes spin {{
                    0% {{
                        transform: rotate(0deg);
                    }}
                    100% {{
                        transform: rotate(360deg);
                    }}
                }}
            </style>
        </head>

        <body>

            <div class="card">

                <h1>☀️ UV Predictor</h1>

                <p>
                    Predict high UV exposure for the next hour.
                </p>

                <select id="city">
                    {options}
                </select>

                <button onclick="predict()">
                    Predict UV Risk
                </button>

                <div id="result"></div>

            </div>

            <script>
                async function predict() {{
                    const city = document.getElementById("city").value;

                    document.getElementById("result").innerHTML =
                        '<div class="spinner"></div> Predicting...';

                    try {{
                        const res = await fetch(`/predict?city=${{city}}`);
                        const data = await res.json();

                        document.getElementById("result").innerHTML =
                            data.message;

                    }} catch (err) {{

                        document.getElementById("result").innerHTML =
                            "Error fetching prediction";

                    }}
                }}
            </script>

        </body>
    </html>
    """