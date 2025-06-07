# File: app/db/session.py

import pymongo
from app.core.config import settings

try:
    client = pymongo.MongoClient(settings.MONGO_DETAILS)
    db = client[settings.DATABASE_NAME]
    users_collection = db.get_collection("users")
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()