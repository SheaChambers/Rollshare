from flask import Blueprint, request
from app.controllers.user_controller import (
    register, get_all_users, get_user_by_id, get_me,
    update_user_profile, reset_password, remove_user,
    save_technique, get_saved_techniques_controller, unsave_technique,
    get_user_rolls, get_settings, update_settings
)
from app.decorators.auth_decorators import jwt_required, admin_required

users_bp = Blueprint("users_bp", __name__)

@users_bp.route("/api/v1.0/users/register", methods=["POST"])
def register_route():
    return register(request)

@users_bp.route("/api/v1.0/users", methods=["GET"])
@jwt_required
@admin_required
def all_users_route(current_user, is_admin):
    return get_all_users()

@users_bp.route("/api/v1.0/users/<string:user_id>", methods=["GET"])
@jwt_required
def get_user_route(user_id, current_user, is_admin):
    return get_user_by_id(user_id, current_user, is_admin)

@users_bp.route("/api/v1.0/users/me", methods=["GET"])
@jwt_required
def me_route(current_user, is_admin):
    return get_me(current_user)

@users_bp.route("/api/v1.0/users/<string:user_id>", methods=["PUT"])
@jwt_required
def update_user_route(user_id, current_user, is_admin):
    return update_user_profile(user_id, current_user, is_admin, request)

@users_bp.route("/api/v1.0/users/reset-password", methods=["PUT"])
@jwt_required
def reset_pw_route(current_user, is_admin):
    return reset_password(current_user, request)

@users_bp.route("/api/v1.0/users/<string:user_id>", methods=["DELETE"])
@jwt_required
def delete_user_route(user_id, current_user, is_admin):
    return remove_user(user_id, current_user, is_admin)

@users_bp.route("/api/v1.0/users/me/saved-techniques", methods=["POST"])
@jwt_required
def saved_tech_route(current_user, is_admin):
    return save_technique(current_user, request)

@users_bp.route("/api/v1.0/users/me/saved-techniques", methods=["GET"])
@jwt_required
def get_saved_techs_route(current_user, is_admin):
    return get_saved_techniques_controller(current_user)

@users_bp.route("/api/v1.0/users/me/saved-techniques/<string:technique_id>", methods=["DELETE"])
@jwt_required
def unsave_tech_route(technique_id, current_user, is_admin):
    return unsave_technique(current_user, technique_id)

@users_bp.route("/api/v1.0/users/me/rolls", methods=["GET"])
@jwt_required
def get_my_rolls(current_user, is_admin):
    return get_user_rolls(current_user)

@users_bp.route("/api/v1.0/users/me/settings", methods=["GET"])
@jwt_required
def get_settings_route(current_user, is_admin):
    return get_settings(current_user)

@users_bp.route("/api/v1.0/users/me/settings", methods=["PUT"])
@jwt_required
def update_settings_route(current_user, is_admin):
    return update_settings(current_user, request)