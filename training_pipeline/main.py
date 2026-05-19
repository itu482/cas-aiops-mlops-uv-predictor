from common import get_project
from load_training_data import load_data_from_feature_store, wait_for_data
from train_model import train
from save_model import save_model_to_hopsworks

def main():
    hopsworks_project = get_project()

    print("Loading data from Feature Store...")
    wait_for_data(hopsworks_project)
    df = load_data_from_feature_store(hopsworks_project)
    
    print("Training model...")
    model, metrics = train(df)
    
    print("Saving model to Hopsworks...")
    save_model_to_hopsworks(model, metrics, hopsworks_project)

    print("Training pipeline finished successfully")

if __name__ == "__main__":
    main()