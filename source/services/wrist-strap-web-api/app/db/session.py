# File: app/db/session.py

import logging
import pymongo
from app.core.config import settings
from typing import Generator, Any

logger = logging.getLogger(__name__)

try:
    client = pymongo.MongoClient(
        settings.mongo_details,
        username=settings.mongo_user,
        password=settings.mongo_password
    )
    client.admin.command('ismaster')

    db_global = client[settings.database_name]
    users_collection = db_global.get_collection("users")

    db_devices = client[settings.device_database_name]
    devices_collection = db_devices.get_collection("devices")
    historical_logs = db_devices.get_collection("historical_logs")

    logger.info("Successfully connected and authenticated to MongoDB.")
except Exception as e:
    logger.critical(f"Error connecting to MongoDB: {e}", exc_info=True)
    exit()

def get_db() -> Generator[pymongo.database.Database, Any, None]:
    """Yields the main database instance (db_devices) for dependency injection."""
    try:
        yield db_devices
    finally:
        pass