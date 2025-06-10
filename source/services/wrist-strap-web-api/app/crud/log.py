from app.db.session import historical_logs
from app.schemas.log import LogCreate
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import pymongo.database


def create_log(db: pymongo.database.Database, log_in: LogCreate):
    historical_logs_collection = db.get_collection("historical_logs")
    new_log_doc = log_in.model_dump()
    result = historical_logs_collection.insert_one(new_log_doc)
    created_log = historical_logs_collection.find_one({"_id": result.inserted_id})
    return created_log


def get_multi_logs(
        db: pymongo.database.Database,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "timestamp",
        sort_direction: str = "desc"
) -> Tuple[List[Dict[str, Any]], int]:
    historical_logs_collection = db.get_collection("historical_logs")
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
            {"installation_area": {"$regex": search_term, "$options": "i"}},
            {"event.type": {"$regex": search_term, "$options": "i"}},
            {"event.status": {"$regex": search_term, "$options": "i"}},
        ]

    total_count = historical_logs_collection.count_documents(query)

    sort_order = 1 if sort_direction == "asc" else -1
    mongo_sort_field_map = {
        "timestamp": "timestamp",
        "deviceName": "device_name",
        "deviceMacAddress": "mac_address",
        "area": "installation_area",
        "eventType": "event.type",
        "status": "event.status",
    }
    mongo_sort_by_field = mongo_sort_field_map.get(sort_by, "timestamp")

    logs_cursor = historical_logs_collection.find(query) \
        .sort(mongo_sort_by_field, sort_order) \
        .skip(skip) \
        .limit(limit)

    logs_list = list(logs_cursor)

    return logs_list, total_count


# NEW: Function to get all filtered logs without pagination
def get_all_filtered_logs(
        db: pymongo.database.Database,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_by: str = "timestamp",
        sort_direction: str = "desc"
) -> List[Dict[str, Any]]:  # Returns just the list of logs
    historical_logs_collection = db.get_collection("historical_logs")
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
            {"installation_area": {"$regex": search_term, "$options": "i"}},
            {"event.type": {"$regex": search_term, "$options": "i"}},
            {"event.status": {"$regex": search_term, "$options": "i"}},
        ]

    sort_order = 1 if sort_direction == "asc" else -1
    mongo_sort_field_map = {
        "timestamp": "timestamp",
        "deviceName": "device_name",
        "deviceMacAddress": "mac_address",
        "area": "installation_area",
        "eventType": "event.type",
        "status": "event.status",
    }
    mongo_sort_by_field = mongo_sort_field_map.get(sort_by, "timestamp")

    # Fetch all matching logs, applying filters and sort, but no skip/limit
    logs_cursor = historical_logs_collection.find(query).sort(mongo_sort_by_field, sort_order)

    return list(logs_cursor)  # Return as list