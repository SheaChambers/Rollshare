import os
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from tqdm import tqdm

# ===== CONFIG =====
DATA_DIR = Path(r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai-dataset")
OUTPUT_DIR = Path(r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai_service\\ai_service\\features")
SPLITS = ["train_cls", "valid_cls", "test_cls"]
MODEL_NAME = "yolov8n-pose.pt"
# ===================


model = YOLO(MODEL_NAME)


def normalize_keypoints(kps):
    """
    kps: (17,2)
    Normalize relative to hip center and torso length
    """
    xy = kps.copy()

    # hip indices in COCO: 11 (left), 12 (right)
    left_hip = xy[11]
    right_hip = xy[12]

    center = (left_hip + right_hip) / 2.0
    xy = xy - center

    # shoulder index 5
    left_shoulder = xy[5]
    scale = np.linalg.norm(left_shoulder)

    if scale > 1e-6:
        xy = xy / scale

    return xy.flatten()


def process_split(split):
    print(f"\nProcessing {split}...")

    features = []
    labels = []

    class_names = sorted(os.listdir(DATA_DIR / split))
    class_to_idx = {cls: i for i, cls in enumerate(class_names)}

    for cls in class_names:
        cls_path = DATA_DIR / split / cls

        for img_name in tqdm(os.listdir(cls_path)):
            img_path = cls_path / img_name

            results = model(str(img_path), verbose=False)

            if len(results) == 0:
                continue

            r = results[0]

            if r.keypoints is None:
                continue

            kps = r.keypoints.xy.cpu().numpy()

            if len(kps) < 2:
                continue

            # sort by bounding box area (largest first)
            boxes = r.boxes.xyxy.cpu().numpy()
            areas = (boxes[:,2] - boxes[:,0]) * (boxes[:,3] - boxes[:,1])
            sorted_idx = np.argsort(-areas)

            person1 = normalize_keypoints(kps[sorted_idx[0]])
            person2 = normalize_keypoints(kps[sorted_idx[1]])

            combined = np.concatenate([person1, person2])

            features.append(combined)
            labels.append(class_to_idx[cls])

    features = np.array(features)
    labels = np.array(labels)

    OUTPUT_DIR.mkdir(exist_ok=True)

    np.savez(
        OUTPUT_DIR / f"{split}_features.npz",
        X=features,
        y=labels,
        class_names=class_names
    )

    print(f"{split} saved: {features.shape}")


if __name__ == "__main__":
    for split in SPLITS:
        process_split(split)
