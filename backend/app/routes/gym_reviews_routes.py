from flask import Blueprint, request
from app.controllers import gym_reviews_controller as c
from app.decorators.auth_decorators import jwt_required

gym_reviews_bp = Blueprint("gym_reviews_bp", __name__)

@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews", methods=["POST"])
@jwt_required
def add_review(gym_id, current_user, is_admin):
    return c.add(gym_id, current_user, request)

@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews", methods=["GET"])
def list_reviews(gym_id):
    return c.list_all(gym_id)

@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews/<string:review_id>", methods=["GET"])
def get_review(gym_id, review_id):
    return c.get_one(gym_id, review_id)

@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews/<string:review_id>", methods=["PUT"])
@jwt_required
def edit_review(gym_id, review_id, current_user, is_admin):
    return c.edit(gym_id, review_id, current_user, is_admin, request)

@gym_reviews_bp.route("/api/v1.0/gyms/<string:gym_id>/reviews/<string:review_id>", methods=["DELETE"])
@jwt_required
def delete_review(gym_id, review_id, current_user, is_admin):
    return c.remove(gym_id, review_id, current_user, is_admin)
