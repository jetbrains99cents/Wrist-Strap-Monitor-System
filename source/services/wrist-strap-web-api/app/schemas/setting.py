from pydantic import BaseModel, Field, model_validator, ValidationError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from bson import ObjectId


# Helper functions for 12-hour AM/PM to 24-hour and vice-versa
def convert_to_24hr(hour_12hr: str, minute: str, period: str) -> Dict[str, int]:
    h = int(hour_12hr)
    m = int(minute)
    if period == "PM" and h != 12:
        h += 12
    elif period == "AM" and h == 12:  # 12 AM (midnight) is 00 in 24-hour
        h = 0
    return {"hour": h, "minute": m}


def convert_to_12hr(hour_24hr: int, minute: int) -> Dict[str, str]:
    period = "AM"
    display_hour = hour_24hr

    if hour_24hr >= 12:
        period = "PM"
    if hour_24hr > 12:
        display_hour -= 12
    elif display_hour == 0:  # 00:XX is 12 AM
        display_hour = 12

    return {"hour": str(display_hour).zfill(2), "minute": str(minute).zfill(2), "period": period}


# REINSTATED: Represents time in 24-hour format for DB storage as a nested object
class TimeSettingInternal(BaseModel):
    hour: int = Field(..., ge=0, le=23)
    minute: int = Field(..., ge=0, le=59)


# MODIFIED: WorkingTimeSettingDB now uses nested TimeSettingInternal objects
class WorkingTimeSettingDB(BaseModel):
    name: str = Field(..., description="Name of the working time shift (e.g., 'Shift 1').")
    from_time: TimeSettingInternal  # Changed to nested object
    to_time: TimeSettingInternal  # Changed to nested object


# MODIFIED: ProductionPlanSettingDB now uses nested TimeSettingInternal objects
class ProductionPlanSettingDB(BaseModel):
    name: str = Field(..., description="Name of the production plan shift (e.g., 'Morning Shift').")
    date: Optional[str] = Field(None, description="Date of the production plan shift in Jamboree-MM-DD format.")
    from_time: TimeSettingInternal  # Changed to nested object
    to_time: TimeSettingInternal  # Changed to nested object


# SystemSettingsBase remains the same, its components now use nested TimeSettingInternal
class SystemSettingsBase(BaseModel):
    workingTime: List[WorkingTimeSettingDB]
    productionPlan: List[ProductionPlanSettingDB]


# SystemSettingsCreateUpdate (Input from Frontend) - Its validator now builds nested objects
class SystemSettingsCreateUpdate(BaseModel):
    workingTime: List[Dict[str, Any]]  # Raw dicts from frontend
    productionPlan: List[Dict[str, Any]]  # Raw dicts from frontend

    @model_validator(mode='before')
    @classmethod
    def convert_frontend_times_to_24hr_internal(cls, data: Any):
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")

        if 'workingTime' in data and isinstance(data['workingTime'], list):
            converted_working_time = []
            for shift_raw in data['workingTime']:
                if not isinstance(shift_raw,
                                  dict) or 'name' not in shift_raw or 'from' not in shift_raw or 'to' not in shift_raw:
                    raise ValueError("Each workingTime shift must be a dict with 'name', 'from', 'to'")

                from_24_data = convert_to_24hr(shift_raw['from']['hour'], shift_raw['from']['minute'],
                                               shift_raw['from']['period'])
                to_24_data = convert_to_24hr(shift_raw['to']['hour'], shift_raw['to']['minute'],
                                             shift_raw['to']['period'])

                converted_working_time.append({
                    "name": shift_raw['name'],
                    "from_time": from_24_data,
                    "to_time": to_24_data
                })
            data['workingTime'] = converted_working_time

        if 'productionPlan' in data and isinstance(data['productionPlan'], list):
            converted_production_plan = []
            for shift_raw in data['productionPlan']:
                if not isinstance(shift_raw,
                                  dict) or 'name' not in shift_raw or 'from' not in shift_raw or 'to' not in shift_raw:
                    raise ValueError("Each productionPlan shift must be a dict with 'name', 'from', 'to'")

                from_24_data = convert_to_24hr(shift_raw['from']['hour'], shift_raw['from']['minute'],
                                               shift_raw['from']['period'])
                to_24_data = convert_to_24hr(shift_raw['to']['hour'], shift_raw['to']['minute'],
                                             shift_raw['to']['period'])

                converted_production_plan.append({
                    "name": shift_raw['name'],
                    "date": shift_raw.get('date'),
                    "from_time": from_24_data,
                    "to_time": to_24_data
                })
            data['productionPlan'] = converted_production_plan
        return data


# SystemSettingsResponse (Output to Frontend) - Its validator now expects nested objects
class SystemSettingsResponse(BaseModel):
    id: str = Field(..., alias="_id", description="Unique identifier for the settings document.")
    workingTime: List[Dict[str, Any]]
    productionPlan: List[Dict[str, Any]]
    createdAt: Optional[int] = Field(None)
    updatedAt: Optional[int] = Field(None)

    @model_validator(mode='before')
    @classmethod
    def convert_backend_times_to_12hr_frontend(cls, data: Any):
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary")

        # Convert workingTime shifts (from nested 24hr objects to 12hr frontend format)
        if 'workingTime' in data and isinstance(data['workingTime'], list):
            converted_working_time = []
            for shift_db in data['workingTime']:
                if not isinstance(shift_db,
                                  dict) or 'name' not in shift_db or 'from_time' not in shift_db or 'to_time' not in shift_db:
                    raise ValueError("Each workingTime shift must be a dict with 'name', 'from_time', 'to_time'")

                from_12 = convert_to_12hr(shift_db['from_time']['hour'], shift_db['from_time']['minute'])
                # FIX: Corrected to access hour/minute from nested to_time object
                to_12 = convert_to_12hr(shift_db['to_time']['hour'], shift_db['to_time']['minute'])

                converted_working_time.append({
                    "name": shift_db['name'],
                    "from": from_12,
                    "to": to_12
                })
            data['workingTime'] = converted_working_time

        # Convert productionPlan shifts (from nested 24hr objects to 12hr frontend format)
        if 'productionPlan' in data and isinstance(data['productionPlan'], list):
            converted_production_plan = []
            for shift_db in data['productionPlan']:
                if not isinstance(shift_db,
                                  dict) or 'name' not in shift_db or 'from_time' not in shift_db or 'to_time' not in shift_db:
                    raise ValueError("Each productionPlan shift must be a dict with 'name', 'from_time', 'to_time'")

                from_12 = convert_to_12hr(shift_db['from_time']['hour'], shift_db['from_time']['minute'])
                # FIX: Corrected to access hour/minute from nested to_time object
                to_12 = convert_to_12hr(shift_db['to_time']['hour'], shift_db['to_time']['minute'])

                converted_production_plan.append({
                    "name": shift_db['name'],
                    "date": shift_db.get('date'),
                    "from": from_12,
                    "to": to_12
                })
            data['productionPlan'] = converted_production_plan

        if '_id' in data and isinstance(data['_id'], ObjectId):
            data['id'] = str(data['_id'])

        return data

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}