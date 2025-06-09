import pymongo
from app.core.config import settings

# Removed motor import, as per the revert request to use pymongo
# from motor.motor_asyncio import AsyncIOMotorClient

try:
    # Using pymongo.MongoClient for synchronous operations
    client = pymongo.MongoClient(
        settings.mongo_details,
        username=settings.mongo_user,
        password=settings.mongo_password
    )
    client.admin.command('ismaster')

    # Get a handle for the global user database
    db_global = client[settings.database_name]
    users_collection = db_global.get_collection("users")

    # Get a handle for the service-specific device database
    db_devices = client[settings.device_database_name]
    devices_collection = db_devices.get_collection("devices")

    # Get a handle for the historical logs collection
    # Changed variable name to `historical_logs` as requested
    historical_logs = db_devices.get_collection("historical_logs") # Changed variable name

    print("Successfully connected and authenticated to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()