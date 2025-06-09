# File: app/api/v1/endpoints/devices.py

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.device import DeviceInDB, DeviceCreate, DeviceUpdate
from app.crud import device as device_crud
from app.security import get_current_user, get_current_admin_user

print("--- Loading devices.py endpoints ---")  # <-- ADD THIS LINE

router = APIRouter()


@router.post("/", response_model=DeviceInDB, status_code=status.HTTP_201_CREATED)
def create_device(
        *,
        device_in: DeviceCreate,
        current_user: dict = Depends(get_current_admin_user)
):
    """Create new device (Admin only)."""
    device = device_crud.create_device(device_in=device_in)
    return device


@router.get("/", response_model=List[DeviceInDB])
def read_devices(
        skip: int = 0,
        limit: int = 100,
        current_user: dict = Depends(get_current_user)
):
    """Retrieve all devices with pagination (Any logged-in user)."""
    devices = device_crud.get_all_devices(skip=skip, limit=limit)
    return devices


# --- NEW: Get a single device endpoint ---
@router.get("/{device_id}", response_model=DeviceInDB)
def read_device(
        *,
        device_id: str,
        current_user: dict = Depends(get_current_user)  # Any logged-in user can view
):
    """Get a single device by ID."""
    device = device_crud.get_device(device_id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


# --- NEW: Update a device endpoint ---
@router.put("/{device_id}", response_model=DeviceInDB)
def update_device(
        *,
        device_id: str,
        device_in: DeviceUpdate,
        current_user: dict = Depends(get_current_admin_user)  # Admin only
):
    """Update a device (Admin only)."""
    device = device_crud.get_device(device_id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    updated_device = device_crud.update_device(device_id=device_id, device_in=device_in)
    return updated_device


# --- NEW: Delete a device endpoint ---
@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
        *,
        device_id: str,
        current_user: dict = Depends(get_current_admin_user)  # Admin only
):
    """Delete a device (Admin only)."""
    device = device_crud.get_device(device_id=device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if not device_crud.delete_device(device_id=device_id):
        raise HTTPException(status_code=404, detail="Device could not be deleted")

    return