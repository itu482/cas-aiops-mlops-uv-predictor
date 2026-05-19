from dotenv import load_dotenv
import os

OPEN_METEO_API_BASE_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_API_HOURLY_VARS = "uv_index,cloud_cover,temperature_2m,relative_humidity_2m"
OPEN_METEO_API_PAST_DAYS = 61 # 2 months
TIMEZONE = "UTC"

load_dotenv()

HOPSWORKS_API_KEY = os.getenv("HOPSWORKS_API_KEY")
HOPSWORKS_FEATURE_GROUP_NAME = os.getenv("HOPSWORKS_FEATURE_GROUP_NAME")
HOPSWORKS_FEATURE_VIEW_NAME = os.getenv("HOPSWORKS_FEATURE_VIEW_NAME")
HOPSWORKS_REALTIME_FEATURE_GROUP_NAME= os.getenv("HOPSWORKS_REALTIME_FEATURE_GROUP_NAME")
HOPSWORKS_MODEL_NAME=os.getenv("HOPSWORKS_MODEL_NAME")
HOPSWORKS_HOST = os.getenv("HOPSWORKS_HOST", "eu-west.cloud.hopsworks.ai")
HOPSWORKS_PORT = os.getenv("HOPSWORKS_PORT", "443")
HOPSWORKS_PROJECT = os.getenv("HOPSWORKS_PROJECT")

