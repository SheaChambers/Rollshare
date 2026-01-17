from flask import Blueprint, request, jsonify, make_response
from bson import ObjectId
import datetime
import uuid

from app.db import get_db
from app.decorators.auth_decorators import jwt_required, admin_required
from app.services.blob_storage_service import BlobStorageService

gyms_bp = Blueprint("gyms_bp", __name__)

ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/gif"}


def get_gyms_collection():
    return get_db().gyms


def _serialize_gym(gym: dict) -> dict:
    gym["_id"] = str(gym["_id"])
    for r in gym.get("reviews", []):
        if "_id" in r:
            r["_id"] = str(r["_id"])
    return gym


@gyms_bp.route("/api/v1.0/gyms", methods=["POST"])
@jwt_required
def create_gym(current_user, is_admin):
    gyms = get_gyms_collection()

    required_fields = ["name", "latitude", "longitude", "phone", "email"]
    for field in required_fields:
        if field not in request.form or not request.form[field].strip():
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate lat/long
    try:
        latitude = float(request.form["latitude"].strip())
        longitude = float(request.form["longitude"].strip())
    except ValueError:
        return jsonify({"error": "Latitude and longitude must be valid numbers"}), 400

    raw_coaches = request.form.get("coaches", "").strip()
    coaches = [c.strip() for c in raw_coaches.split(",") if c.strip()] if raw_coaches else []

    new_gym = {
        "name": request.form["name"].strip(),
        "geo_location": {
            "type": "Point",
            "coordinates": [longitude, latitude],
        },
        "contact": {
            "phone": request.form["phone"].strip(),
            "email": request.form["email"].strip(),
            "website": request.form.get("website", "").strip(),
        },
        "coaches": coaches,
        "media_url": {
            "instagram": request.form.get("instagram", "").strip(),
            "facebook": request.form.get("facebook", "").strip(),
        },
        "verified": False,
        "photos": [],
        "reviews": [],
        "created_by": current_user,
        "created_at": datetime.datetime.now(datetime.UTC),
    }

    result = gyms.insert_one(new_gym)
    return jsonify({"message": "Gym created", "id": str(result.inserted_id)}), 201


@gyms_bp.route("/api/v1.0/gyms", methods=["GET"])
def get_all_gyms():
    gyms = get_gyms_collection()

    # Pagination
    try:
        page_num = int(request.args.get("pn", 1))
        page_size = int(request.args.get("ps", 10))
        if page_num < 1 or page_size < 1 or page_size > 100:
            return jsonify({"error": "Invalid pagination values"}), 400
    except ValueError:
        return jsonify({"error": "Invalid pagination format"}), 400

    filters = {}

    # Filtering
    if request.args.get("verified") is not None:
        filters["verified"] = request.args.get("verified").lower() == "true"

    if request.args.get("created_by"):
        filters["created_by"] = request.args.get("created_by")

    # Search
    if request.args.get("q"):
        q = request.args.get("q").strip()
        filters["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"contact.email": {"$regex": q, "$options": "i"}},
            {"contact.phone": {"$regex": q, "$options": "i"}},
            {"coaches": {"$regex": q, "$options": "i"}},
        ]

    # Sorting
    sort_field = request.args.get("sort_by", "name")
    sort_order = request.args.get("order", "asc").lower()
    sort_direction = 1 if sort_order == "asc" else -1

    total_gyms = gyms.count_documents(filters)
    total_pages = (total_gyms + page_size - 1) // page_size
    page_start = (page_num - 1) * page_size

    cursor = gyms.find(filters).sort(sort_field, sort_direction).skip(page_start).limit(page_size)

    data = []
    for g in cursor:
        data.append(_serialize_gym(g))

    return jsonify({
        "pagination": {
            "page": page_num,
            "page_size": page_size,
            "total_items": total_gyms,
            "total_pages": total_pages,
            "has_next": page_num < total_pages,
            "has_previous": page_num > 1,
        },
        "filters_applied": filters,
        "sort": {"by": sort_field, "order": sort_order},
        "gyms": data,
    }), 200


@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>", methods=["GET"])
def get_one_gym(gym_id):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    gym = gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        return jsonify({"error": "Gym not found"}), 404

    return jsonify(_serialize_gym(gym)), 200


