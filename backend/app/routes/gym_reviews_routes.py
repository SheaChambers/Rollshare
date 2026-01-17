from flask import Blueprint, request, jsonify
from bson import ObjectId
import datetime

from app.db import get_db
from app.decorators.auth_decorators import jwt_required

gym_reviews_bp = Blueprint("gym_reviews_bp", __name__)


def get_gyms_collection():
    return get_db().gyms


def _serialize_review(review: dict) -> dict:
    if "_id" in review:
        review["_id"] = str(review["_id"])
    return review


@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews", methods=["POST"])
@jwt_required
def add_gym_review(gym_id, current_user, is_admin):
    gyms = get_gyms_collection()

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

    # Prevent duplicate review by same user
    if gyms.find_one({"_id": ObjectId(gym_id), "reviews.user": current_user}):
        return jsonify({"error": "You have already reviewed this gym"}), 400

    review = {
        "_id": ObjectId(),
        "user": current_user,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.datetime.now(datetime.UTC),
    }

    result = gyms.update_one(
        {"_id": ObjectId(gym_id)},
        {"$push": {"reviews": review}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Gym not found"}), 404

    return jsonify({"message": "Review added"}), 201


@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews", methods=["GET"])
def get_all_gym_reviews(gym_id):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id):
        return jsonify({"error": "Invalid gym ID"}), 400

    gym = gyms.find_one({"_id": ObjectId(gym_id)}, {"reviews": 1, "_id": 0})
    if not gym:
        return jsonify({"error": "Gym not found"}), 404

    reviews = gym.get("reviews", [])
    for r in reviews:
        _serialize_review(r)

    return jsonify(reviews), 200


@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews/<string:review_id>", methods=["GET"])
def get_one_gym_review(gym_id, review_id):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id) or not ObjectId.is_valid(review_id):
        return jsonify({"error": "Invalid ID"}), 400

    doc = gyms.find_one(
        {"_id": ObjectId(gym_id), "reviews._id": ObjectId(review_id)},
        {"reviews.$": 1}
    )

    if not doc or "reviews" not in doc or len(doc["reviews"]) == 0:
        return jsonify({"error": "Review not found"}), 404

    review = doc["reviews"][0]
    _serialize_review(review)
    return jsonify(review), 200


@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews/<string:review_id>", methods=["PUT"])
@jwt_required
def edit_gym_review(gym_id, review_id, current_user, is_admin):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id) or not ObjectId.is_valid(review_id):
        return jsonify({"error": "Invalid ID"}), 400

    doc = gyms.find_one(
        {"_id": ObjectId(gym_id), "reviews._id": ObjectId(review_id)},
        {"reviews.$": 1}
    )

    if not doc or "reviews" not in doc or len(doc["reviews"]) == 0:
        return jsonify({"error": "Review not found"}), 404

    review = doc["reviews"][0]

    # Only admin or review author can edit
    if not is_admin and review.get("user") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    update_fields = {}

    if "rating" in request.form:
        try:
            rating = int(request.form["rating"])
            if rating < 1 or rating > 5:
                raise ValueError
            update_fields["reviews.$.rating"] = rating
        except ValueError:
            return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

    if "comment" in request.form:
        comment = request.form["comment"].strip()
        if len(comment) < 3:
            return jsonify({"error": "Comment must be at least 3 characters long"}), 400
        update_fields["reviews.$.comment"] = comment

    if not update_fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    update_fields["reviews.$.updated_at"] = datetime.datetime.now(datetime.UTC)

    result = gyms.update_one(
        {"_id": ObjectId(gym_id), "reviews._id": ObjectId(review_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Gym or review not found"}), 404

    return jsonify({"message": "Review updated"}), 200


@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews/<string:review_id>", methods=["DELETE"])
@jwt_required
def delete_gym_review(gym_id, review_id, current_user, is_admin):
    gyms = get_gyms_collection()

    if not ObjectId.is_valid(gym_id) or not ObjectId.is_valid(review_id):
        return jsonify({"error": "Invalid ID"}), 400

    doc = gyms.find_one(
        {"_id": ObjectId(gym_id), "reviews._id": ObjectId(review_id)},
        {"reviews.$": 1}
    )

    if not doc or "reviews" not in doc or len(doc["reviews"]) == 0:
        return jsonify({"error": "Review not found"}), 404

    review = doc["reviews"][0]

    # Only admin or review author can delete
    if not is_admin and review.get("user") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    gyms.update_one(
        {"_id": ObjectId(gym_id)},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}}
    )

    return jsonify({}), 204
