import logging
import pymongo.database
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
from collections import defaultdict

logger = logging.getLogger(__name__)


# --- Helper Function to Parse Date Ranges ---
def _get_date_range_timestamps(date_range_str: str) -> Dict[str, int]:
    """Converts a string like '7days' into a MongoDB timestamp query."""
    now = datetime.now(timezone.utc)
    start_date = None

    if date_range_str == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_range_str == '7days':
        start_date = now - timedelta(days=7)
    elif date_range_str == '30days':
        start_date = now - timedelta(days=30)
    elif date_range_str == 'all':
        return {}

    if start_date:
        return {
            "$gte": int(start_date.timestamp() * 1000),
            "$lte": int(now.timestamp() * 1000)
        }
    return {}


# --- Main Analytics Function ---
def get_analytics_data(
        db: pymongo.database.Database,
        metric: str,
        date_range: str,
        area: Optional[str]
) -> Dict[str, Any]:
    """
    Main function to fetch data for a specific metric.
    """
    logger.info(
        f"Processing analytics data for metric: '{metric}', date_range: '{date_range}', area: '{area or 'all'}'")

    time_filter = _get_date_range_timestamps(date_range)
    base_match_query: Dict[str, Any] = {}
    if time_filter:
        # Use 'timestamp' for historical_logs and voltage_readings
        base_match_query["timestamp"] = time_filter
    if area:
        # This key will be mapped to 'installation_area' or 'area' depending on the collection
        base_match_query["area"] = area

    logger.info(f"Constructed base match query: {base_match_query}")

    # Key metrics are calculated regardless of the selected chart
    key_metrics = _calculate_key_metrics(db, base_match_query)

    chart_data: Dict[str, Any] = {"labels": [], "datasets": []}

    # --- MODIFICATION: Updated the function router ---
    query_functions = {
        "deviceDistribution": _get_device_distribution,
        "deviceStatusOverview": _get_device_status_overview,
        "deviceStatusTrends": _get_device_status_trends,  # New function for the stacked area chart
        "alertFrequencies": _get_alert_frequencies,
        "voltageReadings": _get_voltage_readings,
    }

    if metric in query_functions:
        chart_data = query_functions[metric](db, base_match_query, date_range)
    else:
        logger.warning(f"Unknown analytics metric requested: '{metric}'")

    return {"keyMetrics": key_metrics, "chartData": chart_data}


# --- Internal Helper Functions for Specific Metrics ---

def _calculate_key_metrics(db: pymongo.database.Database, base_match_query: dict) -> dict:
    logger.info("Calculating key metrics...")
    historical_logs_collection = db.get_collection("historical_logs")
    devices_collection = db.get_collection("devices")
    voltage_readings_collection = db.get_collection("voltage_readings")

    # To calculate metrics for a specific area, we need to adapt the query
    area_filter = {"installation_area": base_match_query["area"]} if "area" in base_match_query else {}

    # Active devices based on logs within the date/area range
    active_devices_list = historical_logs_collection.distinct("device_id", base_match_query)
    active_devices = len(active_devices_list)

    # Total alerts from historical logs
    alert_query = {**base_match_query, "event.type": "Alert"}
    total_alerts = historical_logs_collection.count_documents(alert_query)

    # Average Voltage from voltage_readings
    voltage_pipeline = [
        {"$match": base_match_query},
        {"$group": {"_id": None, "avgVoltage": {"$avg": "$voltage"}}}
    ]
    voltage_result = list(voltage_readings_collection.aggregate(voltage_pipeline))
    avg_from_db = voltage_result[0]['avgVoltage'] if voltage_result and 'avgVoltage' in voltage_result[0] else 0.0

    # Uptime calculation based on the LATEST status of devices that were active in the period
    total_devices_in_filter = devices_collection.count_documents(area_filter)
    if total_devices_in_filter == 0:
        uptime_percentage = 0.0
    else:
        # Find the last status for all devices matching the area filter
        pipeline = [
            {"$match": area_filter},
            {"$lookup": {
                "from": "historical_logs",
                "let": {"deviceIdStr": {"$toString": "$_id"}},
                "pipeline": [
                    {"$match": {"$expr": {"$eq": ["$device_id", "$$deviceIdStr"]}}},
                    {"$sort": {"timestamp": -1}},
                    {"$limit": 1}
                ],
                "as": "last_log"
            }},
            {"$unwind": {"path": "$last_log", "preserveNullAndEmptyArrays": True}},
            {"$group": {
                "_id": "$last_log.event.status",
                "count": {"$sum": 1}
            }}
        ]
        status_counts = {item['_id']: item['count'] for item in db.devices.aggregate(pipeline)}
        connected_count = status_counts.get("Connected", 0) + status_counts.get("Voltage reading ok", 0)
        uptime_percentage = (connected_count / total_devices_in_filter) * 100

    return {
        "activeDevices": active_devices,
        "totalAlerts": total_alerts,
        "averageVoltage": round(avg_from_db, 2),
        "uptimePercentage": round(uptime_percentage, 1)
    }


