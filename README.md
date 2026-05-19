# Realtime UV Risk Predictor - *Apply sunscreen now!*

A realtime MLOps system that predicts UV exposure risk across global cities and helps users make informed sun-safety decisions.


We use 11 globally distributed cities to ensure strong variation in UV exposure patterns:

- **Zurich** — Mid-latitude temperate baseline with strong seasonal UV variation.  
- **Dubai** — Extreme UV from desert climate and consistently clear skies.  
- **Nairobi** — Equatorial high UV with minimal seasonal variation.  
- **Sydney** — Southern hemisphere seasonality (inverted UV cycles).  
- **Reykjavik** — High-latitude, low solar angle, strong winter UV drop-off.  
- **New York City** — Urban mid-latitude with strong seasonal and weather-driven variability.  
- **Bogotá** — High-altitude equatorial UV amplification.  
- **Bangkok** — Tropical monsoon climate with seasonal cloud-driven UV changes.  
- **Jakarta** — Equatorial maritime UV with frequent cloud variability.  
- **Singapore** — Stable equatorial UV baseline with minimal seasonal change.  
- **Havana** — Subtropical maritime climate with consistently high UV exposure. 

To extend coverage, simply add new entries to the `CITIES` dictionary under `common/cities.py`.

# Set up

### 1. Copy `.env.sample` to `.env` and set the environment variable `HOPSWORKS_API_KEY` to your Hopsworks API key.
Get your Hopsworks API key from https://www.hopsworks.ai/.

### 2. Build and start all services: `docker compose up --build`.
All dependencies are installed inside Docker containers, no local Python environment or requirements file is required.

On build-and-start the feature and training pipelines start first.

Feature data is generated every 10 minutes and continuously uploaded to the Hopsworks feature store (*offline feature group*) for downstream training and inference. The ingestion data source is the Open-Meteo Weather API, using the past two months of historical data.

The training pipeline waits until sufficient features are available in the feature store before starting model training.

Once training completes successfully, the trained model is uploaded to Hopsworks model registry, and the training container exits.

The inference service starts last (it depends on the training container exiting). **You must wait for it to be ready before proceeding**.

The inference data source is the Open-Meteo Weather API, using the past day and the current day. Realtime data is also continuously uploaded to the Hopsworks feature store (*realtime feature group*). 

The best available model in the Hopsworks model registry is used by the inference service.

Requests to the predict API are *cached*. 

### 3. Access the interference-app in your browser: `http://localhost:8000`

# Pipelines

## 1. Feature Pipeline

### 1.1 Used features and their relevance for UV Risk Prediction

#### Open-Meteo

The following data points are collected from the Open-Meteo Weather API:

- `uv_index`: Represents the intensity of ultraviolet radiation and serves as the primary target variable for UV risk prediction.
- `cloud_cover`: Indicates the percentage of sky covered by clouds, which directly affects UV exposure by blocking or scattering solar radiation.
- `temperature_2m`: Measures air temperature at 2 meters above ground and serves as an indirect indicator of solar intensity and atmospheric heating conditions related to UV levels.
- `relative_humidity_2m`: Represents atmospheric moisture content, which influences weather conditions such as cloud formation and can indirectly impact UV radiation levels.

Additional contextual features:

- `timestamp`: Provides temporal context, enabling the model to learn daily and seasonal UV patterns, as well as time-dependent variations in weather conditions. Is not directly fed to the model, but used for sorting and calculating derived time features.
- `city` (`lat`, `lon`): Provides geographical context for weather and UV predictions.

#### Calculated features

##### Time Features
The following cyclical time-based features are derived from the `timestamp` field to help the model capture daily and seasonal UV patterns:

- `hour_sin`, `hour_cos`: Cyclical encoding of the hour of day using sine and cosine transformations. This preserves the continuous nature of time (e.g. 23:00 and 00:00 are close in representation).
- `doy_sin`, `doy_cos`: Cyclical encoding of the day of year, enabling the model to learn seasonal effects and annual UV trends.

