import logging
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from typing import Generator, Any, Optional
from fastapi import HTTPException, status  # Required for HTTP errors in getters

logger = logging.getLogger(__name__)

# --- SYNCHRONOUS PYMONGO CLIENT SETUP (Managed by lifespan) ---
client: Optional[pymongo.MongoClient] = None
db_global: Optional[pymongo.database.Database] = None  # This is the global user DB instance
db_devices: Optional[pymongo.database.Database] = None  # This is the device DB instance
users_collection: Optional[pymongo.collection.Collection] = None
devices_collection: Optional[pymongo.collection.Collection] = None
historical_logs: Optional[pymongo.collection.Collection] = None


async def connect_to_mongo_sync_managed():
    """Establishes synchronous connections to MongoDB using pymongo, managed by lifespan."""
    global client, db_global, db_devices, users_collection, devices_collection, historical_logs
    try:
        logger.info("Attempting to connect to MongoDB (managed synchronous client)...")
        client = pymongo.MongoClient(
            settings.mongo_details,
            username=settings.mongo_user,
            password=settings.mongo_password
        )

        client.admin.command('ismaster')

        db_global = client[settings.database_name]  # Assign the global user DB instance
        users_collection = db_global.get_collection("users")

        db_devices = client[settings.device_database_name]  # Assign the device DB instance
        devices_collection = db_devices.get_collection("devices")
        historical_logs = db_devices.get_collection("historical_logs")

        logger.info("Successfully connected and authenticated to MongoDB (managed synchronous client).")
    except Exception as e:
        logger.critical(f"Critical Error connecting to MongoDB (managed synchronous client): {e}", exc_info=True)
        raise RuntimeError(f"Failed to connect to MongoDB (managed synchronous client): {e}")


async def close_mongo_connection_sync_managed():
    """Closes the managed synchronous MongoDB connection."""
    global client, db_global, db_devices, users_collection, devices_collection, historical_logs
    if client:
        client.close()
        logger.info("MongoDB managed synchronous connection closed.")
        client = None
        db_global = None
        db_devices = None
        users_collection = None
        devices_collection = None
        historical_logs = None


def get_db() -> Generator[pymongo.database.Database, Any, None]:
    """
    Yields the synchronous device database instance (db_devices) for dependency injection.
    Use this for device-related operations.
    """
    if db_devices is None:
        logger.error("Attempted to access synchronous MongoDB (devices) before it was connected by lifespan.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Synchronous device database not connected.")
    try:
        yield db_devices
    finally:
        pass


# NEW GETTER: For the global user database
def get_db_global_sync() -> Generator[pymongo.database.Database, Any, None]:
    """
    Yields the synchronous global database instance (db_global) for dependency injection.
    Use this for user, settings, or global application data.
    """
    if db_global is None:
        logger.error("Attempted to access synchronous MongoDB (global) before it was connected by lifespan.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Synchronous global database not connected.")
    try:
        yield db_global
    finally:
        pass


# --- ASYNCHRONOUS MOTOR CLIENT SETUP (Managed by lifespan) ---
async_client: Optional[AsyncIOMotorClient] = None
_async_db_global_instance: Optional[AsyncIOMotorDatabase] = None
_async_db_devices_instance: Optional[AsyncIOMotorDatabase] = None


async def connect_to_mongo_async():
    """Establishes asynchronous connections to MongoDB using Motor."""
    global async_client, _async_db_global_instance, _async_db_devices_instance
    try:
        logger.info("Attempting to connect to MongoDB (asynchronous client)...")
        async_client = AsyncIOMotorClient(
            settings.mongo_details,
            username=settings.mongo_user,
            password=settings.mongo_password
        )

        await async_client.admin.command('ping')

        _async_db_global_instance = async_client[settings.database_name]
        _async_db_devices_instance = async_client[settings.device_database_name]

        logger.info(
            f"Successfully connected to MongoDB (asynchronous client). Databases: '{settings.database_name}' and '{settings.device_database_name}'.")

    except Exception as e:
        logger.critical(f"Critical Error connecting to MongoDB (asynchronous client): {e}", exc_info=True)
        raise RuntimeError(f"Failed to connect to MongoDB (asynchronous client): {e}")


async def close_mongo_connection_async():
    """Closes the asynchronous MongoDB connection."""
    global async_client, _async_db_global_instance, _async_db_devices_instance
    if async_client:
        async_client.close()
        logger.info("MongoDB asynchronous connection closed.")
        async_client = None
        _async_db_global_instance = None
        _async_db_devices_instance = None


def get_async_db_devices() -> AsyncIOMotorDatabase:
    """
    Returns the asynchronously connected device database instance.
    Raises RuntimeError if the database is not yet connected.
    """
    if _async_db_devices_instance is None:
        logger.critical("Attempted to access asynchronous MongoDB (devices) before it was connected.")
        raise RuntimeError("Asynchronous MongoDB (devices) is not connected.")
    return _async_db_devices_instance


def get_async_db_global() -> AsyncIOMotorDatabase:
    """
    Returns the asynchronously connected global database instance.
    Raises RuntimeError if the database is not yet connected.
    """
    if _async_db_global_instance is None:
        logger.critical("Attempted to access asynchronous MongoDB (global) before it was connected.")
        raise RuntimeError("Asynchronous MongoDB (global) is not connected.")
    return _async_db_global_instance