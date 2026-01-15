from flask import Blueprint, request, jsonify, make_response
import datetime
import jwt
import bcrypt
import os
from app.db import get_db
from app.decorators.auth_decorators import jwt_required

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/api/v1.0/login", methods=["POST"])
def login():
    db = get_db()

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return make_response(jsonify({"error": "Username and password required"}), 400)

    user = db.users.find_one({"username": username})
    if not user or not bcrypt.checkpw(password.encode(), user["password"]):
        return make_response(jsonify({"error": "Invalid credentials"}), 400)

    now = datetime.datetime.now(datetime.UTC)

    token = jwt.encode(
        {
            "user": user["username"],
            "admin": user.get("admin", False),
            "iat": int(now.timestamp()),
            "exp": int((now + datetime.timedelta(hours=1)).timestamp())
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256"
    )

    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": now}}
    )

    return jsonify({"token": token}), 200


@auth_bp.route("/api/v1.0/logout", methods=["POST"])
@jwt_required
def logout(current_user, is_admin):
    db = get_db()
    token = request.headers["x-access-token"]
    db.blacklist.insert_one({"token": token})
    return jsonify({"message": "Logout successful"}), 200
