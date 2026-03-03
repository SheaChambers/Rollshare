from flask import jsonify
from bson import ObjectId
from app.models.admin_model import (
    count_users, count_techniques, count_gyms, count_reviews,
    count_likes, count_saves, count_new_users_this_week, 
    top_techniques_by_likes, ban_user, unban_user, feature_technique
)


def get_admin_overview():

    return jsonify({
        "total_users": count_users(),
        "total_techniques": count_techniques(),
        "total_gyms": count_gyms(),
        "total_reviews": count_reviews(),
        "total_likes": count_likes(),
        "total_saves": count_saves(),
        "new_users_this_week": count_new_users_this_week()
    }), 200


def get_top_techniques():

    results = top_techniques_by_likes()

    for r in results:
        r["_id"] = str(r["_id"])

    return jsonify(results), 200


def ban_user_controller(user_id: str):

    if not ObjectId.is_valid(user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    result = ban_user(ObjectId(user_id))

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User banned successfully"}), 200


def unban_user_controller(user_id: str):

    if not ObjectId.is_valid(user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    result = unban_user(ObjectId(user_id))

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User unbanned successfully"}), 200


def feature_technique_controller(technique_id: str):

    if not ObjectId.is_valid(technique_id):
        return jsonify({"error": "Invalid technique ID"}), 400

    result = feature_technique(ObjectId(technique_id))

    if result.matched_count == 0:
        return jsonify({"error": "Technique not found"}), 404

    return jsonify({"message": "Technique marked as featured"}), 200