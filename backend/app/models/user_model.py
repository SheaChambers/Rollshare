from bson import ObjectId
from app.db import get_db
from app.models.techniques_model import techniques_col

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

def add_saved_technique(user_id, technique_id):
    return users_col().update_one(
        {"_id": user_id},
        {"$addToSet": {"saved_techniques": technique_id}}
    )

def get_saved_techniques(id_list):
    query_ids = [ObjectId(tid) for tid in id_list]
    return list(techniques_col().find(
        {"_id": {"$in": query_ids}}
    ))

def remove_saved_technique(user_id, technique_id):
    return users_col().update_one(
        {"_id": user_id},
        {"$pull": {"saved_techniques": technique_id}}
    )
