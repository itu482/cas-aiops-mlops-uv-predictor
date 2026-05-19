import pandas as pd

from common import get_feature_store, save_to_feature_store, prep_features_inference

from config import HOPSWORKS_REALTIME_FEATURE_GROUP_NAME

def save_realtime_features(raw: dict, prediction: int, project):
    try:
        df = pd.DataFrame([raw])

        df = prep_features_inference(df)

        df["uv_high_next_pred"] = prediction
        
        # no broken numbers
        df = df.fillna(0)
        
        save_to_feature_store(
            data=df, 
            fs=get_feature_store(project), 
            fg_name=HOPSWORKS_REALTIME_FEATURE_GROUP_NAME, 
            description="Real-time UV features + predictions", 
            pk=["timestamp","city"], 
            event_time="timestamp", 
            wait_for_job = False,
            online_enabled = False
        )
    except Exception as e:
        # Ignore "Commit failed: a concurrent transactions added new data." - saving first instance is good enough for now
        print("Non-critical logging failure:", e)

    return True
