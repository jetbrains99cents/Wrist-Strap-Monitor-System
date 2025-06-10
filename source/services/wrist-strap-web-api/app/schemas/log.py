from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any, List
from .pyobjectid import PyObjectId
from datetime import datetime, timezone
import time

class LogPayload(BaseModel):
    type: str = Field(..., example="Connection")
    status: Optional[str] = Field(None, example="Connected")
    value: Any = Field(..., example="Signal strength: -55dBm")

class LogBase(BaseModel):
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))
    device_id: str = Field(..., example="684658b628265598a9f721a9")
    device_name: str = Field(..., example="Device 1")
    mac_address: str = Field(..., example="AA:BB:CC:DD:EE:FF")
    installation_area: str = Field(..., example="POL")
    event: LogPayload

class LogCreate(LogBase):
    pass

class LogInDB(LogBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# NEW: Pydantic Model for Frontend API Response (HistoricalLog)
class HistoricalLogResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the log entry (MongoDB _id converted to string).")
    timestamp: str = Field(..., description="Timestamp of the log entry in ISO 8601 format (UTC).")
    deviceId: str = Field(..., description="ID of the device.")
    deviceName: str = Field(..., description="Name of the device.")
    deviceMacAddress: str = Field(..., description="MAC address of the device.")
    area: str = Field(..., description="Installation area of the device.")
    eventType: str = Field(..., description="Category of the event.")
    status: Optional[str] = Field(None, description="Status related to the event.")
    messageSummary: str = Field("Log entry details available in payload.", description="A brief summary of the log message (placeholder).")
    fullPayload: dict = Field(..., description="The full, original payload of the log entry, or relevant parts.")

    @model_validator(mode='before')
    @classmethod
    def populate_fields(cls, data: Any):
        if isinstance(data, dict):
            if '_id' in data:
                data['id'] = str(data['_id'])
            if 'timestamp' in data and isinstance(data['timestamp'], int):
                try:
                    dt_object = datetime.fromtimestamp(data['timestamp'] / 1000, tz=timezone.utc)
                    iso_timestamp = dt_object.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                    data['timestamp'] = iso_timestamp
                except Exception as e:
                    print(f"Warning: Could not convert timestamp {data['timestamp']}. Error: {e}")
                    data['timestamp'] = str(data['timestamp'])
            if 'event' in data and isinstance(data['event'], dict):
                data['eventType'] = data['event'].get('type')
                data['status'] = data['event'].get('status')
            data['fullPayload'] = {
                "created_at": data.get('timestamp'),
                "device_name": data.get('device_name'),
                "mac_address": data.get('mac_address'),
                "event": data.get('event', {})
            }
            data['deviceId'] = data.get('device_id')
            data['deviceName'] = data.get('device_name')
            data['deviceMacAddress'] = data.get('mac_address')
            data['area'] = data.get('installation_area')
        return data

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# NEW: Response model for the paginated list of logs (matches combined API call)
class PaginatedLogsResponse(BaseModel):
    items: List[HistoricalLogResponse] = Field(..., description="List of historical log entries for the current page.")
    total_count: int = Field(..., description="Total number of log entries matching the applied filters across all pages.")