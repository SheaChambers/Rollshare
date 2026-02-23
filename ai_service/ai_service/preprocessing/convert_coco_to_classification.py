import json
import os
import shutil
from pathlib import Path
import re

# ======== CHANGE THESE PATHS ========
BASE_DIR = Path("C:\\Users\\sheac\\Documents\\Projects\\Rollshare\\ai-dataset\\raw")
SPLITS = ["train", "valid", "test"]
# ====================================

def clean_label(name):
    """
    Remove trailing digits from class name.
    Example: mount1 -> mount
    """
    return re.sub(r"\d+$", "", name)

for split in SPLITS:
    print(f"\nProcessing {split}...")

    split_dir = BASE_DIR / split
    json_path = split_dir / "_annotations.coco.json"

    with open(json_path) as f:
        coco = json.load(f)

    # Build category_id -> merged_name mapping
    category_map = {}
    for cat in coco["categories"]:
        merged_name = clean_label(cat["name"])
        category_map[cat["id"]] = merged_name

    # Build image_id -> file_name mapping
    image_map = {}
    for img in coco["images"]:
        image_map[img["id"]] = img["file_name"]

    # Create output directory
    output_dir = BASE_DIR / f"{split}_cls"
    output_dir.mkdir(exist_ok=True)

    # Move images
    for ann in coco["annotations"]:
        image_id = ann["image_id"]
        category_id = ann["category_id"]

        file_name = image_map[image_id]
        class_name = category_map[category_id]

        src = split_dir / file_name
        dst_dir = output_dir / class_name
        dst_dir.mkdir(parents=True, exist_ok=True)

        dst = dst_dir / file_name

        if not dst.exists():
            shutil.copy(src, dst)

    print(f"{split} complete.")
