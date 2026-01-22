from flask import Blueprint, request
from app.controllers import gyms_controller as c
from app.decorators.auth_decorators import jwt_required, admin_required

gyms_bp = Blueprint("gyms_bp", __name__)

@gyms_bp.route("/api/v1.0/gyms", methods=["POST"])
@jwt_required
def create_gym(current_user, is_admin):
    return c.create(request, current_user)

@gyms_bp.route("/api/v1.0/gyms", methods=["GET"])
def list_gyms():
    return c.list_all(request)

@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>", methods=["GET"])
def get_gym(gym_id):
    return c.get_one(gym_id)

@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>", methods=["PUT"])
@jwt_required
def update_gym(gym_id, current_user, is_admin):
    return c.update(gym_id, current_user, is_admin, request)

@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>", methods=["DELETE"])
@jwt_required
def delete_gym(gym_id, current_user, is_admin):
    return c.remove(gym_id, current_user, is_admin)

@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>/verify", methods=["PATCH"])
@jwt_required
@admin_required
def verify_gym(gym_id, current_user, is_admin):
    return c.verify(gym_id)

@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>/photos", methods=["POST"])
@jwt_required
def upload_photos(gym_id, current_user, is_admin):
    return c.upload_photos(gym_id, current_user, is_admin, request)

@gyms_bp.route("/api/v1.0/gyms/<string:gym_id>/photos", methods=["DELETE"])
@jwt_required
def delete_photo(gym_id, current_user, is_admin):
    return c.delete_photo(gym_id, current_user, is_admin, request)
