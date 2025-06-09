# File: app/crud/device.py

from app.db.session import devices_collection
from app.schemas.device import DeviceCreate, DeviceUpdate
from datetime import datetime, timezone
from bson import ObjectId
from typing import List, Optional


def create_device(device_in: DeviceCreate):
    new_device_doc = device_in.model_dump()
    current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    new_device_doc['installation_date'] = current_timestamp
    new_device_doc['createdAt'] = current_timestamp
    new_device_doc['updatedAt'] = current_timestamp
    new_device_doc['last_event'] = None

    result = devices_collection.insert_one(new_device_doc)
    created_device = devices_collection.find_one({"_id": result.inserted_id})
    return created_device


def get_all_devices(skip: int = 0, limit: int = 100) -> List[dict]:
    return list(devices_collection.find().skip(skip).limit(limit))


# --- NEW: Get a single device by its ID ---
def get_device(device_id: str) -> Optional[dict]:
    try:
        return devices_collection.find_one({"_id": ObjectId(device_id)})
    except Exception:
        return None


# --- NEW: Update a device in the database ---
def update_device(device_id: str, device_in: DeviceUpdate) -> Optional[dict]:
    update_data = device_in.model_dump(exclude_unset=True)
    if not update_data:
        return get_device(device_id)

    update_data['updatedAt'] = int(datetime.now(timezone.utc).timestamp() * 1000)

    result = devices_collection.update_one(
        {"_id": ObjectId(device_id)},
        {"$set": update_data}
    )
    if result.modified_count == 1:
        return get_device(device_id)
    return None


# --- NEW: Delete a device from the database ---
def delete_device(device_id: str) -> bool:
    delete_result = devices_collection.delete_one({"_id": ObjectId(device_id)})
    return delete_result.deleted_count == 1