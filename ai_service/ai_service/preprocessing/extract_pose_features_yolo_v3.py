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


# ------------------ GEOMETRY HELPERS ------------------

def angle(a, b, c):
    """Angle at point b given three points"""
    ba = a - b
    bc = c - b
    cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return np.arccos(cos_angle)


def normalize_pose(kps):
    left_hip = kps[11]
    right_hip = kps[12]
    center = (left_hip + right_hip) / 2.0
    kps = kps - center

    torso_len = np.linalg.norm(kps[5]) + 1e-6
    kps = kps / torso_len
    return kps


def extract_person_features(kps):
    kps = normalize_pose(kps)

    features = []

    # Joint angles
    features.append(angle(kps[5], kps[7], kps[9]))   # left elbow
    features.append(angle(kps[6], kps[8], kps[10]))  # right elbow
    features.append(angle(kps[11], kps[13], kps[15]))  # left knee
    features.append(angle(kps[12], kps[14], kps[16]))  # right knee
    features.append(angle(kps[5], kps[11], kps[13]))  # left hip
    features.append(angle(kps[6], kps[12], kps[14]))  # right hip

    # Torso orientation
    torso_vec = kps[5] - kps[11]
    torso_angle = np.arctan2(torso_vec[1], torso_vec[0])
    features.append(torso_angle)

    # Flatten normalized pose
    features.extend(kps.flatten())

    return np.array(features)


def extract_interaction_features(kps1, kps2):
    features = []

    # Hip distance
    hip1 = (kps1[11] + kps1[12]) / 2
    hip2 = (kps2[11] + kps2[12]) / 2
    features.append(np.linalg.norm(hip1 - hip2))

    # Shoulder distance
    sh1 = (kps1[5] + kps1[6]) / 2
    sh2 = (kps2[5] + kps2[6]) / 2
    features.append(np.linalg.norm(sh1 - sh2))

    # Centroid distance
    c1 = np.mean(kps1, axis=0)
    c2 = np.mean(kps2, axis=0)
    features.append(np.linalg.norm(c1 - c2))

    # Torso angle difference
    torso1 = np.arctan2(kps1[5][1] - kps1[11][1], kps1[5][0] - kps1[11][0])
    torso2 = np.arctan2(kps2[5][1] - kps2[11][1], kps2[5][0] - kps2[11][0])
    features.append(abs(torso1 - torso2))

    return np.array(features)


# ------------------ MAIN PROCESS ------------------

def process_split(split):
    print(f"\nProcessing {split}...")

    features = []
    labels = []

    class_names = sorted(os.listdir(DATA_DIR / split))
    class_to_idx = {cls: i for i, cls in enumerate(class_names)}

    for cls in class_names:
        cls_path = DATA_DIR / split / cls
        img_list = sorted(os.listdir(cls_path))

        previous_p1 = None
        previous_p2 = None
        previous_torso1 = None
        previous_torso2 = None

        for img_name in tqdm(img_list):
            img_path = cls_path / img_name
            results = model(str(img_path), verbose=False)

            if not results or results[0].keypoints is None:
                continue

            r = results[0]
            kps = r.keypoints.xy.cpu().numpy()

            if len(kps) < 2:
                continue

            boxes = r.boxes.xyxy.cpu().numpy()
            areas = (boxes[:,2] - boxes[:,0]) * (boxes[:,3] - boxes[:,1])
            idx = np.argsort(-areas)

            p1 = kps[idx[0]]
            p2 = kps[idx[1]]

            # Base pose features
            f1 = extract_person_features(p1)
            f2 = extract_person_features(p2)
            f_inter = extract_interaction_features(p1, p2)

            # ---- Motion Features ----
            motion_features = []

            if previous_p1 is not None:

                vel1 = np.mean(np.linalg.norm(p1 - previous_p1, axis=1))
                vel2 = np.mean(np.linalg.norm(p2 - previous_p2, axis=1))
                motion_features.append(vel1)
                motion_features.append(vel2)

                c1 = np.mean(p1, axis=0)
                c2 = np.mean(p2, axis=0)
                pc1 = np.mean(previous_p1, axis=0)
                pc2 = np.mean(previous_p2, axis=0)

                motion_features.append(np.linalg.norm(c1 - pc1))
                motion_features.append(np.linalg.norm(c2 - pc2))

                torso1 = np.arctan2(p1[5][1] - p1[11][1], p1[5][0] - p1[11][0])
                torso2 = np.arctan2(p2[5][1] - p2[11][1], p2[5][0] - p2[11][0])

                motion_features.append(abs(torso1 - previous_torso1))
                motion_features.append(abs(torso2 - previous_torso2))

            else:
                motion_features.extend([0, 0, 0, 0, 0, 0])

            previous_p1 = p1.copy()
            previous_p2 = p2.copy()

            previous_torso1 = np.arctan2(p1[5][1] - p1[11][1], p1[5][0] - p1[11][0])
            previous_torso2 = np.arctan2(p2[5][1] - p2[11][1], p2[5][0] - p2[11][0])

            combined = np.concatenate([f1, f2, f_inter, motion_features])

            features.append(combined)
            labels.append(class_to_idx[cls])

    features = np.array(features)
    labels = np.array(labels)

    OUTPUT_DIR.mkdir(exist_ok=True)
    np.savez(
        OUTPUT_DIR / f"{split}_features_v3.npz",
        X=features,
        y=labels,
        class_names=class_names
    )

    print(f"{split} saved: {features.shape}")


if __name__ == "__main__":
    for split in SPLITS:
        process_split(split)
