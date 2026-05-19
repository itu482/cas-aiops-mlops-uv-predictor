from ingest import fetch_uv_data_all_cities
from process import prep_features, save_features
import time

def run_feature_pipeline():
    print("Fetching meteo data for all cities...")
    df = fetch_uv_data_all_cities()

    print("Preparing features...")
    df = prep_features(df)

    print("Saving features and labels to feature store")
    return save_features(df)

def run_worker():
    while True:
        print("Running ingestion job...")
        try:
            run_feature_pipeline()
            print("ingestion done")
        except Exception as e:
            print("ingestion failed:", e)

        print("sleeping 10 minutes...\n")
        time.sleep(600)

def main():
    run_worker()

if __name__ == "__main__":
    main()