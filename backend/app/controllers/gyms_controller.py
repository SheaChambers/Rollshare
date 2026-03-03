import datetime
import uuid
from bson import ObjectId
from flask import jsonify

from app.models.gyms_model import (
    insert_gym, count, find_many, find_one_by_id, update_by_id, delete_by_id,
    push_photos, pull_photo
)
from app.services.blob_storage_service import BlobStorageService

ALLOWED_IMAGE_MIMES = {"image/png", "image/jpeg", "image/jpg", "image/gif"}

def create(request, current_user: str):
    required = ["name", "latitude", "longitude", "phone", "email"]
    for f in required:
        if f not in request.form or not request.form[f].strip():
            return jsonify({"error": f"Missing required field: {f}"}), 400

    try:
        lat = float(request.form["latitude"].strip())
        lon = float(request.form["longitude"].strip())
    except ValueError:
        return jsonify({"error": "Latitude and longitude must be valid numbers"}), 400

    raw_coaches = request.form.get("coaches", "").strip()
    coaches = [c.strip() for c in raw_coaches.split(",") if c.strip()] if raw_coaches else []

    doc = {
        "name": request.form["name"].strip(),
        "address": request.form["address"].strip(),
        "geo_location": {"type": "Point", "coordinates": [lon, lat]},
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

    res = insert_gym(doc)
    return jsonify({"message": "Gym created", "id": str(res.inserted_id)}), 201


def list_all(request):
    try:
        pn = int(request.args.get("pn", 1))
        ps = int(request.args.get("ps", 10))
        if pn < 1 or ps < 1 or ps > 100:
            return jsonify({"error": "Invalid pagination values"}), 400
    except ValueError:
        return jsonify({"error": "Invalid pagination format"}), 400

    filters = {}
    if request.args.get("verified") is not None:
        filters["verified"] = request.args.get("verified").lower() == "true"
    if request.args.get("created_by"):
        filters["created_by"] = request.args.get("created_by")

    if request.args.get("q"):
        q = request.args.get("q").strip()
        filters["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"contact.email": {"$regex": q, "$options": "i"}},
            {"contact.phone": {"$regex": q, "$options": "i"}},
            {"coaches": {"$regex": q, "$options": "i"}},
        ]

    sort_field = "_id"
    sort_order = 1

    total = count(filters)
    total_pages = (total + ps - 1) // ps
    skip = (pn - 1) * ps

    cursor = find_many(filters, sort_field, sort_order, skip, ps)
    storage = BlobStorageService()

    gyms = []
    for g in cursor:
        g["_id"] = str(g["_id"])

        if g.get("photos"):
            g["photos"][0] = storage.generate_read_url(g["photos"][0])

        for r in g.get("reviews", []):
            if "_id" in r:
                r["_id"] = str(r["_id"])
        gyms.append(g)

    return jsonify({
        "pagination": {
            "page": pn,
            "page_size": ps,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": pn < total_pages,
            "has_previous": pn > 1,
        },
        "filters_applied": filters,
        "gyms": gyms
    }), 200


def get_one(gym_id: str):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    g = find_one_by_id(gym_id)
    if not g:
        return jsonify({"error": "Gym not found"}), 404
    
    storage = BlobStorageService()

    if "photos" in g and isinstance(g["photos"], list):
        signed_photos = []
        for photo_path in g["photos"]:
            signed_photos.append(storage.generate_read_url(photo_path))
        g["photos"] = signed_photos

    g["_id"] = str(g["_id"])
    for r in g.get("reviews", []):
        if "_id" in r:
            r["_id"] = str(r["_id"])
    return jsonify(g), 200


def update(gym_id: str, current_user: str, is_admin: bool, request):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    g = find_one_by_id(gym_id)
    if not g:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and g.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    fields = {}

    if "name" in request.form:
        v = request.form["name"].strip()
        if not v:
            return jsonify({"error": "name cannot be empty"}), 400
        fields["name"] = v

    if "address" in request.form:
        fields["address"] = request.form["address"].strip()

    if "phone" in request.form:
        fields["contact.phone"] = request.form["phone"].strip()
    if "email" in request.form:
        fields["contact.email"] = request.form["email"].strip()
    if "website" in request.form:
        fields["contact.website"] = request.form["website"].strip()

    if "instagram" in request.form:
        fields["media_url.instagram"] = request.form["instagram"].strip()
    if "facebook" in request.form:
        fields["media_url.facebook"] = request.form["facebook"].strip()

    if "coaches" in request.form:
        raw = request.form.get("coaches", "").strip()
        fields["coaches"] = [c.strip() for c in raw.split(",") if c.strip()]

    if "latitude" in request.form or "longitude" in request.form:
        try:
            lat = float(request.form.get("latitude", g["geo_location"]["coordinates"][1]))
            lon = float(request.form.get("longitude", g["geo_location"]["coordinates"][0]))
        except ValueError:
            return jsonify({"error": "Latitude/longitude must be numbers"}), 400
        fields["geo_location.coordinates"] = [lon, lat]

    if not fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    res = update_by_id(gym_id, fields)
    if res.modified_count == 0:
        return jsonify({"error": "No changes made"}), 400

    return jsonify({"message": "Gym updated"}), 200


def remove(gym_id: str, current_user: str, is_admin: bool):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    g = find_one_by_id(gym_id)
    if not g:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and g.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    res = delete_by_id(gym_id)
    if res.deleted_count == 0:
        return jsonify({"error": "Deletion failed"}), 500

    return jsonify({}), 204


def verify_gym(gym_id: str):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    res = update_by_id(gym_id, {"verified": True})
    if res.matched_count == 0:
        return jsonify({"error": "Gym not found"}), 404

    return jsonify({"message": "Gym verified"}), 200


def unverify_gym(gym_id: str):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    res = update_by_id(gym_id, {"verified": False})
    if res.matched_count == 0:
        return jsonify({"error": "Gym not found"}), 404

    return jsonify({"message": "Gym unverified"}), 200


def upload_photos(gym_id: str, current_user: str, is_admin: bool, request):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    g = find_one_by_id(gym_id)
    if not g:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and g.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    files = request.files.getlist("photos")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    storage = BlobStorageService()
    urls = []
    signed_urls = []

    for f in files:
        if not f or not f.filename:
            continue
        if (f.mimetype or "").lower() not in ALLOWED_IMAGE_MIMES:
            return jsonify({"error": f"File type not allowed: {f.filename}"}), 400

        ext = f.filename.rsplit(".", 1)[1].lower() if "." in f.filename else "jpg"
        blob_name = f"gyms/{gym_id}/{uuid.uuid4()}.{ext}"
        storage.upload_file(f.stream, blob_name, f.mimetype)
        urls.append(blob_name)

        signed_urls.append(storage.generate_read_url(blob_name))

    if not urls:
        return jsonify({"error": "No valid files uploaded"}), 400

    push_photos(gym_id, urls)
    return jsonify({
        "message": "Photos uploaded", 
        "photos": signed_urls
    }), 200


def delete_photo(gym_id: str, current_user: str, is_admin: bool, request):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    g = find_one_by_id(gym_id)
    if not g:
        return jsonify({"error": "Gym not found"}), 404

    if not is_admin and g.get("created_by") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    data = request.get_json(silent=True) or {}
    photo = data.get("photo")
    if not photo:
        return jsonify({"error": "photo is required"}), 400

    pull_photo(gym_id, photo)

    storage = BlobStorageService()
    storage.delete_blob(photo)

    return jsonify({"message": "Photo removed from gym"}), 200
