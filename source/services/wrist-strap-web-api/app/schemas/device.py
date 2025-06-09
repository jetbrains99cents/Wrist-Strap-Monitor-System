# File: app/schemas/device.py

from pydantic import BaseModel, Field
from typing import Optional, List
from .pyobjectid import PyObjectId


class Coordinates(BaseModel):
    row: int
    col: int


class DeviceBase(BaseModel):
    name: str = Field(..., example="FLW Line 2 Sensor")
    mac_address: str = Field(..., example="00:1A:2B:3C:4D:5E")
    device_type: str = Field(..., example="WristStrapMonitorV1")
    installation_area: str = Field(..., example="FLW")

    # --- MODIFIED LINE ---
    # Made 'coordinates' optional to allow device creation without it.
    coordinates: Optional[Coordinates] = Field(None, example={"row": 10, "col": 5})

    firmware_version: Optional[str] = Field(None, example="1.2.3")


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    installation_area: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    firmware_version: Optional[str] = None


class DeviceInDB(DeviceBase):
    id: PyObjectId = Field(..., alias="_id")
    installation_date: int
    last_event: Optional[dict] = None
    createdAt: int
    updatedAt: int

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True