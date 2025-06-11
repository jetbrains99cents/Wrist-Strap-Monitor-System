# File: app/crud/device.py

import logging
from app.db.session import devices_collection
from app.schemas.device import DeviceCreate, DeviceUpdate
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Optional

# Get a logger instance for this file
logger = logging.getLogger(__name__)


def create_device(device_in: DeviceCreate):
    """Creates a new device document in the database."""
    logger.info(f"Attempting to create a new device with name: '{device_in.name}'")
    new_device_doc = device_in.model_dump()
    current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    new_device_doc['installation_date'] = current_timestamp
    new_device_doc['createdAt'] = current_timestamp
    new_device_doc['updatedAt'] = current_timestamp
    new_device_doc['last_event'] = None

    result = devices_collection.insert_one(new_device_doc)
    created_device = devices_collection.find_one({"_id": result.inserted_id})
    logger.info(f"Successfully created device '{device_in.name}' with new ID: {result.inserted_id}")
    return created_device


def get_all_devices(skip: int = 0, limit: int = 100) -> List[dict]:
    """Retrieves all devices from the database with pagination."""
    logger.info(f"Fetching all devices with skip: {skip}, limit: {limit}")
    return list(devices_collection.find().skip(skip).limit(limit))


def get_device(device_id: str) -> Optional[dict]:
    """Retrieves a single device by its ID."""
    logger.info(f"Attempting to fetch device with ID: {device_id}")
    try:
        device = devices_collection.find_one({"_id": ObjectId(device_id)})
        if device:
            logger.info(f"Found device with ID: {device_id}")
        else:
            logger.warning(f"No device found with ID: {device_id}")
        return device
    except Exception as e:
        logger.error(f"Error fetching device with ID {device_id}. Invalid ID format or DB error: {e}")
        return None


def update_device(device_id: str, device_in: DeviceUpdate) -> Optional[dict]:
    """Updates a device document in the database."""
    logger.info(f"Attempting to update device with ID: {device_id}")
    update_data = device_in.model_dump(exclude_unset=True)
    if not update_data:
        logger.warning(
            f"Update called for device ID {device_id} but no update data was provided. Returning current device.")
        return get_device(device_id)

    update_data['updatedAt'] = int(datetime.now(timezone.utc).timestamp() * 1000)

    result = devices_collection.update_one(
        {"_id": ObjectId(device_id)},
        {"$set": update_data}
    )
    if result.modified_count == 1:
        logger.info(f"Successfully updated device with ID: {device_id}")
        return get_device(device_id)

    logger.warning(
        f"Update operation for device ID {device_id} did not modify any documents. The device may not exist or the data was the same.")
    return None


def delete_device(device_id: str) -> bool:
    """Deletes a device document from the database."""
    logger.info(f"Attempting to delete device with ID: {device_id}")
    try:
        delete_result = devices_collection.delete_one({"_id": ObjectId(device_id)})
        if delete_result.deleted_count == 1:
            logger.info(f"Successfully deleted device with ID: {device_id}")
            return True
        else:
            logger.warning(
                f"Delete operation for device ID {device_id} did not delete any documents. It may not have existed.")
            return False
    except Exception as e:
        logger.error(f"Error deleting device with ID {device_id}. Invalid ID format or DB error: {e}")
        return False