@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>", methods=["PUT"])
@jwt_required
def update_gym(gym_id, current_user, is_admin):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    gym = gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and gym.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    update_fields = {}

    # Simple text updates
    for field in ["name"]:
        if field in request.form:
            val = request.form[field].strip()
            if not val:
                return jsonify({"error": f"{field} cannot be empty"}), 400
            update_fields[field] = val

    # Contact
    if "phone" in request.form:
        update_fields["contact.phone"] = request.form["phone"].strip()
    if "email" in request.form:
        update_fields["contact.email"] = request.form["email"].strip()
    if "website" in request.form:
        update_fields["contact.website"] = request.form["website"].strip()

    # Media URLs
    if "instagram" in request.form:
        update_fields["media_url.instagram"] = request.form["instagram"].strip()
    if "facebook" in request.form:
        update_fields["media_url.facebook"] = request.form["facebook"].strip()

    # Coaches
    if "coaches" in request.form:
        raw = request.form.get("coaches", "").strip()
        update_fields["coaches"] = [c.strip() for c in raw.split(",") if c.strip()]

    # Optional lat/long update
    if "latitude" in request.form or "longitude" in request.form:
        try:
            lat = float(request.form.get("latitude", gym["geo_location"]["coordinates"][1]))
            lon = float(request.form.get("longitude", gym["geo_location"]["coordinates"][0]))
        except ValueError:
            return jsonify({"error": "Latitude/longitude must be numbers"}), 400

        update_fields["geo_location.coordinates"] = [lon, lat]

    if not update_fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    result = gyms.update_one({"_id": ObjectId(gym_id)}, {"$set": update_fields})
    if result.modified_count == 0:
        return jsonify({"error": "No changes made"}), 400

    return jsonify({"message": "Gym updated"}), 200


@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>", methods=["DELETE"])
@jwt_required
def delete_gym(gym_id, current_user, is_admin):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    gym = gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and gym.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    result = gyms.delete_one({"_id": ObjectId(gym_id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Deletion failed"}), 500

    return jsonify({}), 204


@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>/verify", methods=["PATCH"])
@jwt_required
@admin_required
def verify_gym(gym_id, current_user, is_admin):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    result = gyms.update_one({"_id": ObjectId(gym_id)}, {"$set": {"verified": True}})
    if result.matched_count == 0:
        return jsonify({"error": "Gym not found"}), 404

    return jsonify({"message": "Gym verified"}), 200


@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>/photos", methods=["POST"])
@jwt_required
def upload_gym_photos(gym_id, current_user, is_admin):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    gym = gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and gym.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    files = request.files.getlist("photos")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    storage = BlobStorageService()
    uploaded_urls = []

    for f in files:
        if not f or not f.filename:
            continue

        if not f.mimetype or f.mimetype.lower() not in ALLOWED_IMAGE_MIMES:
            return jsonify({"error": f"File type not allowed: {f.filename}"}), 400

        # Keep original extension where possible
        ext = (f.filename.rsplit(".", 1)[1].lower() if "." in f.filename else "jpg")
        blob_name = f"gyms/{gym_id}/{uuid.uuid4()}.{ext}"

        url = storage.upload_file(f.stream, blob_name, f.mimetype)
        uploaded_urls.append(url)

    if not uploaded_urls:
        return jsonify({"error": "No valid files uploaded"}), 400

    gyms.update_one(
        {"_id": ObjectId(gym_id)},
        {"$push": {"photos": {"$each": uploaded_urls}}}
    )

    return jsonify({"message": "Photos uploaded", "photos": uploaded_urls}), 200


@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>/photos", methods=["DELETE"])
@jwt_required
def delete_gym_photo(gym_id, current_user, is_admin):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    gym = gyms.find_one({"_id": ObjectId(gym_id)})
    if not gym:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and gym.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    data = request.get_json(silent=True) or {}
    photo_url = data.get("photo_url")

    if not photo_url:
        return jsonify({"error": "photo_url is required"}), 400

    gyms.update_one(
        {"_id": ObjectId(gym_id)},
        {"$pull": {"photos": photo_url}}
    )

    # Note: We are not deleting the blob from storage here (optional to implement later)
    return jsonify({"message": "Photo removed from gym"}), 200
