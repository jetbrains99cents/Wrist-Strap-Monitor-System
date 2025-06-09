from pydantic import BaseModel, Field
from typing import Optional, Any
from .pyobjectid import PyObjectId
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