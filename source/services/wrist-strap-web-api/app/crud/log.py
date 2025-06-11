# File: app/crud/log.py

import logging
from app.schemas.log import LogCreate
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import pymongo.database

# Get a logger instance for this file
logger = logging.getLogger(__name__)


def create_log(db: pymongo.database.Database, log_in: LogCreate):
    """Creates a new historical log document."""
    historical_logs_collection = db.get_collection("historical_logs")
    new_log_doc = log_in.model_dump()
    # No need to log here as this will be called very frequently and create too much noise.
    # Logging for new events is better handled at a higher level if needed.
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
    """Retrieves multiple historical logs with filtering, sorting, and pagination."""
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

    logger.info(f"Querying historical_logs with filter: {query}, skip: {skip}, limit: {limit}")
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
    logger.info(f"Found {total_count} total logs, returning {len(logs_list)} logs.")
    return logs_list, total_count


def get_all_filtered_logs(
        db: pymongo.database.Database,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        sort_by: str = "timestamp",
        sort_direction: str = "desc"
) -> List[Dict[str, Any]]:
    """Retrieves all historical logs that match filters, without pagination (for export)."""
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

    logger.info(f"Exporting historical_logs with filter: {query}")
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

    logs_cursor = historical_logs_collection.find(query).sort(mongo_sort_by_field, sort_order)

    logs_list = list(logs_cursor)
    logger.info(f"Returning {len(logs_list)} logs for export.")
    return logs_list