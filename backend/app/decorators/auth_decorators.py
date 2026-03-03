from flask import request, jsonify, make_response
import jwt
import os
from functools import wraps
import datetime
from app.db import get_db


def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("x-access-token")
        if not token:
            return make_response(jsonify({"message": "Token is missing"}), 401)

        try:
            data = jwt.decode(
                token,
                os.getenv("JWT_SECRET_KEY", "dev-secret-change-me"),
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return make_response(jsonify({"message": "Token expired"}), 401)
        except jwt.InvalidTokenError:
            return make_response(jsonify({"message": "Token invalid"}), 401)

        db = get_db()

        # blacklist check
        if db.blacklist.find_one({"token": token}):
            return make_response(jsonify({"message": "Token has been cancelled"}), 401)

        # password reset invalidation
        user = db.users.find_one({"username": data["user"]})
        if not user:
            return make_response(jsonify({"message": "User not found"}), 401)
        
        if user.get("banned", False):
            return make_response(jsonify({
                "error": "Account is banned",
                "banned_at": user.get("banned_at"),
                "banned_by": user.get("banned_by")
            }), 403)
        
        pwd_updated = user.get("password_updated_at")
        issued_at = data.get("iat")

        if pwd_updated and issued_at:
            issued_dt = datetime.datetime.fromtimestamp(issued_at, datetime.UTC)
            pwd_updated = pwd_updated.replace(tzinfo=datetime.UTC)
            if issued_dt < pwd_updated:
                return make_response(
                    jsonify({"message": "Token no longer valid"}), 401
                )

        kwargs["current_user"] = data["user"]
        kwargs["is_admin"] = data.get("admin", False)
        return func(*args, **kwargs)

    return wrapper


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not kwargs.get("is_admin", False):
            return make_response(jsonify({"message": "Admin access required"}), 403)
        return func(*args, **kwargs)
    return wrapper
