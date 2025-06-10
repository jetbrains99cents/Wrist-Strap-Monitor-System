import pymongo
from app.core.config import settings
from typing import Generator, Any # ADDED imports for Generator, Any

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

    # Get a handle for the historical logs collection (variable name as per your provided content)
    historical_logs = db_devices.get_collection("historical_logs") # Variable name is 'historical_logs'

    print("Successfully connected and authenticated to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

# NEW: Dependency to yield the database object
# This allows other modules (like crud/log.py) to receive the correct database instance
# and then get the collections from it.
def get_db() -> Generator[pymongo.database.Database, Any, None]:
    """Yields the main database instance (db_devices) for dependency injection."""
    try:
        yield db_devices # Yield the database object that contains historical_logs
    finally:
        # In a real application, you might close connections here if they were per-request,
        # but for a global client, often nothing is needed.
        pass