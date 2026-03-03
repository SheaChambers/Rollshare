from app.db import get_db
import datetime
from bson import ObjectId


def users_col():
    return get_db().users


def techniques_col():
    return get_db().techniques


def gyms_col():
    return get_db().gyms


def count_users():
    return users_col().count_documents({})


def count_techniques():
    return techniques_col().count_documents({})


def count_gyms():
    return gyms_col().count_documents({})


def count_reviews():
    total = 0

    for t in techniques_col().find({}, {"reviews": 1}):
        total += len(t.get("reviews", []))

    for g in gyms_col().find({}, {"reviews": 1}):
        total += len(g.get("reviews", []))

    return total


def count_likes():
    total = 0
    for t in techniques_col().find({}, {"likes": 1}):
        total += len(t.get("likes", []))
    return total


def count_saves():
    total = 0
    for u in users_col().find({}, {"saved_techniques": 1}):
        total += len(u.get("saved_techniques", []))
    return total


def count_new_users_this_week():
    one_week_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)

    return users_col().count_documents({
        "created_at": {"$gte": one_week_ago}
    })


def top_techniques_by_likes():
    pipeline = [
        {
            "$project": {
                "name": 1,
                "likes_count": {"$size": {"$ifNull": ["$likes", []]}}
            }
        },
        {"$sort": {"likes_count": -1}},
        {"$limit": 5}
    ]

    return list(techniques_col().aggregate(pipeline))

def ban_user(user_id: str, admin_username: str):
    return users_col().update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "banned": True,
                "banned_at": datetime.datetime.now(datetime.UTC),
                "banned_by": admin_username
            }
        }
    )

def unban_user(user_id):
    return users_col().update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "banned": False
            },
            "$unset": {
                "banned_at": "",
                "banned_by": ""
            }
        }
    )

def feature_technique(technique_id):
    techniques_col().update_many({}, {"$set": {"featured": False}})

    return techniques_col().update_one(
        {"_id": technique_id},
        {"$set": {"featured": True}}
    )