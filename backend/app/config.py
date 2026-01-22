import os

class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "rollshare")
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")

def get_config():
    return Config
