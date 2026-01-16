from flask import Blueprint, request, jsonify, make_response
from bson import ObjectId
import datetime
import re
import uuid

from app.db import get_db
from app.decorators.auth_decorators import jwt_required, admin_required
from app.services.blob_storage_service import BlobStorageService

techniques_bp = Blueprint("techniques_bp", __name__)

def get_techniques_collection():
    return get_db().techniques


@techniques_bp.route("/api/v1.0/techniques", methods=["POST"])
@jwt_required
def create_technique(current_user, is_admin):
    techniques = get_techniques_collection()

    # --- Validate form fields ---
    required_fields = ["name", "category", "difficulty", "description"]
    for field in required_fields:
        if field not in request.form or not request.form[field].strip():
            return make_response(
                jsonify({"error": f"Missing required field: {field}"}), 400
            )

    if "video" not in request.files:
        return make_response(
            jsonify({"error": "Technique video is required"}), 400
        )

    video = request.files["video"]
    if not video.content_type.startswith("video/"):
        return make_response(jsonify({"error": "Invalid video file"}), 400)

    # --- Upload to Azure Blob Storage ---

    storage = BlobStorageService()
    filename = f"techniques/{uuid.uuid4()}.mp4"

    video_url = storage.upload_file(
        video.stream,
        filename,
        video.content_type
    )

    # --- Create technique document ---
    technique = {
        "name": request.form["name"].strip(),
        "category": request.form["category"].strip(),
        "difficulty": request.form["difficulty"].strip().capitalize(),
        "description": request.form["description"].strip(),
        "video_blob_url": video_url,
        "created_by": current_user,
        "created_at": datetime.datetime.now(datetime.UTC),
        "reviews": []
    }

    result = techniques.insert_one(technique)

    return jsonify({
        "message": "Technique created successfully",
        "id": str(result.inserted_id),
        "video_blob_url": video_url
    }), 201



@techniques_bp.route("/api/v1.0/techniques", methods=["GET"])
def get_all_techniques():
    techniques = get_techniques_collection()

    try:
        # Get pagination params from URL query
        page_num = int(request.args.get("pn", 1))
        page_size = int(request.args.get("ps", 10))

        # Validate values
        if page_num < 1 or page_size < 1 or page_size > 100:
            return make_response(jsonify({  
                    "error": "Invalid pagination values. 'pn' and 'ps' must be positive integers, and 'ps' <= 100"
                }), 400)
    
    except ValueError:
        return make_response(jsonify({
            "error": "Invalid pagination format. 'pn' and 'ps' must be integers"
        }), 400)
    
    # Filtering
    filters = {}

    # Category Filtering
    if "category" in request.args:
        filters["category"] = {"$in": request.args.getlist("category")}
    # Difficulty Filtering
    if "difficulty" in request.args:
        filters["difficulty"] = {"$in": request.args.getlist("difficulty")}
    # Created_by Filter
    if "created_by" in request.args:
        filters["created_by"] = {"$in": request.args.getlist("created_by")}
    # Rating Filtering
    if "rating" in request.args:
        filters["rating"] = {"$in": request.args.get("rating")}
    # Rating range Filtering
    min_rating = request.args.get("min_rating")
    max_rating = request.args.get("max_rating")
    if min_rating or max_rating:
        rating_filter = {}
        if min_rating:
            rating_filter["$gte"] = float(min_rating)
        if max_rating:
            rating_filter["$lte"] = float(max_rating)
        filters["average_Rating"] = rating_filter

    # Search
    if request.args.get("q"):
        search_terms = request.args.get("q", "").split()
        for term in search_terms:
            filters["$and"] = [
                {"$or": [
                    {"name": {"$regex": term, "$options": "i"}},
                    {"category": {"$regex": term, "$options": "i"}},
                    {"description": {"$regex": term, "$options": "i"}}
                ]}
            ]

    # Sorting
    sort_field = request.args.get("sort_by", "name")
    sort_order = request.args.get("order", "asc").lower()

    sort_direction = 1 if sort_order == "asc" else -1
    
    # Calculate total techniques and number of pages
    total_techniques = techniques.count_documents(filters)
    total_pages = (total_techniques + page_size - 1) // page_size

    # Pagination offset
    page_start = (page_num - 1) * page_size
    
    # Fetch results with filtering, sorting, and pagination
    cursor = techniques.find(filters).sort(sort_field, sort_direction).skip(page_start).limit(page_size)

    data_to_return = []
    for technique in cursor:
        technique['_id'] = str(technique['_id'])
        for review in technique['reviews']:
            review['_id'] = str(review['_id'])
        data_to_return.append(technique)
    return make_response( jsonify({
        "pagination": {
            "page": page_num,
            "page_size": page_size,
            "total_items": total_techniques,
            "total_pages": total_pages,
            "has_next": page_num < total_pages,
            "has_previous": page_num > 1
        },
        "filters_applied": filters,
        "sort": {"by": sort_field, "order": sort_order},
        "techniques": data_to_return
    }), 200 )




@techniques_bp.route("/api/v1.0/techniques/<string:id>", methods=["GET"])
def get_one_technique(id):
    techniques = get_techniques_collection()

    if not ObjectId.is_valid(id):
        return jsonify({"error": "Invalid ID"}), 400

    technique = techniques.find_one({"_id": ObjectId(id)})

    if not technique:
        return jsonify({"error": "Not found"}), 404

    technique["_id"] = str(technique["_id"])

    if "reviews" in technique:
        for r in technique["reviews"]:
            r["_id"] = str(r["_id"])

    return jsonify(technique), 200



@techniques_bp.route("/api/v1.0/techniques/<string:id>", methods=["PUT"])
@jwt_required
def edit_technique(id, current_user, is_admin):
    techniques = get_techniques_collection()

    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid technique ID"}), 400)

    technique = techniques.find_one({"_id": ObjectId(id)})
    if not technique:
        return make_response(jsonify({"error": "Technique not found"}), 404)

    # Only admin or creator can edit
    if not is_admin and technique.get("created_by") != current_user:
        return make_response(jsonify({"error": "Not authorised"}), 403)

    update_fields = {}
    allowed_fields = ["name", "category", "difficulty", "description"]

    for field in allowed_fields:
        if field in request.form:
            value = request.form[field].strip()
            if not value:
                return make_response(
                    jsonify({"error": f"{field} cannot be empty"}), 400
                )
            update_fields[field] = value

    if not update_fields:
        return make_response(jsonify({"error": "No fields provided for update"}), 400)

    if "difficulty" in update_fields:
        if update_fields["difficulty"] not in ["Beginner", "Intermediate", "Advanced"]:
            return make_response(jsonify({"error": "Invalid difficulty"}), 400)

    result = techniques.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_fields}
    )

    if result.modified_count == 0:
        return make_response(jsonify({"error": "No changes made"}), 400)

    return make_response(jsonify({"message": "Technique updated"}), 200)


@techniques_bp.route("/api/v1.0/techniques/<string:id>", methods=["DELETE"])
@jwt_required
def delete_technique(id, current_user, is_admin):
    techniques = get_techniques_collection()

    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid technique ID"}), 400)

    technique = techniques.find_one({"_id": ObjectId(id)})
    if not technique:
        return make_response(jsonify({"error": "Technique not found"}), 404)

    # Only admin or creator can delete
    if not is_admin and technique.get("created_by") != current_user:
        return make_response(jsonify({"error": "Not authorised"}), 403)

    result = techniques.delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        return make_response(jsonify({"error": "Deletion failed"}), 500)

    return make_response(jsonify({}), 204)
