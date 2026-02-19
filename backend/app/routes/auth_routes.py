from flask import Blueprint, request
from app.controllers.auth_controller import login, verify_2fa_login, logout
from app.decorators.auth_decorators import jwt_required

auth_bp = Blueprint("auth_bp", __name__)

@auth_bp.route("/api/v1.0/login", methods=["POST"])
def login_route():
    return login(request)

@auth_bp.route("/api/v1.0/auth/2fa-login", methods=["POST"])
def verify_2fa_login_route():
    return verify_2fa_login(request)

@auth_bp.route("/api/v1.0/logout", methods=["POST"])
@jwt_required
def logout_route(current_user, is_admin):
    token = request.headers.get("x-access-token")
    return logout(token)
