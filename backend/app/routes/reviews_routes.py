from flask import Blueprint, request, jsonify, make_response
from bson import ObjectId
import datetime

from app.db import get_db
from app.decorators.auth_decorators import jwt_required, admin_required

reviews_bp = Blueprint("reviews_bp", __name__)


def get_techniques_collection():
    return get_db().techniques


@reviews_bp.route("/api/v1.0/techniques/<string:t_id>/reviews", methods=["POST"])
@jwt_required
def add_review(t_id, current_user, is_admin):
    techniques = get_techniques_collection()

    if not ObjectId.is_valid(t_id):
        return jsonify({"error": "Invalid technique ID"}), 400

    if "rating" not in request.form or "comment" not in request.form:
        return jsonify({"error": "Rating and comment required"}), 400

    try:
        rating = int(request.form["rating"])
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        return jsonify({"error": "Rating must be an integer between 1 and 5"}), 400

    # Prevent duplicate reviews
    if techniques.find_one({
        "_id": ObjectId(t_id),
        "reviews.user": current_user
    }):
        return jsonify({"error": "You have already reviewed this technique"}), 400

    review = {
        "_id": ObjectId(),
        "user": current_user,
        "rating": rating,
        "comment": request.form["comment"].strip(),
        "created_at": datetime.datetime.now(datetime.UTC)
    }

    result = techniques.update_one(
        {"_id": ObjectId(t_id)},
        {"$push": {"reviews": review}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Technique not found"}), 404

    return jsonify({"message": "Review added"}), 201


@reviews_bp.route("/api/v1.0/techniques/<string:t_id>/reviews", methods=["GET"])
def get_reviews(t_id):
    techniques = get_techniques_collection()

    if not ObjectId.is_valid(t_id):
        return jsonify({"error": "Invalid technique ID"}), 400

    technique = techniques.find_one(
        {"_id": ObjectId(t_id)},
        {"reviews": 1, "_id": 0}
    )

    if not technique:
        return jsonify({"error": "Technique not found"}), 404

    reviews = technique.get("reviews", [])
    for r in reviews:
        r["_id"] = str(r["_id"])

    return jsonify(reviews), 200


@reviews_bp.route("/api/v1.0/techniques/<string:t_id>/reviews/<string:r_id>", methods=["PUT"])
@jwt_required
def edit_review(t_id, r_id, current_user, is_admin):
    techniques = get_techniques_collection()

    # Validate IDs
    if not ObjectId.is_valid(t_id):
        return jsonify({"error": "Invalid technique ID"}), 400
    if not ObjectId.is_valid(r_id):
        return jsonify({"error": "Invalid review ID"}), 400

    # Find the review (projection returns only the matched review)
    doc = techniques.find_one(
        {"_id": ObjectId(t_id), "reviews._id": ObjectId(r_id)},
        {"reviews.$": 1}
    )

    if not doc or "reviews" not in doc or len(doc["reviews"]) == 0:
        return jsonify({"error": "Review not found"}), 404

    review = doc["reviews"][0]

    # Only admin or review author can edit
    if not is_admin and review.get("user") != current_user:
        return jsonify({"error": "Not authorised"}), 403

    # Build update fields
    update_fields = {}

    if "rating" in request.form:
        try:
            rating = int(request.form["rating"])
            if rating < 1 or rating > 5:
                return jsonify({"error": "Rating must be between 1 and 5"}), 400
            update_fields["reviews.$.rating"] = rating
        except ValueError:
            return jsonify({"error": "Rating must be an integer"}), 400

    if "comment" in request.form:
        comment = request.form["comment"].strip()
        if len(comment) < 3:
            return jsonify({"error": "Comment must be at least 3 characters long"}), 400
        update_fields["reviews.$.comment"] = comment

    if not update_fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    # Optional: track edits
    update_fields["reviews.$.updated_at"] = datetime.datetime.now(datetime.UTC)

    result = techniques.update_one(
        {"_id": ObjectId(t_id), "reviews._id": ObjectId(r_id)},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Technique or review not found"}), 404

    return jsonify({"message": "Review updated"}), 200



@reviews_bp.route("/api/v1.0/techniques/<string:t_id>/reviews/<string:r_id>", methods=["DELETE"])
@jwt_required
def delete_review(t_id, r_id, current_user, is_admin):
    techniques = get_techniques_collection()

    if not ObjectId.is_valid(t_id) or not ObjectId.is_valid(r_id):
        return jsonify({"error": "Invalid ID"}), 400

    technique = techniques.find_one(
        {"_id": ObjectId(t_id), "reviews._id": ObjectId(r_id)},
        {"reviews.$": 1}
    )

    if not technique:
        return jsonify({"error": "Review not found"}), 404

    review = technique["reviews"][0]

    if not is_admin and review["user"] != current_user:
        return jsonify({"error": "Not authorised"}), 403

    techniques.update_one(
        {"_id": ObjectId(t_id)},
        {"$pull": {"reviews": {"_id": ObjectId(r_id)}}}
    )

    return jsonify({}), 204
