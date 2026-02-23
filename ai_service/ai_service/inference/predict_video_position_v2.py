import cv2
import numpy as np
from ultralytics import YOLO
import joblib
from pathlib import Path
from collections import Counter

def analyse_video(video_path):

    # ===== CONFIG =====
    MODEL_PATH = r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai_service\\ai_service\\models\\pose_random_forest_tuned.pkl"
    FEATURES_NPZ = r"C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai-service\\ai_service\\featues\\train_cls_features_v3.npz"
    SMOOTH_WINDOW = 5
    STATE_CONFIRM_FRAMES = 4
    # ===================

    pose_model = YOLO("yolov8n-pose.pt")
    clf = joblib.load(MODEL_PATH)

    # Load class names
    feature_data = np.load(FEATURES_NPZ, allow_pickle=True)
    class_names = list(feature_data["class_names"])


    # ---------- Feature Helpers ----------

    def angle(a, b, c):
        ba = a - b
        bc = c - b
        cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return np.arccos(cos_angle)


    def normalize_pose(kps):
        center = (kps[11] + kps[12]) / 2
        kps = kps - center
        torso_len = np.linalg.norm(kps[5]) + 1e-6
        kps = kps / torso_len
        return kps


    def extract_person_features(kps):
        kps = normalize_pose(kps)
        features = []

        features.append(angle(kps[5], kps[7], kps[9]))
        features.append(angle(kps[6], kps[8], kps[10]))
        features.append(angle(kps[11], kps[13], kps[15]))
        features.append(angle(kps[12], kps[14], kps[16]))
        features.append(angle(kps[5], kps[11], kps[13]))
        features.append(angle(kps[6], kps[12], kps[14]))

        torso_vec = kps[5] - kps[11]
        torso_angle = np.arctan2(torso_vec[1], torso_vec[0])
        features.append(torso_angle)

        features.extend(kps.flatten())
        return np.array(features)


    def extract_interaction_features(kps1, kps2):
        features = []

        hip1 = (kps1[11] + kps1[12]) / 2
        hip2 = (kps2[11] + kps2[12]) / 2
        features.append(np.linalg.norm(hip1 - hip2))

        sh1 = (kps1[5] + kps1[6]) / 2
        sh2 = (kps2[5] + kps2[6]) / 2
        features.append(np.linalg.norm(sh1 - sh2))

        c1 = np.mean(kps1, axis=0)
        c2 = np.mean(kps2, axis=0)
        features.append(np.linalg.norm(c1 - c2))

        torso1 = np.arctan2(kps1[5][1] - kps1[11][1], kps1[5][0] - kps1[11][0])
        torso2 = np.arctan2(kps2[5][1] - kps2[11][1], kps2[5][0] - kps2[11][0])
        features.append(abs(torso1 - torso2))

        return np.array(features)


    # ---------- Video Processing ----------

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frame_preds = []
    frame_probs = []

    print("Processing video...")

    previous_p1 = None
    previous_p2 = None
    previous_torso1 = None
    previous_torso2 = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = pose_model(frame, verbose=False, conf=0.15)

        if not results or results[0].keypoints is None:
            print("No keypoints detected")
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

        f1 = extract_person_features(p1)
        f2 = extract_person_features(p2)
        f_inter = extract_interaction_features(p1, p2)

        # ---- Motion Features ----
        motion_features = []

        if previous_p1 is not None and previous_p2 is not None:

            # Joint velocity (average per person)
            vel1 = np.mean(np.linalg.norm(p1 - previous_p1, axis=1))
            vel2 = np.mean(np.linalg.norm(p2 - previous_p2, axis=1))
            motion_features.append(vel1)
            motion_features.append(vel2)

            # Centroid velocity
            c1 = np.mean(p1, axis=0)
            c2 = np.mean(p2, axis=0)
            pc1 = np.mean(previous_p1, axis=0)
            pc2 = np.mean(previous_p2, axis=0)

            motion_features.append(np.linalg.norm(c1 - pc1))
            motion_features.append(np.linalg.norm(c2 - pc2))

            # Torso angle change
            torso1 = np.arctan2(p1[5][1] - p1[11][1], p1[5][0] - p1[11][0])
            torso2 = np.arctan2(p2[5][1] - p2[11][1], p2[5][0] - p2[11][0])

            motion_features.append(abs(torso1 - previous_torso1))
            motion_features.append(abs(torso2 - previous_torso2))

        else:
            # First frame fallback (no motion)
            motion_features.extend([0, 0, 0, 0, 0, 0])

        # Update previous states
        previous_p1 = p1.copy()
        previous_p2 = p2.copy()

        previous_torso1 = np.arctan2(p1[5][1] - p1[11][1], p1[5][0] - p1[11][0])
        previous_torso2 = np.arctan2(p2[5][1] - p2[11][1], p2[5][0] - p2[11][0])

        combined = np.concatenate([f1, f2, f_inter, motion_features]).reshape(1, -1)

        pred = clf.predict(combined)[0]
        prob = np.max(clf.predict_proba(combined))

        frame_preds.append(pred)
        frame_probs.append(prob)

    cap.release()

    if len(frame_preds) == 0:
        print("No usable frames (need 2 people detected).")
        raise SystemExit(1)

    # ---------- Short Smoothing ----------

    smoothed = []

    for i in range(len(frame_preds)):
        start = max(0, i - SMOOTH_WINDOW // 2)
        end = min(len(frame_preds), i + SMOOTH_WINDOW // 2 + 1)
        window = frame_preds[start:end]
        majority = Counter(window).most_common(1)[0][0]
        smoothed.append(majority)

    # ---------- State Transition Logic ----------

    final_states = []
    current_state = smoothed[0]
    counter = 0

    for i,pred in enumerate(smoothed):
        if pred == current_state:
            counter = 0
        else:
            counter += 1
            if counter >= STATE_CONFIRM_FRAMES:
                current_state = pred
                counter = 0
        final_states.append(current_state)
    
    # ----------- Print Logic ------------

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps is None or fps == 0:
        fps = 30.0

    segments = []
    last = final_states[0]
    start_frame = 0

    for i, state in enumerate(final_states):
        if state != last:
            segments.append({
                "position": class_names[last],
                "start_s": start_frame / fps,
                "end_s": i / fps
            })
            start_frame = i
            last = state

    segments.append({
        "position": class_names[last],
        "start_s": start_frame / fps,
        "end_s": len(final_states) / fps
    })

    return segments
