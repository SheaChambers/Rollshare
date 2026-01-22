import datetime
import bcrypt
import jwt
from bson import ObjectId
from flask import jsonify
import os

from app.models.user_model import (
    find_by_username, find_by_email, insert_user, list_users, 
    users_col, update_user, delete_user
)

def register(request):
    required_fields = ["username", "email", "password", "confirm_password", "belt_rank"]
    for f in required_fields:
        if f not in request.form or not request.form[f].strip():
            return jsonify({"error": f"Missing required field: {f}"}), 400

    username = request.form["username"].strip()
    email = request.form["email"].strip()
    password = request.form["password"]

    if find_by_username(username):
        return jsonify({"error": "Username already exists"}), 400
    if find_by_email(email):
        return jsonify({"error": "Email already in use"}), 400
    if password != request.form["confirm_password"]:
        return jsonify({"error": "Passwords do not match"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    new_user = {
        "_id": ObjectId(),
        "username": username,
        "email": email,
        "password": hashed_pw,
        "belt_rank": request.form["belt_rank"].strip(),
        "bio": request.form.get("bio", "").strip(),
        "admin": False,
        "created_at": datetime.datetime.now(datetime.UTC),
    }

    insert_user(new_user)

    secret = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    token = jwt.encode(
        {
            "user": username,
            "admin": False,
            "iat": datetime.datetime.now(datetime.UTC).timestamp(),
            "exp": (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)).timestamp(),
        },
        secret,
        algorithm="HS256",
    )

    return jsonify({"message": "User registered successfully", "token": token}), 201


def get_all_users():
    data = []
    for u in list_users({"password": 0}):
        u["_id"] = str(u["_id"])
        data.append(u)
    return jsonify(data), 200


def get_user_by_id(user_id: str, requester: str, is_admin: bool):
    if not ObjectId.is_valid(user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    u = users_col().find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not u:
        return jsonify({"error": "User not found"}), 404

    u["_id"] = str(u["_id"])
    if is_admin:
        return jsonify(u), 200

    public = {
        "username": u.get("username"),
        "created_at": u.get("created_at"),
        "bio": u.get("bio", ""),
        "belt_rank": u.get("belt_rank", "")
    }
    return jsonify(public), 200


def get_me(requester: str):
    u = users_col().find_one({"username": requester}, {"password": 0})
    if not u:
        return jsonify({"error": "User not found"}), 404
    u["_id"] = str(u["_id"])
    return jsonify(u), 200


def update_user_profile(user_id: str, requester: str, is_admin: bool, request):
    if not ObjectId.is_valid(user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    u = users_col().find_one({"_id": ObjectId(user_id)})
    if not u:
        return jsonify({"error": "User not found"}), 404

    if not is_admin and u.get("username") != requester:
        return jsonify({"error": "Not authorised"}), 403

    allowed = ["username", "email", "belt_rank", "bio"]
    fields = {}
    for f in allowed:
        if f in request.form:
            val = request.form[f].strip()
            if not val:
                return jsonify({"error": f"{f} cannot be empty"}), 400
            fields[f] = val

    if not fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    res = update_user(ObjectId(user_id), fields)
    if res.modified_count == 0:
        return jsonify({"error": "No changes made"}), 400

    return jsonify({"message": "User updated"}), 200


def reset_password(requester: str, request):
    current_pw = request.form.get("current_password")
    new_pw = request.form.get("new_password")

    if not current_pw or not new_pw:
        return jsonify({"error": "Both current_password and new_password are required"}), 400

    u = find_by_username(requester)
    if not u:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(current_pw.encode("utf-8"), u["password"]):
        return jsonify({"error": "Incorrect current password"}), 401

    if current_pw == new_pw:
        return jsonify({"error": "New password cannot be the same as previous"}), 400

    hashed = bcrypt.hashpw(new_pw.encode("utf-8"), bcrypt.gensalt())
    update_user(u["_id"], {"password": hashed, "password_updated_at": datetime.datetime.now(datetime.UTC)})
    return jsonify({"message": "Password updated successfully"}), 200


def remove_user(user_id: str, requester: str, is_admin: bool):
    if not ObjectId.is_valid(user_id):
        return jsonify({"error": "Invalid user ID"}), 400

    u = users_col().find_one({"_id": ObjectId(user_id)})
    if not u:
        return jsonify({"error": "User not found"}), 404

    if not is_admin and u.get("username") != requester:
        return jsonify({"error": "Not authorised"}), 403

    res = delete_user(ObjectId(user_id))
    if res.deleted_count == 0:
        return jsonify({"error": "Deletion failed"}), 500

    return jsonify({}), 204
