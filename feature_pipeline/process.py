from common import prep_features_ingest, get_feature_store,get_project,save_to_feature_store
from config import HOPSWORKS_FEATURE_GROUP_NAME

def prep_features(df):
    df = prep_features_ingest(df)
    return df

def save_features(data):
    project = get_project()
    
    fs = get_feature_store(project);
    
    save_to_feature_store(
        data=data,
        fs=fs,
        fg_name=HOPSWORKS_FEATURE_GROUP_NAME, 
        description="UV risk prediction dataset",
        pk=["timestamp","city"],
        event_time="timestamp"
    )