import os
from pymongo import MongoClient

_client = None

def get_db():
    global _client
    if _client is None:
        conn = os.getenv("MONGODB_CONNECTION_STRING")
        if not conn:
            raise RuntimeError("MONGODB_CONNECTION_STRING not set")
        _client = MongoClient(conn)
    return _client[os.getenv("MONGODB_DB_NAME", "rollshare")]
