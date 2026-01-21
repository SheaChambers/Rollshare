from app.db import get_db

def users_col():
    return get_db().users

def blacklist_col():
    return get_db().blacklist

def find_by_username(username: str):
    return users_col().find_one({"username": username})

def find_by_email(email: str):
    return users_col().find_one({"email": email})

def insert_user(doc: dict):
    return users_col().insert_one(doc)

def update_user(user_id, fields: dict):
    return users_col().update_one({"_id": user_id}, {"$set": fields})

def delete_user(user_id):
    return users_col().delete_one({"_id": user_id})

def list_users(projection=None):
    return users_col().find({}, projection or {})

def add_blacklist_token(token: str):
    return blacklist_col().insert_one({"token": token})

def token_is_blacklisted(token: str) -> bool:
    return blacklist_col().find_one({"token": token}) is not None
