import datetime
from bson import ObjectId
from flask import jsonify

from app.models.gyms_model import (
    find_one_by_id, push_review, get_reviews_only, find_review_projection,
    update_review, pull_review
)
from app.models.user_model import users_col
from app.services.blob_storage_service import BlobStorageService

def add(gym_id: str, current_user: str, request):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    if "rating" not in request.form or "comment" not in request.form:
        return jsonify({"error": "Rating and comment required"}), 400

    try:
        rating = int(request.form["rating"])
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

    comment = request.form["comment"].strip()
    if len(comment) < 3:
        return jsonify({"error": "Comment must be at least 3 characters long"}), 400

    g = find_one_by_id(gym_id)
    if not g:
        return jsonify({"error": "Gym not found"}), 404

    for r in g.get("reviews", []):
        if r.get("user") == current_user:
            return jsonify({"error": "You have already reviewed this gym"}), 400

    review = {
        "_id": ObjectId(),
        "user": current_user,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.datetime.now(datetime.UTC),
    }

    push_review(gym_id, review)
    return jsonify({"message": "Review added"}), 201


def list_all(gym_id: str):
    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    doc = get_reviews_only(gym_id)
    if not doc:
        return jsonify({"error": "Gym not found"}), 404

    reviews = doc.get("reviews", [])

    storage = BlobStorageService()

    for r in reviews:
        r["_id"] = str(r["_id"])

        user_doc = users_col().find_one({"username": r["user"]}, {"avatar_url": 1})

        if user_doc and user_doc.get("avatar_url"):
            r["avatar_url"] = storage.generate_read_url(user_doc["avatar_url"])
        else:
            r["avatar_url"] = None

    return jsonify(reviews), 200


def get_one(gym_id: str, review_id: str):
    if not ObjectId.is_valid(gym_id) or not ObjectId.is_valid(review_id):
        return jsonify({"error": "Invalid ID"}), 400

    doc = find_review_projection(gym_id, review_id)
    if not doc or "reviews" not in doc or len(doc["reviews"]) == 0:
        return jsonify({"error": "Review not found"}), 404

    r = doc["reviews"][0]
    r["_id"] = str(r["_id"])
    return jsonify(r), 200


def edit(gym_id: str, review_id: str, current_user: str, is_admin: bool, request):
    if not ObjectId.is_valid(gym_id) or not ObjectId.is_valid(review_id):
        return jsonify({"error": "Invalid ID"}), 400

    doc = find_review_projection(gym_id, review_id)
    if not doc or "reviews" not in doc or len(doc["reviews"]) == 0:
        return jsonify({"error": "Review not found"}), 404

    matching_reviews = [r for r in doc["reviews"] if str(r["_id"]) == review_id]
    if not matching_reviews:
        return jsonify({"error": "Review not found in list"}), 404
        
    review = matching_reviews[0]
    if not is_admin and review.get("user") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    fields = {}
    if "rating" in request.form:
        try:
            rating = int(request.form["rating"])
            if rating < 1 or rating > 5:
                raise ValueError
            fields["reviews.$.rating"] = rating
        except ValueError:
            return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

    if "comment" in request.form:
        comment = request.form["comment"].strip()
        if len(comment) < 3:
            return jsonify({"error": "Comment must be at least 3 characters long"}), 400
        fields["reviews.$.comment"] = comment

    if not fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    fields["reviews.$.updated_at"] = datetime.datetime.now(datetime.UTC)

    res = update_review(gym_id, review_id, fields)
    if res.modified_count == 0:
        return jsonify({"error": "No changes made"}), 400

    return jsonify({"message": "Review updated"}), 200


def remove(gym_id: str, review_id: str, current_user: str, is_admin: bool):
    if not ObjectId.is_valid(gym_id) or not ObjectId.is_valid(review_id):
        return jsonify({"error": "Invalid ID"}), 400

    doc = find_review_projection(gym_id, review_id)
    if not doc or "reviews" not in doc or len(doc["reviews"]) == 0:
        return jsonify({"error": "Review not found"}), 404

    review = doc["reviews"][0]
    if not is_admin and review.get("user") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    pull_review(gym_id, review_id)
    return jsonify({}), 204
