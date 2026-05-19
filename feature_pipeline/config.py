from dotenv import load_dotenv
import os

load_dotenv()

HOPSWORKS_FEATURE_GROUP_NAME = os.getenv("HOPSWORKS_FEATURE_GROUP_NAME")