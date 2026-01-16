from flask import Blueprint, request, make_response, jsonify
from bson import ObjectId
import datetime
import bcrypt
import os
import jwt
from app.db import get_db
from app.decorators.auth_decorators import jwt_required, admin_required


users_bp = Blueprint("users_bp", __name__)

# Selecting the collections
def get_users_collection():
    return get_db().users

def get_blacklist_collection():
    return get_db().blacklist

# Register a user
@users_bp.route("/api/v1.0/users/register", methods=['POST'])
def register_user():
    users = get_users_collection()

    required_fields = ["username", "email", "password", "confirm_password", "belt_rank"]
    for field in required_fields:
        if field not in request.form:
            return make_response(jsonify({"error": f"Missing required field: {field}"}), 400)
    
        value = request.form[field].strip()
        if not value:
            return make_response(jsonify({"error": f"{field} cannot be empty"}), 400)
    
    username = request.form["username"].strip()
    email = request.form["email"].strip()
    password = request.form["password"]
    
    if users.find_one({"username": username}):
        return make_response(jsonify({"error": "Username already exists"}), 400)
    if users.find_one({"email": email}):
        return make_response(jsonify({"error": "Email already in use"}), 400)
    if password != request.form["confirm_password"]:
        return make_response(jsonify({"error": "Passwords do not match"}), 400)
    
    hashed_pw = bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt())

    new_user = {
        "_id": ObjectId(),
        "username": username,
        "email": email,
        "password": hashed_pw,
        "belt_rank": request.form["belt_rank"].strip(),
        "bio": request.form.get("bio"),
        "admin": False,
        "created_at": datetime.datetime.now(datetime.UTC)
    }

    users.insert_one(new_user)

    token = jwt.encode(
        {
            "user": request.form["username"],
            "admin": False,
            "iat": datetime.datetime.now(datetime.UTC).timestamp(),
            "exp": (datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=1)).timestamp()
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm="HS256"
    )

    new_user_url = f"http://localhost:5001/api/v1.0/users/{new_user['_id']}"
    
    return make_response(jsonify({"message": "User registered successfully",
                                  "url": new_user_url,
                                  "token": token}), 201)

# Fetch all users (Admin only)
@users_bp.route("/api/v1.0/users", methods=['GET'])
@jwt_required
@admin_required
def fetch_all_users(current_user, is_admin):
    users = get_users_collection()

    data_to_return = []
    for user in users.find({}, {"password": 0}): # Exclude passwords
        user["_id"] = str(user["_id"])
        data_to_return.append(user)
    return make_response(jsonify(data_to_return), 200)

# Fecth one user
@users_bp.route("/api/v1.0/users/<string:id>", methods=['GET'])
@jwt_required
def fetch_one_user(id, current_user, is_admin):
    users = get_users_collection()

    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid user ID"}), 400)
    
    user = users.find_one({"_id": ObjectId(id)}, {"password": 0})
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)
    
    user["_id"] = str(user["_id"])

    # If the requester is admin
    if is_admin:
        return make_response(jsonify(user), 200)
    
    # If the requester is a user (public viewing)
    public_fields = {
        "username": user.get("username"),
        "created_at": user.get("created_at"),
        "bio": user.get("bio", ""),
        "belt_rank": user.get("belt_rank", "")
    }

    return make_response(jsonify(public_fields), 200)

@users_bp.route("/api/v1.0/users/me", methods=['GET'])
@jwt_required
def get_current_user(current_user, is_admin):
    users = get_users_collection()

    user = users.find_one({"username": current_user}, {"password": 0})
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)
    
    user["_id"] = str(user["_id"])
    return make_response(jsonify(user), 200)

# Edit user details
@users_bp.route("/api/v1.0/users/<string:id>", methods=['PUT'])
@jwt_required
def edit_user(id, current_user, is_admin):
    users = get_users_collection()

    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid user ID"}), 400)
    
    user = users.find_one({"_id": ObjectId(id)})
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)
    
    # Only admin or the user themselves can edit
    if not is_admin and user["username"] != current_user:
        return make_response(jsonify({"error": "Not authorised"}), 401)
    
    update_fields = {}
    allowed_fields = ["username", "email", "belt_rank", "bio"]
    for field in allowed_fields:
        if field in request.form:
            update_fields[field] = request.form[field]
    
    if not update_fields:
        return make_response(jsonify({"error": "No valid fields provided for update"}), 400)
    
    result = users.update_one({"_id": ObjectId(id)}, {"$set": update_fields})

    if result.modified_count == 0:
        return make_response(jsonify({"error": "No changes made"}), 400)
    
    edited_user_link = "http://localhost:5001/api/v1.0/users/" + id
    return make_response(jsonify({"url": edited_user_link}), 200)

# Change user password
@users_bp.route("/api/v1.0/users/reset-password", methods=['PUT'])
@jwt_required
def reset_password(current_user, is_admin):
    users = get_users_collection()

    current_pw = request.form.get("current_password")
    new_pw = request.form.get("new_password")

    if not current_pw or not new_pw:
        return make_response(jsonify({"error": "Both current_password and new_password are required"}), 400)
    
    user = users.find_one({"username": current_user})
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)
    
    if not bcrypt.checkpw(current_pw.encode("utf-8"), user["password"]):
        return make_response(jsonify({"error": "Incorrect current password"}), 401)
    
    if current_pw == new_pw:
        return make_response(jsonify({"error": "New password cannot be the same as previous"}), 400)
    
    hashed_new_pw = bcrypt.hashpw(new_pw.encode("utf-8"), bcrypt.gensalt())
    users.update_one({"_id": user["_id"]}, {"$set": {"password": hashed_new_pw, "password_updated_at": datetime.datetime.now(datetime.UTC)}})

    return make_response(jsonify({"message": "Password updated successfully"}), 200)

# Delete user
@users_bp.route("/api/v1.0/users/<string:id>", methods=['DELETE'])
@jwt_required
def delete_user(id, current_user, is_admin):
    users = get_users_collection()

    if not ObjectId.is_valid(id):
        return make_response(jsonify({"error": "Invalid user ID"}), 400)
    
    user = users.find_one({"_id": ObjectId(id)})
    if not user:
        return make_response(jsonify({"error": "Invalid user ID — user not found"}), 404)
    
    # Checking if user is authorised
    if not is_admin and user['username'] != current_user:
        return make_response(jsonify({"error": "Not authorised"}), 401)
    
    result = users.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return make_response(jsonify({"error": "User not found"}), 404)
    
    return make_response(jsonify({}), 204)