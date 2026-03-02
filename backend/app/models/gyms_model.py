from bson import ObjectId
from app.db import get_db

def gyms_col():
    return get_db().gyms

def insert_gym(doc: dict):
    return gyms_col().insert_one(doc)

def count(filters: dict):
    return gyms_col().count_documents(filters)

def find_many(filters: dict, sort_field: str, sort_direction: int, skip: int, limit: int):
    return gyms_col().find(filters).sort(sort_field, sort_direction).skip(skip).limit(limit)

def find_one_by_id(gym_id: str):
    return gyms_col().find_one({"_id": ObjectId(gym_id)})

def update_by_id(gym_id: str, fields: dict):
    return gyms_col().update_one({"_id": ObjectId(gym_id)}, {"$set": fields})

def delete_by_id(gym_id: str):
    return gyms_col().delete_one({"_id": ObjectId(gym_id)})

def push_photos(gym_id: str, photo_urls: list[str]):
    return gyms_col().update_one(
        {"_id": ObjectId(gym_id)},
        {"$push": {"photos": {"$each": photo_urls}}}
    )

def pull_photo(gym_id: str, photo_url: str):
    return gyms_col().update_one(
        {"_id": ObjectId(gym_id)},
        {"$pull": {"photos": photo_url}}
    )

def push_review(gym_id: str, review: dict):
    return gyms_col().update_one({"_id": ObjectId(gym_id)}, {"$push": {"reviews": review}})

def get_reviews_only(gym_id: str):
    return gyms_col().find_one({"_id": ObjectId(gym_id)}, {"reviews": 1, "_id": 0})

def find_review_projection(gym_id: str, review_id: str):
    return gyms_col().find_one(
        {"_id": ObjectId(gym_id), "reviews._id": ObjectId(review_id)},
        {
            "reviews.$": 1,
            "reviews.user": 1
        }
    )

def update_review(gym_id: str, review_id: str, update_fields: dict):
    return gyms_col().update_one(
        {"_id": ObjectId(gym_id), "reviews._id": ObjectId(review_id)},
        {"$set": update_fields}
    )

def pull_review(gym_id: str, review_id: str):
    return gyms_col().update_one(
        {"_id": ObjectId(gym_id)},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}}
    )
