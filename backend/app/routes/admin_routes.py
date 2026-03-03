from flask import Blueprint
from app.controllers.admin_controller import (
    get_admin_overview, get_top_techniques, ban_user_controller,
    unban_user_controller, feature_technique_controller,
    list_all_techniques, list_all_gyms
)
from app.decorators.auth_decorators import jwt_required, admin_required
from app.controllers.gyms_controller import (
    verify_gym, unverify_gym
)

admin_bp = Blueprint("admin_bp", __name__)


@admin_bp.route("/api/v1.0/admin/overview", methods=["GET"])
@jwt_required
@admin_required
def admin_overview_route(current_user, is_admin):
    return get_admin_overview()


@admin_bp.route("/api/v1.0/admin/top-techniques", methods=["GET"])
@jwt_required
@admin_required
def top_techniques_route(current_user, is_admin):
    return get_top_techniques()


@admin_bp.route("/api/v1.0/admin/users/<string:user_id>/ban", methods=["PUT"])
@jwt_required
@admin_required
def ban_user_route(user_id, current_user, is_admin):
    return ban_user_controller(user_id)


@admin_bp.route("/api/v1.0/admin/users/<string:user_id>/unban", methods=["PUT"])
@jwt_required
@admin_required
def unban_user_route(user_id, current_user, is_admin):
    return unban_user_controller(user_id)


@admin_bp.route("/api/v1.0/admin/techniques/<string:technique_id>/feature", methods=["PUT"])
@jwt_required
@admin_required
def feature_technique_route(technique_id, current_user, is_admin):
    return feature_technique_controller(technique_id)


@admin_bp.route("/api/v1.0/admin/techniques", methods=["GET"])
@jwt_required
@admin_required
def admin_techniques_route(current_user, is_admin):
    return list_all_techniques()

@admin_bp.route("/api/v1.0/admin/gyms", methods=["GET"])
@jwt_required
@admin_required
def admin_gyms_route(current_user, is_admin):
    return list_all_gyms()


@admin_bp.route("/api/v1.0/admin/gyms/<string:gym_id>/verify", methods=["PUT"])
@jwt_required
@admin_required
def verify_gym_route(gym_id, current_user, is_admin):
    return verify_gym(gym_id)


@admin_bp.route("/api/v1.0/admin/gyms/<string:gym_id>/unverify", methods=["PUT"])
@jwt_required
@admin_required
def unverify_gym_route(gym_id, current_user, is_admin):
    return unverify_gym(gym_id)