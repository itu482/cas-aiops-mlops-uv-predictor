import hopsworks
from common.config import HOPSWORKS_API_KEY, HOPSWORKS_HOST, HOPSWORKS_PORT, HOPSWORKS_PROJECT

def get_project():
    project = hopsworks.login(
        project=HOPSWORKS_PROJECT,
        host=HOPSWORKS_HOST,
        port=HOPSWORKS_PORT,
        api_key_value=HOPSWORKS_API_KEY
    )
    return project

def get_feature_store(project):
    return project.get_feature_store()

def get_or_create_feature_group(fs, name, description, pk, event_time, online_enabled = True):
    fg = fs.get_or_create_feature_group(
        name=name,
        version=1,
        primary_key=pk,
        event_time=event_time,
        description=description,
        online_enabled=online_enabled,
    )
    return fg

def save_to_feature_store(data, fs, fg_name, description, pk, event_time, wait_for_job = True, online_enabled = True):
    fg = get_or_create_feature_group(fs, fg_name, description, pk, event_time, online_enabled);
    fg.insert(data, write_options={"wait_for_job": wait_for_job})
