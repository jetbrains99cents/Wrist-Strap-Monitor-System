from pydantic import BaseModel, Field
from typing import Optional, Any
from .pyobjectid import PyObjectId  # Import your custom type

class Coordinates(BaseModel):
    row: int
    col: int

class LastEventDetails(BaseModel):
    type: str
    status: Optional[str] = None
    timestamp: int  # Stored as Unix ms
    value: Any

class DeviceBase(BaseModel):
    name: str = Field(..., description="Name of the device.")
    mac_address: str = Field(
        ...,
        pattern=r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
        description="Unique MAC address in XX:XX:XX:XX:XX:XX format."
    )
    device_type: str = Field(..., description="Type of the device (e.g., 'WristStrapMonitorV1').")
    installation_area: str = Field(..., description="Area where the device is installed.")
    firmware_version: str = Field(..., description="Firmware version of the device.")
    coordinates: Optional[Coordinates] = Field(None, description="Coordinates (row, col) on the map grid.")
    scale_at_creation_time: Optional[float] = Field(None, description="PDF scale at which coordinates were assigned.")
    last_event: Optional[LastEventDetails] = Field(None, description="Most recent event data for the device.")
    installation_date: int
    createdAt: int
    updatedAt: int

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class DeviceCreate(BaseModel):
    # Fields provided by the user when creating a new device
    name: str
    mac_address: str
    device_type: str
    installation_area: str
    firmware_version: str
    coordinates: Optional[Coordinates] = None
    scale_at_creation_time: Optional[float] = None
    last_event: Optional[LastEventDetails] = None

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    installation_area: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    scale_at_creation_time: Optional[float] = None
    firmware_version: Optional[str] = None

class DeviceInDB(DeviceBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        # We no longer need the complex validator. PyObjectId handles it.
        populate_by_name = True
        arbitrary_types_allowed = True