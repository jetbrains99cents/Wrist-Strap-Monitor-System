from app.db.session import historical_logs
from app.schemas.log import LogCreate
# Corrected import: removed 'timezone' as it's unused in this file
from datetime import datetime # Fix 2: Removed timezone
from typing import Optional, List, Dict, Any


# This function is not strictly needed for the read endpoint,
# but is good practice to have for when devices start creating logs.
# These functions are synchronous, as they use pymongo directly.
def create_log(log_in: LogCreate):
    new_log_doc = log_in.model_dump()
    result = historical_logs.insert_one(new_log_doc)
    created_log = historical_logs.find_one({"_id": result.inserted_id})
    return created_log


def get_multi_logs(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
) -> List[Dict[str, Any]]:
    query: Dict[str, Any] = {}

    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = int(start_date.timestamp() * 1000)
        if end_date:
            query["timestamp"]["$lte"] = int(end_date.timestamp() * 1000)

    if event_type: query["event.type"] = event_type
    if status: query["event.status"] = status

    if search_term:
        query["$or"] = [
            {"device_name": {"$regex": search_term, "$options": "i"}},
            {"mac_address": {"$regex": search_term, "$options": "i"}},
            # Fix 1: Corrected syntax for {"installation_area": ...}
            {"installation_area": {"$regex": search_term, "$options": "i"}},
            {"event.type": {"$regex": search_term, "$options": "i"}},
            {"event.status": {"$regex": search_term, "$options": "i"}},
        ]

    logs_cursor = historical_logs.find(query).sort("timestamp", -1).skip(skip).limit(limit)
    return list(logs_cursor)


def get_logs_count(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None
) -> int:
    query: Dict[str, Any] = {}

    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = int(start_date.timestamp() * 1000)
        if end_date:
            query["timestamp"]["$lte"] = int(end_date.timestamp() * 1000)
    if event_type: query["event.type"] = event_type
    if status: query["event.status"] = status
    if search_term:
        query["$or"] = [
            {"device_name": {"$regex": search_term, "$options": "i"}},
            {"mac_address": {"$regex": search_term, "$options": "i"}},
            # Fix 1: Corrected syntax for {"installation_area": ...}
            {"installation_area": {"$regex": search_term, "$options": "i"}},
            {"event.type": {"$regex": search_term, "$options": "i"}},
            {"event.status": {"$regex": search_term, "$options": "i"}},
        ]

    return historical_logs.count_documents(query)