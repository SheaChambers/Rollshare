from flask import Blueprint, request
from app.controllers import reviews_controller as c
from app.decorators.auth_decorators import jwt_required

reviews_bp = Blueprint("reviews_bp", __name__)

@reviews_bp.route("/api/v1.0/techniques/<string:technique_id>/reviews", methods=["POST"])
@jwt_required
def add_review(technique_id, current_user, is_admin):
    return c.add_review(technique_id, current_user, request)

@reviews_bp.route("/api/v1.0/techniques/<string:technique_id>/reviews", methods=["GET"])
def list_reviews(technique_id):
    return c.list_reviews(technique_id)

@reviews_bp.route("/api/v1.0/techniques/<string:technique_id>/reviews/<string:review_id>", methods=["GET"])
def get_review(technique_id, review_id):
    return c.get_one_review(technique_id, review_id)

@reviews_bp.route("/api/v1.0/techniques/<string:technique_id>/reviews/<string:review_id>", methods=["PUT"])
@jwt_required
def edit_review(technique_id, review_id, current_user, is_admin):
    return c.edit_review(technique_id, review_id, current_user, is_admin, request)

@reviews_bp.route("/api/v1.0/techniques/<string:technique_id>/reviews/<string:review_id>", methods=["DELETE"])
@jwt_required
def delete_review(technique_id, review_id, current_user, is_admin):
    return c.delete_review(technique_id, review_id, current_user, is_admin)
