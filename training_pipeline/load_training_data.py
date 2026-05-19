from common import get_feature_store
from config import HOPSWORKS_FEATURE_GROUP_NAME, HOPSWORKS_FEATURE_VIEW_NAME
import time

def wait_for_data(project):
    while True:
        data = load_data_from_feature_store(project)
        if len(data) > 10:
            break
        print("Waiting for initial data...")
        time.sleep(10)

def load_data_from_feature_store(project):
    fs = get_feature_store(project)

    fg = fs.get_feature_group(
        name=HOPSWORKS_FEATURE_GROUP_NAME,
        version=1
    )

    query = fg.select([
        "city",
        "cloud_cover",
        "cloud_mean_3h",
        "cloud_trend",
        "doy_cos",
        "doy_sin",
        "hour_cos",
        "hour_sin",
        "humidity_norm",
        "is_hot_region",
        "is_northern",
        "lat",
        "lon",
        "relative_humidity_2m",
        "temp_norm",
        "temperature_2m",
        "timestamp",
        "uv_high_next"
    ])

    fv = fs.get_or_create_feature_view(
        name=HOPSWORKS_FEATURE_VIEW_NAME,
        version=1,
        query=query
    )

    df = fv.get_batch_data()
    return df
