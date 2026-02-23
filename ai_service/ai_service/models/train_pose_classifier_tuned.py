import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import RandomizedSearchCV
import joblib

# ===== CONFIG =====
FEATURE_DIR = Path(r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai_service\\ai_service\\features")
MODEL_DIR = Path(r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai_service\\ai_service\\models")
# ===================

# Load data
train_data = np.load(FEATURE_DIR / "train_cls_features_v3.npz", allow_pickle=True)
valid_data = np.load(FEATURE_DIR / "valid_cls_features_v3.npz", allow_pickle=True)
test_data  = np.load(FEATURE_DIR / "test_cls_features_v3.npz", allow_pickle=True)

X_train, y_train = train_data["X"], train_data["y"]
X_valid, y_valid = valid_data["X"], valid_data["y"]
X_test,  y_test  = test_data["X"], test_data["y"]
class_names = train_data["class_names"]

print("Train shape:", X_train.shape)
print("Valid shape:", X_valid.shape)
print("Test shape:", X_test.shape)

# ---------------------------------------------------
# Hyperparameter Search Space
# ---------------------------------------------------

param_dist = {
    "n_estimators": [300, 500, 800],
    "max_depth": [None, 10, 20, 30],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2"],
    "class_weight": [None, "balanced"]
}

base_model = RandomForestClassifier(
    random_state=42,
    n_jobs=-1
)

search = RandomizedSearchCV(
    estimator=base_model,
    param_distributions=param_dist,
    n_iter=15,
    cv=3,
    verbose=2,
    n_jobs=-1
)

print("\nTuning RandomForest...")
search.fit(X_train, y_train)

best_model = search.best_estimator_

print("\nBest Parameters Found:")
print(search.best_params_)

# ---------------------------------------------------
# Evaluate on Validation
# ---------------------------------------------------

val_preds = best_model.predict(X_valid)
val_acc = accuracy_score(y_valid, val_preds)

print(f"\nValidation Accuracy: {val_acc * 100:.2f}%")

# ---------------------------------------------------
# Evaluate on Test
# ---------------------------------------------------

test_preds = best_model.predict(X_test)
test_acc = accuracy_score(y_test, test_preds)

print(f"Test Accuracy: {test_acc * 100:.2f}%")

print("\nClassification Report (Test):")
print(classification_report(y_test, test_preds, target_names=class_names))

# ---------------------------------------------------
# Save tuned model
# ---------------------------------------------------

MODEL_DIR.mkdir(exist_ok=True)
joblib.dump(best_model, MODEL_DIR / "pose_random_forest_tuned.pkl")

print("\nTuned Pose classifier saved.")
