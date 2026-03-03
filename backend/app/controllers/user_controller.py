import datetime
import bcrypt
import jwt
from bson import ObjectId
from flask import jsonify
import os
import pyotp

from app.services.blob_storage_service import BlobStorageService
from app.models.user_model import (
    find_by_username, find_by_email, insert_user, list_users, 
    users_col, update_user, delete_user, add_saved_technique,
    get_saved_techniques, remove_saved_technique, get_techniques_by_user
)
from app.models.techniques_model import (techniques_col)

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
        "banned": False,
        "saved_techniques": [],
        "created_at": datetime.datetime.now(datetime.UTC),

        "settings": {
            "security": {
                "two_factor_enabled": False,
                "two_factor_secret": None,
                "login_history": []
            },
            "privacy": {
                "profile_visibility": "public"
            },
            "preferences": {
                "email_notifications": True,
                "theme": "light"
            }
        }
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

    if u.get("avatar_url"):
        storage = BlobStorageService()
        u["avatar_url"] = storage.generate_read_url(u["avatar_url"])
        
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


def save_technique(user_id, request):
    user = find_by_username(user_id)
    technique_id = request.json.get("technique_id")

    if not ObjectId.is_valid(technique_id):
        return jsonify({"error": "Invalid technique ID"}), 400
    
    add_saved_technique(user["_id"], technique_id)

    return jsonify({"message": "Technique saved"}), 200


def get_saved_techniques_controller(username):
    user = find_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 400
    
    saved_ids = user.get("saved_techniques", [])

    if not saved_ids:
        return jsonify([]), 200

    techniques = get_saved_techniques(saved_ids)

    storage = BlobStorageService()

    for roll in techniques:
        roll["_id"] = str(roll["_id"])

        if roll.get("thumbnail_blob_url"):
            roll["thumbnail_blob_url"] = storage.generate_read_url(roll["thumbnail_blob_url"])
        
        if roll.get("video_blob_url"):
            roll["video_blob_url"] = storage.generate_read_url(roll["video_blob_url"])

        if "reviews" in roll:
            for review in roll["reviews"]:
                if "_id" in review:
                    review["_id"] = str(review["_id"])
    
    return jsonify(techniques), 200


def unsave_technique(user_id, technique_id):
    user = find_by_username(user_id)
    remove_saved_technique(user["_id"], technique_id)

    return jsonify({}), 204

def get_user_rolls(username):
    user = find_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    techniques = get_techniques_by_user(username)

    storage = BlobStorageService()

    rolls = []
    for roll in techniques:
        roll["_id"] = str(roll["_id"])

        if roll.get("thumbnail_blob_url"):
            roll["thumbnail_blob_url"] = storage.generate_read_url(roll["thumbnail_blob_url"])
        
        if roll.get("video_blob_url"):
            roll["video_blob_url"] = storage.generate_read_url(roll["video_blob_url"])

        if "reviews" in roll:
            for review in roll["reviews"]:
                if "_id" in review:
                    review["_id"] = str(review["_id"])
        
        rolls.append(roll)
    
    return jsonify({"techniques": rolls}), 200


def get_settings(requester):
    user = find_by_username(requester)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.get("settings", {})), 200


def update_settings(requester, request):
    user = find_by_username(requester)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400
    
    update_fields = {}

    if "theme" in data:
        if data["theme"] not in ["light", "dark"]:
            return jsonify({"error": "Invalid theme value"}), 400
        update_fields["settings.preferences.theme"] = data["theme"]
    
    if "email_notifications" in data:
        if not isinstance(data["email_notifications"], bool):
            return jsonify({"error": "email_notifications must be boolean"}), 400
        update_fields["settings.preferences.email_notifications"] = data["email_notifications"]

    if "profile_visibility" in data:
        if data["profile_visibility"] not in ["public", "private"]:
            return jsonify({"error": "Invalid profile_visibility value"}), 400
        update_fields["settings.privacy.profile_visibility"] = data["profile_visibility"]
    
    if not update_fields:
        return jsonify({"error": "No valid preference fields provided"}), 400
    
    update_user(user["_id"], update_fields)

    return jsonify({"message": "Preferences updated"}), 200

def enable_2fa(requester):
    user = find_by_username(requester)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    security = user.get("settings", {}).get("security", {})
    existing_secret = security.get("two_factor_secret")
    enabled = security.get("two_factor_enabled", False)

    if enabled:
        return jsonify({"error": "2FA already enabled"}), 400
    
    secret = existing_secret or pyotp.random_base32()

    if not existing_secret:
        update_user(user["_id"], {
            "settings.security.two_factor_secret": secret,
            "settings.security.two_factor_enabled": False
        })

    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=user["email"],
        issuer_name="RollShare"
    )

    return jsonify({
        "provisioning_uri": provisioning_uri
    }), 200


def verify_2fa_setup(requester, request):
    user = find_by_username(requester)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    code = request.json.get("code")
    secret = user.get("settings", {}).get("security", {}).get("two_factor_secret")

    if not secret:
        return jsonify({"error": "2FA not initiated"}), 400
    
    totp = pyotp.TOTP(secret)

    if not totp.verify(code, valid_window=1):
        return jsonify({"error": "Invalid verification code"}), 400
    
    update_user(user["_id"], {
        "settings.security.two_factor_enabled": True
    })

    return jsonify({"message": "2FA successfully enabled"}), 200


def disable_2fa(requester):
    user = find_by_username(requester)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    update_user(user["_id"], {
        "settings.security.two_factor_enabled": False,
        "settings.security.two_factor_secret": None
    })

    return jsonify({"message": "2FA disabled"}), 200


def upload_avatar(requester: str, request):
    user = find_by_username(requester)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if "avatar" not in request.files:
        return jsonify({"error": "Avatar image is required"}), 400

    avatar = request.files["avatar"]

    if not avatar or avatar.filename.strip() == "":
        return jsonify({"error": "No image selected"}), 400

    if not (avatar.content_type or "").startswith("image/"):
        return jsonify({"error": "Invalid file type. Must be an image"}), 400

    try:
        storage = BlobStorageService()

        ext = os.path.splitext(avatar.filename)[1].lower()
        blob_name = f"avatars/{requester}_{ObjectId()}{ext}"

        storage.upload_file(
            avatar.stream,
            blob_name,
            avatar.content_type
        )

        update_user(user["_id"], {"avatar_url": blob_name})

        avatar_url = storage.generate_read_url(blob_name)

        return jsonify({
            "message": "Avatar updated successfully",
            "avatar_url": avatar_url
        }), 200

    except Exception:
        return jsonify({"error": "Failed to upload avatar"}), 500