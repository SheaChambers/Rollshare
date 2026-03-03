from flask import Blueprint
from app.controllers.admin_controller import (
    get_admin_overview, get_top_techniques, ban_user_controller,
    unban_user_controller, feature_technique_controller
)
from app.decorators.auth_decorators import jwt_required, admin_required

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