import os
from pymongo import MongoClient

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db

    conn = os.getenv("MONGODB_CONNECTION_STRING")
    if not conn:
        raise RuntimeError("MONGODB_CONNECTION_STRING not set")

    db_name = os.getenv("MONGODB_DB_NAME", "rollshare")

    _client = MongoClient(conn)
    _db = _client[db_name]
    return _db
