import datetime
import jwt
import bcrypt
from flask import jsonify
from app.models.user_model import find_by_username, update_user, add_blacklist_token, push_login_history
import os
import pyotp

def login(request):
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = find_by_username(username)
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"error": "Invalid username or password"}), 400

    security = user.get("settings", {}).get("security", {})

    if security.get("two_factor_enabled"):
        return jsonify({
            "required_2fa": True,
            "username": user["username"]
        }), 200

    return _issue_jwt(user)


def verify_2fa_login(request):
    username = (request.json or {}).get("username")
    code = (request.json or {}).get("code")

    if not username or not code:
        return jsonify({"error": "username and code are required"}), 400
    
    user = find_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    security = user.get("settings", {}).get("security", {})

    if not security.get("two_factor_enabled"):
        return jsonify({"error": "2FA not enabled"}), 400
    
    secret = security.get("two_factor_secret")
    if not secret:
        return jsonify({"error": "2FA secret missing"}), 400
    
    totp = pyotp.TOTP(secret)

    if not totp.verify(code, valid_window=1):
        return jsonify({"error": "Invalid 2FA code"}), 401
    
    return _issue_jwt(user)


def _issue_jwt(user):
    secret = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")

    token = jwt.encode(
        {
            "user": user["username"],
            "admin": user.get("admin", False),
            "iat": datetime.datetime.now(datetime.UTC).timestamp(),
            "exp": (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)).timestamp(),
        },
        secret,
        algorithm="HS256",
    )

    push_login_history(user["_id"], {
        "timestamp": datetime.datetime.now(datetime.UTC)
    })

    return jsonify({"token": token}), 200


def logout(token: str):
    add_blacklist_token(token)
    return jsonify({"message": "Logout successful"}), 200