##### Weather Features

Additional weather-derived features are engineered to improve predictive performance and capture short-term atmospheric changes:

- `temp_norm`: Normalized air temperature (`temperature_2m / 40`) used to scale temperature values into a consistent range for model training.
- `humidity_norm`: Normalized relative humidity (`relative_humidity_2m / 100`) used to standardize atmospheric moisture values.
- `cloud_trend`: Measures the change in cloud cover between consecutive observations for a given city, capturing short-term cloud movement and weather dynamics.
- `cloud_mean_3h`: Rolling 3-sample average of cloud cover for each city, providing a smoothed representation of recent atmospheric conditions.

##### Location Features

Geographical features are derived from latitude coordinates to help the model learn regional UV behavior:

- `is_hot_region`: Boolean indicator identifying locations within tropical and subtropical regions (`|latitude| < 30`), where UV exposure is generally higher.
- `is_northern`: Binary indicator specifying whether a location is in the Northern Hemisphere.


##### Labels

The following prediction targets are generated for supervised learning:

- `uv_high_next`: Binary classification label indicating whether the UV index value for next hour is considered high risk (`uv_index >= 6`).


### 1.2. Feature Store Integration

The engineered feature dataset (historical feature data used for model training and batch processing) is stored in the Hopsworks Feature Store using a dedicated feature group for offline training. A custom feature group name can be configured using the `HOPSWORKS_FEATURE_GROUP_NAME` environment variable.

The feature group is continuously populated by the feature engineering pipeline every 10 minutes.

The feature group is configured with:
- **primary key**: `city` + `timestamp`
- **event time**: `timestamp`

## 2. Training Pipeline

The training pipeline loads engineered features from the Hopsworks Feature Store, trains a supervised machine learning model for UV risk prediction, evaluates its performance, and uploads the trained model to the Hopsworks Model Registry.

### 2.1. Feature availability

Before training begins, the pipeline continuously checks to ensure that sufficient feature data for training is available in the feature store.

### 2.2. Feature retrieval

The pipeline reads data from the configured offline Hopsworks Feature Group (env var: `HOPSWORKS_FEATURE_GROUP_NAME`, version `1`)

A feature view (env var: `HOPSWORKS_FEATURE_VIEW_NAME`) is created to define the exact training dataset schema and selected features.

### 2.3. Model training
The model is trained using a `RandomForestClassifier` using balanced class weighting (`class_weight="balanced"`) to compensate for potential class imbalance between low-risk and high-risk UV events.

A chronological train/test split is used to simulate real-world forecasting conditions. While chronological splitting may introduce temporal distribution shifts (e.g. seasonal differences or day/night imbalance), cyclical time features (`hour_sin`, `hour_cos`, `doy_sin`, `doy_cos`) are included to help the model learn recurring temporal patterns and mitigate these effects.

The target variable `uv_high_next` is constructed using a temporal shift of the UV index, ensuring a one-step-ahead forecasting setup without data leakage.


## 3. Inference Pipeline

The inference pipeline retrieves realtime weather data, generates prediction features, loads the best available model from the Hopsworks Model Registry, and performs UV risk predictions through a FastAPI service. Hence, inference-time feature computation is partially performed in the application layer (inference-data is not loaded via Hopsworks Feature Views), resulting in a hybrid feature generation approach.


### 3.1. User Interface & API

The inference pipeline consists of a FastAPI-based prediction API and a simple user interface available at:

``` id="1z2h8s"
http://localhost:8000
```

Predictions are served via the `/predict` endpoint, returning a binary UV risk label and a user-friendly message.

### 3.2. Realtime Data & Feature Processing
When a request is received, the latest weather data (previous and current day) is fetched from the Open-Meteo Weather API. The same feature engineering pipeline used during training is applied to ensure consistent preprocessing and avoid training-serving skew.

