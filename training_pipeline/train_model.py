from sklearn.metrics import accuracy_score, classification_report, recall_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

def prepare_training_data(df):
    df = df.dropna(subset=["uv_high_next"])
    df = df.sort_values("timestamp")

    X = df.drop(columns=["uv_high_next", "timestamp"])
    y = df["uv_high_next"]

    categorical_cols = ["city"]
    numeric_cols = [col for col in X.columns if col not in categorical_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ("num", "passthrough", numeric_cols)
        ]
    )

    return X, y, preprocessor


def split_sorted_data(X, y):
    split_index = int(len(X) * 0.8)

    return (
        X.iloc[:split_index],
        X.iloc[split_index:],
        y.iloc[:split_index],
        y.iloc[split_index:]
    )

def train_model(X_train, y_train, preprocessor):
    model = Pipeline([
        ("preprocessing", preprocessor),
        ("model", RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight="balanced"
        ))
    ])
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    probs = model.predict_proba(X_test)[:, 1]

    print("\n--- Threshold analysis ---")
    best_t = None
    best_recall = 0

    for t in [0.5, 0.4, 0.3, 0.2]:
        preds = (probs >= t).astype(int)
        recall = recall_score(y_test, preds)

        print(f"Threshold {t}: Recall = {recall:.3f}")

        if recall > best_recall:
            best_recall = recall
            best_t = t

    print(f"\nBest threshold (by recall): {best_t}")

    final_preds = (probs >= best_t).astype(int)

    acc = accuracy_score(y_test, final_preds)
    report = classification_report(y_test, final_preds)

    print("\n--- Final evaluation ---")
    print("Accuracy:", acc)
    print(report)
    print("Recall:", best_recall)

    return {
        "accuracy": acc,
        "recall": best_recall,
        "threshold": best_t
    }


def train(df):
    X, y, preprocessor = prepare_training_data(df)

    X_train, X_test, y_train, y_test = split_sorted_data(X, y)

    model = train_model(X_train, y_train, preprocessor)

    metrics = evaluate_model(model, X_test, y_test)

    return model, metrics