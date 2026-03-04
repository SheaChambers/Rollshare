import datetime
import uuid
from bson import ObjectId
from flask import jsonify
import threading

from app.services.blob_storage_service import BlobStorageService
from app.models.techniques_model import (
    insert_technique, count, find_many, find_one_by_id, update_by_id, delete_by_id,
    add_like_to_technique, remove_like_from_technique, get_featured
)
from app.controllers.video_analyser_controller import analyse_video_task

ALLOWED_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]
ALLOWED_CATEGORIES = ["Guard", "Pass", "Sweep", "Takedown", "Submission",
                      "Escape", "Transition", "Drill", "Pin", "Roll"]

def create(request, current_user: str):
    required_fields = ["name", "category", "difficulty", "description"]
    for f in required_fields:
        if f not in request.form or not request.form[f].strip():
            return jsonify({"error": f"Missing required field: {f}"}), 400

    if "video" not in request.files:
        return jsonify({"error": "Technique video is required"}), 400

    video = request.files["video"]
    if not (video.content_type or "").startswith("video/"):
        return jsonify({"error": "Invalid video file"}), 400

    difficulty = request.form["difficulty"].strip().capitalize()
    if difficulty not in ALLOWED_DIFFICULTIES:
        return jsonify({"error": f"Invalid difficulty. Must be one of: {ALLOWED_DIFFICULTIES}"}), 400
    
    category = request.form["category"].strip()
    if category not in ALLOWED_CATEGORIES:
        return jsonify({"error": f"Invalid category. Must be one of: {ALLOWED_CATEGORIES}"}), 400

    storage = BlobStorageService()
    blob_name = f"techniques/{uuid.uuid4()}.mp4"
    storage.upload_file(video.stream, blob_name, video.content_type)

    thumbnail_blob = storage.generate_video_thumbnail(blob_name)

    doc = {
        "name": request.form["name"].strip(),
        "category": category,
        "difficulty": difficulty,
        "description": request.form["description"].strip(),
        "video_blob_url": blob_name,
        "thumbnail_blob_url": thumbnail_blob,
        "created_by": current_user,
        "created_at": datetime.datetime.now(datetime.UTC),
        "featured": False,
        "analysis_status": "not_requested",
        "analysis": None,
        "likes": [],
        "reviews": []
    }

    res = insert_technique(doc)

    video_url = storage.generate_read_url(blob_name)
    thumb_url = storage.generate_read_url(thumbnail_blob)

    return jsonify({"message": "Technique created successfully", 
                    "id": str(res.inserted_id), 
                    "video_blob_url": video_url,
                    "thumbnail_blob_url": thumb_url}), 201


def list_all(request):
    # Pagination
    try:
        page_num = int(request.args.get("pn", 1))
        page_size = int(request.args.get("ps", 10))
        if page_num < 1 or page_size < 1 or page_size > 100:
            return jsonify({"error": "Invalid pagination values"}), 400
    except ValueError:
        return jsonify({"error": "Invalid pagination format"}), 400

    filters = {}
    if "category" in request.args:
        filters["category"] = {"$in": request.args.getlist("category")}
    if "difficulty" in request.args:
        filters["difficulty"] = {"$in": request.args.getlist("difficulty")}
    if "created_by" in request.args:
        filters["created_by"] = {"$in": request.args.getlist("created_by")}

    if request.args.get("q"):
        term = request.args.get("q", "")
        filters["$or"] = [
            {"name": {"$regex": term, "$options": "i"}},
            {"category": {"$regex": term, "$options": "i"}},
            {"description": {"$regex": term, "$options": "i"}},
        ]

    sort_field = request.args.get("sort_by", "name")
    sort_order = request.args.get("order", "asc").lower()
    sort_direction = 1 if sort_order == "asc" else -1

    total = count(filters)
    total_pages = (total + page_size - 1) // page_size
    skip = (page_num - 1) * page_size

    cursor = find_many(filters, sort_field, sort_direction, skip, page_size)

    storage = BlobStorageService()

    items = []
    for t in cursor:
        t["_id"] = str(t["_id"])
        if t.get("video_blob_url"):
            t["video_blob_url"] = storage.generate_read_url(t["video_blob_url"])
        if t.get("thumbnail_blob_url"):
            t["thumbnail_blob_url"] = storage.generate_read_url(t["thumbnail_blob_url"])

        for r in t.get("reviews", []):
            if "_id" in r:
                r["_id"] = str(r["_id"])
        items.append(t)

    return jsonify({
        "pagination": {
            "page": page_num,
            "page_size": page_size,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page_num < total_pages,
            "has_previous": page_num > 1,
        },
        "filters_applied": filters,
        "sort": {"by": sort_field, "order": sort_order},
        "techniques": items
    }), 200


