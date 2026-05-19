import joblib
from config import HOPSWORKS_MODEL_NAME

def save_model_to_hopsworks(model, metrics, project):
    model_path = f"{HOPSWORKS_MODEL_NAME}.pkl"
    joblib.dump(model, model_path)

    print(f"Model saved locally at {model_path}")

    mr = project.get_model_registry()

    model_meta = mr.python.create_model(
        name=HOPSWORKS_MODEL_NAME,
        metrics=metrics,
        description=(
            "UV risk prediction model using weather + temporal + location features. "
            "Includes threshold tuning for safety-first predictions."
        )
    )

    model_meta.save(model_path)

    print("Model successfully uploaded to Hopsworks Model Registry")

    return model_meta