def _get_device_distribution(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating device distribution...")
    devices_collection = db.get_collection("devices")
    match_query = {}
    if "area" in base_match_query:
        match_query["installation_area"] = base_match_query["area"]

    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": "$installation_area", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    results = list(devices_collection.aggregate(pipeline))
    labels = [r["_id"] for r in results]
    data = [r["count"] for r in results]
    return {"labels": labels, "datasets": [{"label": "Device Count", "data": data}]}


def _get_device_status_overview(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating device status overview...")
    historical_logs_collection = db.get_collection("historical_logs")
    pipeline = [
        {"$match": base_match_query},
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$device_id", "last_status": {"$first": "$event.status"}}},
        {"$group": {"_id": "$last_status", "count": {"$sum": 1}}}
    ]
    results = list(historical_logs_collection.aggregate(pipeline))
    labels = [r["_id"] for r in results if r["_id"]]
    data = [r["count"] for r in results if r["_id"]]
    return {"labels": labels, "datasets": [{"label": "Device Status", "data": data}]}


# --- MODIFICATION: New function for the stacked area chart ---
def _get_device_status_trends(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating device status trends...")
    historical_logs_collection = db.get_collection("historical_logs")

    group_id_format = "%Y-%m-%d"
    if date_range == 'today':
        group_id_format = "%Y-%m-%d %H:00"

    # This is a complex pipeline to get the count of devices in each state for each time bucket.
    pipeline = [
        {"$match": base_match_query},
        {"$sort": {"timestamp": 1}},
        # Group by device and time bucket to find the last status in that bucket
        {"$group": {
            "_id": {
                "date": {"$dateToString": {"format": group_id_format, "date": {"$toDate": "$timestamp"}}},
                "device_id": "$device_id"
            },
            "last_status": {"$last": "$event.status"}
        }},
        # Group again by date and status to count devices
        {"$group": {
            "_id": {
                "date": "$_id.date",
                "status": "$last_status"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.date": 1}},
    ]

    results = list(historical_logs_collection.aggregate(pipeline))

    # Post-process the data in Python to format it for Chart.js
    if not results:
        return {"labels": [], "datasets": []}

    # Get all unique dates and statuses to build the final structure
    all_dates = sorted(list(set(r["_id"]["date"] for r in results)))
    all_statuses = sorted(list(set(r["_id"]["status"] for r in results if r["_id"]["status"])))

    # Create a lookup table for quick access
    data_lookup = defaultdict(lambda: defaultdict(int))
    for r in results:
        if r["_id"]["status"]:
            data_lookup[r["_id"]["date"]][r["_id"]["status"]] = r["count"]

    # Build the datasets array
    datasets = []
    for status in all_statuses:
        dataset = {
            "label": status,
            "data": [data_lookup[date].get(status, 0) for date in all_dates]
        }
        datasets.append(dataset)

    return {"labels": all_dates, "datasets": datasets}


def _get_alert_frequencies(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating alert frequencies...")
    historical_logs_collection = db.get_collection("historical_logs")
    match_query = {**base_match_query, "event.type": "Alert"}

    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": "$event.status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = list(historical_logs_collection.aggregate(pipeline))
    labels = [r["_id"] for r in results if r["_id"]]
    data = [r["count"] for r in results if r["_id"]]
    return {"labels": labels, "datasets": [{"label": "Alerts", "data": data}]}


def _get_voltage_readings(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating voltage readings...")
    voltage_readings_collection = db.get_collection("voltage_readings")

    group_id_format = "%Y-%m-%d"
    if date_range == 'today':
        group_id_format = "%Y-%m-%d %H:00"

    pipeline = [
        {"$match": base_match_query},
        {"$group": {
            "_id": {"$dateToString": {"format": group_id_format, "date": {"$toDate": "$timestamp"}}},
            "value": {"$avg": "$voltage"}
        }},
        {"$sort": {"_id": 1}}
    ]
    results = list(voltage_readings_collection.aggregate(pipeline))
    labels = [r["_id"] for r in results]
    data = [round(r["value"], 2) if r.get("value") is not None else 0 for r in results]
    return {"labels": labels, "datasets": [{"label": "Average Voltage", "data": data}]}