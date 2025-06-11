# File: app/crud/analytics.py

import logging
import pymongo.database
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone

# Get a logger instance for this file
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
        base_match_query["timestamp"] = time_filter
    if area:
        base_match_query["installation_area"] = area

    logger.info(f"Constructed base match query: {base_match_query}")

    key_metrics = _calculate_key_metrics(db, base_match_query)

    chart_data: Dict[str, Any] = {"labels": [], "datasets": []}

    query_functions = {
        "deviceDistribution": _get_device_distribution,
        "deviceStatusOverview": _get_device_status_overview,
        "connectionStatusTimeline": _get_connection_status_timeline,
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
    historical_logs = db.get_collection("historical_logs")
    devices_collection = db.get_collection("devices")

    active_devices_list = historical_logs.distinct("device_id", base_match_query)
    active_devices = len(active_devices_list)

    alert_query = {**base_match_query, "event.type": "Alert"}
    total_alerts = historical_logs.count_documents(alert_query)

    voltage_query = {**base_match_query, "event.type": "Sensor Reading", "event.value": {"$type": "number"}}
    voltage_pipeline = [
        {"$match": voltage_query},
        {"$group": {"_id": None, "avgVoltage": {"$avg": "$event.value"}}}
    ]
    voltage_result = list(historical_logs.aggregate(voltage_pipeline))

    avg_from_db = voltage_result[0]['avgVoltage'] if voltage_result and 'avgVoltage' in voltage_result[0] else None
    average_voltage = avg_from_db if avg_from_db is not None else 0.0

    total_devices = devices_collection.count_documents({})
    if total_devices == 0:
        uptime_percentage = 0.0
    else:
        connected_devices_pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$group": {"_id": "$device_id", "lastStatus": {"$first": "$event.status"}}},
            {"$match": {"lastStatus": "Connected"}}
        ]
        connected_count = len(list(historical_logs.aggregate(connected_devices_pipeline)))
        uptime_percentage = (connected_count / total_devices) * 100 if total_devices > 0 else 0

    logger.info(
        f"Key metrics calculated: ActiveDevices={active_devices}, TotalAlerts={total_alerts}, AvgVoltage={average_voltage:.2f}, Uptime={uptime_percentage:.1f}%")
    return {
        "activeDevices": active_devices,
        "totalAlerts": total_alerts,
        "averageVoltage": round(average_voltage, 2),
        "uptimePercentage": round(uptime_percentage, 1)
    }


def _get_device_distribution(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating device distribution...")
    devices_collection = db.get_collection("devices")
    match_query = {}
    if "installation_area" in base_match_query:
        match_query["installation_area"] = base_match_query["installation_area"]

    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": "$installation_area", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    results = list(devices_collection.aggregate(pipeline))

    labels = [r["_id"] for r in results]
    data = [r["count"] for r in results]

    return {"labels": labels, "datasets": [{"label": "Devices by Area", "data": data}]}


def _get_device_status_overview(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating device status overview...")
    historical_logs = db.get_collection("historical_logs")
    pipeline = [
        {"$match": base_match_query},
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$device_id", "last_status": {"$first": "$event.status"}}},
        {"$group": {"_id": "$last_status", "count": {"$sum": 1}}}
    ]
    results = list(historical_logs.aggregate(pipeline))

    labels = [r["_id"] for r in results if r["_id"]]
    data = [r["count"] for r in results if r["_id"]]

    return {"labels": labels, "datasets": [{"label": "Device Status", "data": data}]}


def _get_connection_status_timeline(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating connection status timeline...")
    return _get_grouped_time_series_data(db, base_match_query, date_range, "Connection", "Connection Events")


def _get_alert_frequencies(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating alert frequencies...")
    return _get_grouped_time_series_data(db, base_match_query, date_range, "Alert", "Alerts")


def _get_voltage_readings(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating voltage readings...")
    voltage_readings_collection = db.get_collection("voltage_readings")

    match_query = {}
    if "timestamp" in base_match_query:
        match_query["timestamp"] = base_match_query["timestamp"]
    if "area" in base_match_query:  # Note: Your original code had "area", but the query had "installation_area". Sticking with "area" as per your code.
        match_query["area"] = base_match_query["area"]

    group_id_format = "%Y-%m-%d"
    if date_range == 'today':
        group_id_format = "%Y-%m-%d %H:00"

    pipeline = [
        {"$match": match_query},
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


def _get_grouped_time_series_data(
        db: pymongo.database.Database, base_match_query: dict, date_range: str, event_type: str,
        label: str, aggregate_type: str = "count"
) -> dict:
    logger.info(f"Calculating grouped time series for event_type: '{event_type}', aggregate: '{aggregate_type}'")
    historical_logs = db.get_collection("historical_logs")
    match_query = {**base_match_query, "event.type": event_type}
    if aggregate_type == "avg":
        match_query["event.value"] = {"$type": "number"}
    group_id_format = "%Y-%m-%d"
    if date_range == 'today':
        group_id_format = "%Y-%m-%d %H:00"
    group_operator = {"$avg": "$event.value"} if aggregate_type == "avg" else {"$sum": 1}
    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": {"$dateToString": {"format": group_id_format, "date": {"$toDate": "$timestamp"}}},
                    "value": group_operator}},
        {"$sort": {"_id": 1}}
    ]
    results = list(historical_logs.aggregate(pipeline))
    labels = [r["_id"] for r in results]
    data = [round(r["value"], 2) if isinstance(r["value"], float) else r["value"] for r in results]
    return {"labels": labels, "datasets": [{"label": label, "data": data}]}