import logging
import pymongo.database
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone

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
        # Use 'area' field in query, assuming it's consistent in voltage_readings
        # For devices collection, it might be 'installation_area'
        base_match_query["area"] = area


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
    historical_logs_collection = db.get_collection("historical_logs")
    devices_collection = db.get_collection("devices")
    voltage_readings_collection = db.get_collection("voltage_readings") # Get voltage readings collection

    # Active devices from historical logs (events)
    active_devices_list = historical_logs_collection.distinct("device_id", base_match_query)
    active_devices = len(active_devices_list)

    # Total alerts from historical logs
    alert_query = {**base_match_query, "event.type": "Alert"}
    total_alerts = historical_logs_collection.count_documents(alert_query)

    # Average Voltage from voltage_readings_collection
    # Use base_match_query for timestamp/area filters directly on voltage_readings
    voltage_pipeline = [
        {"$match": base_match_query},
        {"$group": {"_id": None, "avgVoltage": {"$avg": "$voltage"}}} # Use $voltage field from voltage_readings
    ]
    voltage_result = list(voltage_readings_collection.aggregate(voltage_pipeline))
    avg_from_db = voltage_result[0]['avgVoltage'] if voltage_result and 'avgVoltage' in voltage_result[0] else None
    average_voltage = avg_from_db if avg_from_db is not None else 0.0

    # Total devices from devices collection
    total_devices = devices_collection.count_documents({})

    # Uptime calculation: connected devices from voltage_readings
    if total_devices == 0:
        uptime_percentage = 0.0
    else:
        connected_devices_pipeline = [
            {"$match": base_match_query}, # Apply general date/area filters
            {"$sort": {"timestamp": -1}},
            {"$group": {"_id": "$device_id", "lastStatus": {"$first": "$status"}}}, # Use '$status' from voltage_readings
            {"$match": {"lastStatus": "Voltage reading ok"}} # Using new status naming
        ]
        connected_count = len(list(voltage_readings_collection.aggregate(connected_devices_pipeline))) # Query voltage_readings_collection
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
    if "area" in base_match_query: # Check for 'area' key in query, which might be 'installation_area' in devices
        match_query["installation_area"] = base_match_query["area"] # Match 'area' from query with 'installation_area' in DB

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
    # This should query voltage_readings for latest status
    voltage_readings_collection = db.get_collection("voltage_readings")
    pipeline = [
        {"$match": base_match_query}, # Will match on timestamp/area
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$device_id", "last_status": {"$first": "$status"}}}, # Use '$status' from voltage_readings
        {"$group": {"_id": "$last_status", "count": {"$sum": 1}}}
    ]
    results = list(voltage_readings_collection.aggregate(pipeline))

    labels = [r["_id"] for r in results if r["_id"]]
    data = [r["count"] for r in results if r["_id"]]

    return {"labels": labels, "datasets": [{"label": "Device Status", "data": data}]}


def _get_connection_status_timeline(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating connection status timeline...")
    # This should query voltage_readings for 'Voltage reading ok' status over time
    return _get_grouped_time_series_data(db, base_match_query, date_range, "Voltage reading ok", "Connection Events", collection_name="voltage_readings") # Use new status and collection

def _get_alert_frequencies(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating alert frequencies...")
    # Assuming 'Alert's are still logged in 'historical_logs'
    return _get_grouped_time_series_data(db, base_match_query, date_range, "Alert", "Alerts", collection_name="historical_logs")


def _get_voltage_readings(db: pymongo.database.Database, base_match_query: dict, date_range: str) -> dict:
    logger.info("Calculating voltage readings...")
    voltage_readings_collection = db.get_collection("voltage_readings")

    match_query = {**base_match_query} # Use base_match_query for timestamp/area filters

    group_id_format = "%Y-%m-%d"
    if date_range == 'today':
        group_id_format = "%Y-%m-%d %H:00"

    pipeline = [
        {"$match": match_query},
        {"$group": {
            "_id": {"$dateToString": {"format": group_id_format, "date": {"$toDate": {"$convert": {"input": "$timestamp", "to": "date"}}}}}, # Corrected $toDate input
            "value": {"$avg": "$voltage"}
        }},
        {"$sort": {"_id": 1}}
    ]
    results = list(voltage_readings_collection.aggregate(pipeline))

    labels = [r["_id"] for r in results]
    data = [round(r["value"], 2) if r.get("value") is not None else 0 for r in results]

    return {"labels": labels, "datasets": [{"label": "Average Voltage", "data": data}]}


# CHANGED: Add 'db' as the first parameter and optional collection_name
def _get_grouped_time_series_data(
        db: pymongo.database.Database, # Accept db parameter
        base_match_query: dict, date_range: str, event_type: str,
        label: str, aggregate_type: str = "count", collection_name: str = "historical_logs" # Default to historical_logs
) -> dict:
    logger.info(f"Calculating grouped time series for event_type: '{event_type}', aggregate: '{aggregate_type}'")

    target_collection = db.get_collection(collection_name)

    match_query = {**base_match_query}
    # Add specific event type filter IF it's relevant for the target collection
    if collection_name == "historical_logs":
        match_query["event.type"] = event_type
        if aggregate_type == "avg":
            match_query["event.value"] = {"$type": "number"}
    elif collection_name == "voltage_readings":
        # For voltage_readings, 'event_type' might correspond to 'status' field, not 'event.type'
        # And the field for average is 'voltage', not 'event.value'
        if event_type: # Assuming event_type here is for 'status'
            match_query["status"] = event_type


    group_id_format = "%Y-%m-%d"
    if date_range == 'today':
        group_id_format = "%Y-%m-%d %H:00"

    # Adjust group operator based on collection and aggregate type
    group_operator = {"$sum": 1} # Default for count
    if aggregate_type == "avg":
        if collection_name == "historical_logs":
            group_operator = {"$avg": "$event.value"}
        elif collection_name == "voltage_readings":
            group_operator = {"$avg": "$voltage"} # Use $voltage for voltage_readings

    pipeline = [
        {"$match": match_query},
        {"$group": {"_id": {"$dateToString": {"format": group_id_format, "date": {"$toDate": {"$convert": {"input": "$timestamp", "to": "date"}}}}},
                    "value": group_operator}},
        {"$sort": {"_id": 1}}
    ]
    results = list(target_collection.aggregate(pipeline))
    labels = [r["_id"] for r in results]
    data = [round(r["value"], 2) if isinstance(r["value"], float) else r["value"] for r in results]
    return {"labels": labels, "datasets": [{"label": label, "data": data}]}