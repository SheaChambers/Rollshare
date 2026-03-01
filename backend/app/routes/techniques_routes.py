from flask import Blueprint, request
from app.controllers import techniques_controller as c
from app.decorators.auth_decorators import jwt_required

techniques_bp = Blueprint("techniques_bp", __name__)

@techniques_bp.route("/api/v1.0/techniques", methods=["POST"])
@jwt_required
def create_technique(current_user, is_admin):
    return c.create(request, current_user)

@techniques_bp.route("/api/v1.0/techniques", methods=["GET"])
def list_techniques():
    return c.list_all(request)

@techniques_bp.route("/api/v1.0/techniques/<string:technique_id>", methods=["GET"])
def get_technique(technique_id):
    return c.get_one(technique_id)

@techniques_bp.route("/api/v1.0/techniques/<string:technique_id>", methods=["PUT"])
@jwt_required
def update_technique(technique_id, current_user, is_admin):
    return c.update(technique_id, current_user, is_admin, request)

@techniques_bp.route("/api/v1.0/techniques/<string:technique_id>/like", methods=["POST"])
@jwt_required
def like_technique(technique_id, current_user, is_admin):
    return c.toggle_like(technique_id, current_user)

@techniques_bp.route("/api/v1.0/techniques/<string:technique_id>", methods=["DELETE"])
@jwt_required
def delete_technique(technique_id, current_user, is_admin):
    return c.remove(technique_id, current_user, is_admin)