def get_one(technique_id: str):
    storage = BlobStorageService()

    if not ObjectId.is_valid(technique_id):
        return jsonify({"error": "Invalid technique ID"}), 400

    t = find_one_by_id(technique_id)
    if not t:
        return jsonify({"error": "Technique not found"}), 404

    if "video_blob_url" in t:
        t["video_blob_url"] = storage.generate_read_url(t["video_blob_url"])
    
    if t.get("thumbnail_blob_url"):
        t["thumbnail_blob_url"] = storage.generate_read_url(t["thumbnail_blob_url"])

    t["_id"] = str(t["_id"])
    for r in t.get("reviews", []):
        if "_id" in r:
            r["_id"] = str(r["_id"])
    return jsonify(t), 200


def update(technique_id: str, current_user: str, is_admin: bool, request):
    if not ObjectId.is_valid(technique_id):
        return jsonify({"error": "Invalid technique ID"}), 400

    t = find_one_by_id(technique_id)
    if not t:
        return jsonify({"error": "Technique not found"}), 404

    if not is_admin and t.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    allowed = ["name", "category", "difficulty", "description"]
    fields = {}
    for f in allowed:
        if f in request.form:
            v = request.form[f].strip()
            if not v:
                return jsonify({"error": f"{f} cannot be empty"}), 400
            fields[f] = v

    if "difficulty" in fields:
        d = fields["difficulty"].capitalize()
        if d not in ALLOWED_DIFFICULTIES:
            return jsonify({"error": "Invalid difficulty"}), 400
        fields["difficulty"] = d

    if not fields:
        return jsonify({"error": "No fields provided for update"}), 400

    res = update_by_id(technique_id, fields)
    if res.modified_count == 0:
        return jsonify({"error": "No changes made"}), 400

    return jsonify({"message": "Technique updated"}), 200


def toggle_like(technique_id: str, current_user: str):
    if not ObjectId.is_valid(technique_id):
        return jsonify({"error": "Invalid technique ID"}), 400
    
    t = find_one_by_id(technique_id)
    if not t:
        return jsonify({"error": "Technique not found"}), 404
    
    if current_user in t.get("likes", []):
        remove_like_from_technique(technique_id, current_user)
        return jsonify({"liked": False}), 200
    else:
        add_like_to_technique(technique_id, current_user)
        return jsonify({"liked": True}), 200


def remove(technique_id: str, current_user: str, is_admin: bool):
    if not ObjectId.is_valid(technique_id):
        return jsonify({"error": "Invalid technique ID"}), 400

    t = find_one_by_id(technique_id)
    if not t:
        return jsonify({"error": "Technique not found"}), 404

    if not is_admin and t.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403
    
    storage = BlobStorageService()
    if t.get("video_blob_url"):
        storage.delete_blob(t["video_blob_url"])
    if t.get("thumbnail_blob_url"):
        storage.delete_blob(t["thumbnail_blob_url"])

    res = delete_by_id(technique_id)
    if res.deleted_count == 0:
        return jsonify({"error": "Deletion failed"}), 500
    return jsonify({}), 204


def get_featured_technique():
    tech = get_featured()

    if not tech:
        return jsonify({"error": "No featured technique"}), 404

    tech["_id"] = str(tech["_id"])

    storage = BlobStorageService()

    if tech.get("thumbnail_blob_url"):
        tech["thumbnail_blob_url"] = storage.generate_read_url(
            tech["thumbnail_blob_url"]
        )

    if tech.get("video_blob_url"):
        tech["video_blob_url"] = storage.generate_read_url(
            tech["video_blob_url"]
        )

    if "reviews" in tech:
        for r in tech["reviews"]:
            if "_id" in r:
                r["_id"] = str(r["_id"])

    return jsonify(tech), 200
