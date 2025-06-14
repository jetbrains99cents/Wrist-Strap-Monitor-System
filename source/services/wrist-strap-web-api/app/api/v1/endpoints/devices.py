import logging
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any # Added Any for db type hinting
from app.schemas.device import DeviceInDB, DeviceCreate, DeviceUpdate
from app.crud import device as device_crud
from app.security import get_current_user, get_current_admin_user
from app.db.session import get_db # Import the get_db dependency

print("--- Loading devices.py endpoints ---")
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=DeviceInDB, status_code=status.HTTP_201_CREATED)
def create_device(
        *,
        device_in: DeviceCreate,
        current_user: dict = Depends(get_current_admin_user),
        db: Any = Depends(get_db) # INJECTED: The synchronous DB client
):
    """Create new device (Admin only)."""
    admin_email = current_user.get("email")
    logger.info(f"Admin '{admin_email}' attempting to create new device: {device_in.name}")
    # CHANGED: Pass the db object to the CRUD function
    device = device_crud.create_device(db=db, device_in=device_in)
    logger.info(f"Device '{device.get('name')}' created successfully with ID: {device.get('_id')}")
    return device


@router.get("/", response_model=List[DeviceInDB])
def read_devices(
        skip: int = 0,
        limit: int = 100,
        current_user: dict = Depends(get_current_user),
        db: Any = Depends(get_db) # INJECTED: The synchronous DB client
):
    """Retrieve all devices with pagination (Any logged-in user)."""
    user_email = current_user.get("email")
    logger.info(f"User '{user_email}' requesting device list with skip: {skip}, limit: {limit}")
    # CHANGED: Pass the db object to the CRUD function
    devices = device_crud.get_all_devices(db=db, skip=skip, limit=limit)
    return devices


@router.get("/{device_id}", response_model=DeviceInDB)
def read_device(
        *,
        device_id: str,
        current_user: dict = Depends(get_current_user),
        db: Any = Depends(get_db) # INJECTED: The synchronous DB client
):
    """Get a single device by ID."""
    user_email = current_user.get("email")
    logger.info(f"User '{user_email}' requesting details for device ID: {device_id}")
    # CHANGED: Pass the db object to the CRUD function
    device = device_crud.get_device(db=db, device_id=device_id)
    if not device:
        logger.warning(f"Device not found for ID: {device_id}, requested by {user_email}")
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.put("/{device_id}", response_model=DeviceInDB)
def update_device(
        *,
        device_id: str,
        device_in: DeviceUpdate,
        current_user: dict = Depends(get_current_admin_user),
        db: Any = Depends(get_db) # INJECTED: The synchronous DB client
):
    """Update a device (Admin only)."""
    admin_email = current_user.get("email")
    logger.info(f"Admin '{admin_email}' attempting to update device ID: {device_id}")
    # CHANGED: Pass the db object to the CRUD function
    device = device_crud.get_device(db=db, device_id=device_id)
    if not device:
        logger.warning(f"Update failed: Device not found for ID: {device_id}, requested by {admin_email}")
        raise HTTPException(status_code=404, detail="Device not found")

    # CHANGED: Pass the db object to the CRUD function
    updated_device = device_crud.update_device(db=db, device_id=device_id, device_in=device_in)
    logger.info(f"Device '{updated_device.get('name')}' (ID: {device_id}) updated successfully by {admin_email}")
    return updated_device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
        *,
        device_id: str,
        current_user: dict = Depends(get_current_admin_user),
        db: Any = Depends(get_db) # INJECTED: The synchronous DB client
):
    """Delete a device (Admin only)."""
    admin_email = current_user.get("email")
    logger.info(f"Admin '{admin_email}' attempting to delete device ID: {device_id}")
    # CHANGED: Pass the db object to the CRUD function
    device = device_crud.get_device(db=db, device_id=device_id)
    if not device:
        logger.warning(f"Delete failed: Device not found for ID: {device_id}, requested by {admin_email}")
        raise HTTPException(status_code=404, detail="Device not found")

    # CHANGED: Pass the db object to the CRUD function
    if not device_crud.delete_device(db=db, device_id=device_id):
        logger.error(f"Delete failed unexpectedly for device ID: {device_id}, requested by {admin_email}")
        raise HTTPException(status_code=500, detail="Device could not be deleted")

    logger.info(f"Device (ID: {device_id}) deleted successfully by {admin_email}")
    return