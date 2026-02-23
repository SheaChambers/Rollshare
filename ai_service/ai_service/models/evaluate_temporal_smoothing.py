import numpy as np
from pathlib import Path
import joblib
from collections import Counter
from sklearn.metrics import classification_report, accuracy_score

# ===== CONFIG =====
FEATURE_DIR = Path(r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai_service\\ai_service\\features")
MODEL_PATH = Path(r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai_service\\ai_service\\models\\pose_random_forest_tuned.pkl")
WINDOW_SIZE = 15
# ===================

# Load data
data = np.load(FEATURE_DIR / "test_cls_features_v2.npz", allow_pickle=True)
X_test, y_test = data["X"], data["y"]
class_names = list(data["class_names"])

clf = joblib.load(MODEL_PATH)

# Frame-level predictions
frame_preds = clf.predict(X_test)

# ---- Temporal Smoothing ----
smoothed_preds = []

for i in range(len(frame_preds)):
    start = max(0, i - WINDOW_SIZE // 2)
    end = min(len(frame_preds), i + WINDOW_SIZE // 2 + 1)

    window = frame_preds[start:end]
    majority_class = Counter(window).most_common(1)[0][0]
    smoothed_preds.append(majority_class)

smoothed_preds = np.array(smoothed_preds)

# Evaluate
print("\n=== Frame-Level Performance ===")
print(f"Accuracy: {accuracy_score(y_test, frame_preds) * 100:.2f}%")
print(classification_report(y_test, frame_preds, target_names=class_names))

print("\n=== Temporal Smoothed Performance ===")
print(f"Accuracy: {accuracy_score(y_test, smoothed_preds) * 100:.2f}%")
print(classification_report(y_test, smoothed_preds, target_names=class_names))
