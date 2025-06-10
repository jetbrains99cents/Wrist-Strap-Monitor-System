from app.db.session import db_devices  # Assuming db_devices has the system_settings collection
from app.schemas.setting import SystemSettingsCreateUpdate  # Import schemas
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import pymongo.database  # For type hinting 'db' parameter
from bson import ObjectId  # For using ObjectId in queries if necessary

# Define a fixed ID for the single settings document to make it easily identifiable
SETTINGS_DOC_ID = "global_system_settings"


def get_settings(db: pymongo.database.Database) -> Optional[Dict[str, Any]]:
    """
    Retrieves the global system settings document from MongoDB.
    """
    settings_collection = db.get_collection("system_settings")
    settings_doc = settings_collection.find_one({"_id": SETTINGS_DOC_ID})
    return settings_doc


def update_settings(db: pymongo.database.Database, settings_in: SystemSettingsCreateUpdate) -> Dict[str, Any]:
    """
    Updates or creates the global system settings document in MongoDB.
    Handles creation if the document does not exist.
    """
    settings_collection = db.get_collection("system_settings")

    # settings_in has already been validated and converted to internal 24hr format by its model_validator
    update_data = settings_in.model_dump(
        by_alias=False)  # model_dump(by_alias=False) uses field names like 'from_time', 'to_time'

    # Add/update timestamps
    current_time_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    update_data['updatedAt'] = current_time_ms

    # Use upsert=True to create the document if it doesn't exist.
    # $set updates fields, $setOnInsert sets fields only on insertion.
    result = settings_collection.update_one(
        {"_id": SETTINGS_DOC_ID},
        {"$set": update_data, "$setOnInsert": {"createdAt": current_time_ms}},
        upsert=True
    )

    # Retrieve the updated document to return it, ensuring we get all fields including _id and createdAt
    updated_doc = settings_collection.find_one({"_id": SETTINGS_DOC_ID})

    # If for some reason updated_doc is None after upsert (highly unlikely), raise an error
    if updated_doc is None:
        raise Exception("Failed to retrieve settings document after update/insert.")

    return updated_doc