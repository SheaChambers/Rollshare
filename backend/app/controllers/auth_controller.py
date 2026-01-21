import datetime
import jwt
import bcrypt
from flask import jsonify
from app.models.user_model import find_by_username, update_user, add_blacklist_token
import os

def login(request):
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = find_by_username(username)
    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return jsonify({"error": "Invalid username or password"}), 400

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

    update_user(user["_id"], {"last_login": datetime.datetime.now(datetime.UTC)})
    return jsonify({"token": token}), 200


def logout(token: str):
    add_blacklist_token(token)
    return jsonify({"message": "Logout successful"}), 200
