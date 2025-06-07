# File: app/db/session.py
import pymongo
from app.core.config import settings

try:
    client = pymongo.MongoClient(
        settings.mongo_details,
        username=settings.mongo_user,
        password=settings.mongo_password
    )
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    db = client[settings.database_name]
    users_collection = db.get_collection("users")
    print("Successfully connected and authenticated to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()