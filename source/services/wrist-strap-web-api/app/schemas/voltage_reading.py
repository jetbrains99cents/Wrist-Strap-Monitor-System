from pydantic import BaseModel, Field, ValidationError
# FIXED: Added Dict to typing imports
from typing import Literal, Optional, Any, List, Dict
from app.schemas.pyobjectid import PyObjectId  # Assuming you have this for ObjectId handling


# --- NEW: Nested Schema for LastEventDetails (matches frontend's EventDetails) ---
class EventDetails(BaseModel):
    type: Literal["Connection", "Sensor Reading", "Alert", "User action", "System"]
    status: Optional[Literal[
        "Connected",
        "Disconnected",
        "Voltage reading ok",
        "Voltage reading failed",
        "Info",
        "Warning",
        "Error",
        "Critical",
        "Configured",
        "Reset"
    ]] = None  # Optional status
    timestamp: int  # Unix timestamp in milliseconds
    value: Any  # Can be string, number, or object, to represent sensor value, error message, etc.


# --- Schema for raw incoming device data (from MQTT) ---
class DeviceReadingIn(BaseModel):
    mac_address: str = Field(..., description="The MAC address of the ESP32 device.")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds when the reading occurred on the device.")
    voltage_value: float = Field(..., description="The raw voltage reading from the device.")

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "timestamp": 1718886400000,
                "voltage_value": 3.25
            }
        }


# --- Schema for the COMPLETE DOCUMENT TO BE SAVED to MongoDB (Voltage Readings Collection) ---
class VoltageReadingCreate(BaseModel):
    device_id: PyObjectId = Field(..., description="The native _id of the device from the 'devices' collection.")
    area: str = Field(..., description="Denormalized installation area for high-performance filtering.")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds when the reading occurred.")
    voltage: float = Field(..., description="The voltage reading.")
    status: Literal["Voltage reading ok", "Voltage reading failed"] = Field(
        ...,
        description="Operational status based on voltage reading: 'Voltage reading ok' or 'Voltage reading failed'."
    )

    class Config:
        json_encoders = {PyObjectId: str}
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "device_id": "60c728e20b33b0001c8a0a1a",
                "area": "Main_Lab",
                "timestamp": 1718886400000,
                "voltage": 3.25,
                "status": "Voltage reading ok"
            }
        }


class VoltageReadingInDB(VoltageReadingCreate):
    id: PyObjectId = Field(alias="_id", description="MongoDB's ObjectId for the reading.")

    class Config(VoltageReadingCreate.Config):
        extra = "allow"


# --- NEW SCHEMA: For the Rich WebSocket Payload sent from Backend to Frontend ---
class RealtimeDeviceStatusMessage(BaseModel):
    """
    Represents a comprehensive real-time status update for a device,
    sent via WebSocket from backend to frontend.
    Combines latest reading with essential device metadata.
    """
    id: PyObjectId = Field(..., alias="_id", description="MongoDB _id of the device.")  # Device ID
    name: str
    mac_address: str
    device_type: str
    installation_area: str
    firmware_version: Optional[str] = None
    # Assuming coordinates is a dict like {row: int, col: int}
    coordinates: Optional[Dict[str, int]] = None

    # New: Replicate the 'last_event' structure from DeviceData
    last_event: EventDetails  # Use the EventDetails schema defined above

    class Config:
        populate_by_name = True  # Allow mapping _id to id, etc.
        json_encoders = {PyObjectId: str}  # Ensure ObjectId converts to string for JSON output
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "60c728e20b33b0001c8a0a1a",
                "name": "My Wrist Strap",
                "mac_address": "AA:BB:CC:DD:EE:FF",
                "device_type": "WristStrapMonitorV1",
                "installation_area": "Assembly Line 1",
                "firmware_version": "1.0.0",
                "coordinates": {"row": 5, "col": 10},
                "last_event": {
                    "type": "Sensor Reading",
                    "status": "Voltage reading ok",
                    "timestamp": 1718886400000,
                    "value": 3.25
                }
            }
        }