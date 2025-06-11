# File: app/crud/setting.py

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import pymongo.database
from app.schemas.setting import SystemSettingsCreateUpdate

# Get a logger instance for this file
logger = logging.getLogger(__name__)

# Define a fixed ID for the single settings document
SETTINGS_DOC_ID = "global_system_settings"


def get_settings(db: pymongo.database.Database) -> Optional[Dict[str, Any]]:
    """
    Retrieves the global system settings document from MongoDB.
    """
    settings_collection = db.get_collection("system_settings")
    logger.info(f"Attempting to find settings document with ID: {SETTINGS_DOC_ID}")
    settings_doc = settings_collection.find_one({"_id": SETTINGS_DOC_ID})
    if settings_doc:
        logger.info("Found existing settings document.")
    else:
        logger.info("No settings document found.")
    return settings_doc


def update_settings(db: pymongo.database.Database, settings_in: SystemSettingsCreateUpdate) -> Dict[str, Any]:
    """
    Updates or creates the global system settings document in MongoDB.
    """
    settings_collection = db.get_collection("system_settings")

    update_data = settings_in.model_dump(by_alias=False)
    current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    update_data['updatedAt'] = current_time_ms

    logger.info(f"Upserting settings document with ID: {SETTINGS_DOC_ID}")

    # Use upsert=True to create the document if it doesn't exist.
    result = settings_collection.update_one(
        {"_id": SETTINGS_DOC_ID},
        {"$set": update_data, "$setOnInsert": {"createdAt": current_time_ms}},
        upsert=True
    )

    if result.upserted_id:
        logger.info(f"Created new settings document with upserted ID: {result.upserted_id}")
    elif result.modified_count > 0:
        logger.info(f"Updated existing settings document.")
    else:
        logger.info("Settings update operation resulted in no changes.")

    updated_doc = settings_collection.find_one({"_id": SETTINGS_DOC_ID})
    if updated_doc is None:
        logger.critical("Failed to retrieve settings document after an upsert operation!")
        raise Exception("Failed to retrieve settings document after update/insert.")

    return updated_doc