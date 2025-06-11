# File: app/schemas/voltage_reading.py

from pydantic import BaseModel, Field

class VoltageReadingCreate(BaseModel):
    deviceId: str = Field(..., description="The ID of the device that produced the reading.")
    timestamp: int = Field(..., description="Unix timestamp in milliseconds when the reading occurred.")
    value: float = Field(..., description="The voltage value.")