### 3.3. Model Loading Strategy

At application startup, the best model is loaded from the Hopsworks Model Registry.

The model is selected based on highest **recall** score, prioritizing detection of high UV risk events and minimizing missed dangerous exposures.

### 3.4. Caching

Prediction results are cached per city and UTC hour to reduce redundant API calls and improve response latency.

### 3.5. Realtime Logging

After inference, features and predictions are stored in a dedicated realtime feature group in Hopsworks for monitoring and future reuse.

---
# Reflection & Limitations

## 1. Feature Engineering and Temporal Dependencies

The pipeline combines raw meteorological data from Open-Meteo with engineered time, weather, and location-based features. While this increases model expressiveness, it introduces a strong dependency on temporal structure.

In particular, rolling statistics and differencing-based features rely on sequential observations. This makes the model sensitive to timestamp alignment and data continuity, meaning that small changes in temporal ordering or missing observations can influence feature values and therefore predictions.

## 2. Temporal Feature Sensitivity

Time-based encodings (sine/cosine transformations of hour and day-of-year) are strong predictors of UV exposure. While effective, they can dominate model behaviour in regions with stable weather conditions (e.g., desert climates such as Dubai).

This leads to the model learning strong periodic patterns, sometimes outweighing short-term weather variations.

## 3. Realtime Data Constraints

Inference relies on the most recent weather observation retrieved from the Open-Meteo API. In contrast, training is based on dense historical sequences with multiple observations per city.

This discrepancy introduces a mild distribution shift between training and inference, particularly for features that benefit from longer temporal context.

## 4. Feature Store and System-Level Trade-offs

The system uses Hopsworks as a feature store to ensure reproducibility between training and inference pipelines. However, realtime feature writes are asynchronous and may introduce minor latency or duplicate-write conflicts under concurrent requests.

These issues were mitigated using background tasks and idempotent inserts, but eventual consistency is still a design consideration.

The feature store is used as an offline training source and online logging sink, not an online feature retrieval layer.

## 5. Model Limitations

The model is formulated as a binary classification problem using a fixed threshold (UV ≥ 6). While this simplifies deployment and interpretation, it reduces the granularity of risk estimation and does not capture uncertainty or gradual transitions in UV intensity.

Furthermore, model performance was not the primary optimization goal; the focus of this project is the end-to-end MLOps pipeline rather than achieving state-of-the-art predictive accuracy.

## 6. Reliance to Open-Meteo API

The system depends on the Open-Meteo for all its data. This introduces rate limits and availability constraints. Moreover, if the API is slow, down, or changes its data, both training and predictions are affected.

## 7. What is missing for a production-ready system

* Proper fault tolerance (retries - especially in regard to Open-Meteo API, circuit breakers, robust API failure handling)
* Real observability (metrics dashboards, structured logging, drift monitoring)
* Data validation layer (schema checks, outlier detection, stronger missing-data strategy)
* Scalable infrastructure (no single-instance assumption, no Redis/external cache, no orchestration like Kubernetes, 
tight service coupling, e.g., inference startup depends on training completion)
* Deployment maturity (no staging/production separation, no model rollback or canary deployments)
* Strong monitoring of model performance over time (no continuous evaluation or alerting)
* Automated testing (unit, integration, and end-to-end tests for pipelines, feature engineering, and inference APIs)

## 8. What is missing for production-grade ML

* Baseline comparisons (e.g., logistic regression or naive models)
* Proper time-series validation (e.g., cross-validation instead of single split)
* Uncertainty estimation and probability calibration
* More expressive problem formulation (e.g., regression or ordinal prediction instead of binary thresholding)
* Ablation studies to quantify feature importance and contribution
* Larger and more diverse dataset (longer time range, more seasonal coverage)
* More advanced temporal/spatial models beyond feature engineering + Random Forest 
