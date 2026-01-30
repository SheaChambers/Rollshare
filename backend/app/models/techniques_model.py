from bson import ObjectId
from app.db import get_db

def techniques_col():
    return get_db().techniques

def insert_technique(doc: dict):
    return techniques_col().insert_one(doc)

def count(filters: dict):
    return techniques_col().count_documents(filters)

def find_many(filters: dict, sort_field: str, sort_direction: int, skip: int, limit: int):
    return techniques_col().find(filters).sort(sort_field, sort_direction).skip(skip).limit(limit)

def find_one_by_id(technique_id: str):
    return techniques_col().find_one({"_id": ObjectId(technique_id)})

def update_by_id(technique_id: str, fields: dict):
    return techniques_col().update_one({"_id": ObjectId(technique_id)}, {"$set": fields})

def delete_by_id(technique_id: str):
    return techniques_col().delete_one({"_id": ObjectId(technique_id)})

def push_review(technique_id: str, review: dict):
    return techniques_col().update_one({"_id": ObjectId(technique_id)}, {"$push": {"reviews": review}})

def get_reviews_only(technique_id: str):
    return techniques_col().find_one({"_id": ObjectId(technique_id)}, {"reviews": 1, "_id": 0})

def find_review_projection(technique_id: str, review_id: str):
    return techniques_col().find_one(
        {"_id": ObjectId(technique_id), "reviews._id": ObjectId(review_id)},
        {
            "reviews.$": 1,
            "reviews.user": 1
        }
    )

def update_review(technique_id: str, review_id: str, update_fields: dict):
    return techniques_col().update_one(
        {"_id": ObjectId(technique_id), "reviews._id": ObjectId(review_id)},
        {"$set": update_fields}
    )

def pull_review(technique_id: str, review_id: str):
    return techniques_col().update_one(
        {"_id": ObjectId(technique_id)},
        {"$pull": {"reviews": {"_id": ObjectId(review_id)}}}
    )
