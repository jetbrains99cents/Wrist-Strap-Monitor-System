import json
import os
from datetime import datetime, timedelta, timezone
from random import choice, randint, uniform
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv  # <-- Import the dotenv library

# --- Configuration ---
NUM_LOGS_TO_GENERATE = 5000
MAX_DAYS_BACK = 90
OUTPUT_FILENAME = "historical_logs_data.json"

# --- Load Environment Variables ---
load_dotenv()

# --- NEW: MongoDB Connection Setup from .env ---
MONGO_DETAILS_URI = os.getenv("MONGO_DETAILS")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
DEVICE_DB_NAME = os.getenv("DEVICE_DATABASE_NAME")

# --- Validate that environment variables were loaded ---
if not all([MONGO_DETAILS_URI, MONGO_USER, MONGO_PASSWORD, DEVICE_DB_NAME]):
    print("Error: One or more required database environment variables are missing.")
    print("Please check your .env file.")
    exit()

# --- Connect to MongoDB and Fetch Real Device Data ---
print("Connecting to MongoDB to fetch real device data...")
try:
    # Use the loaded credentials for authentication
    client = MongoClient(
        MONGO_DETAILS_URI,
        username=MONGO_USER,
        password=MONGO_PASSWORD
    )
    db = client[DEVICE_DB_NAME]

    # Fetch all devices to be used in log generation
    devices_from_db = list(db.devices.find({}))
    REAL_DEVICE_DATA = [
        {
            "id": str(d["_id"]),
            "name": d["name"],
            "mac": d["mac_address"],
            "area": d["installation_area"]
        } for d in devices_from_db
    ]
    client.close()
    if not REAL_DEVICE_DATA:
        raise Exception("No devices found in the database. Please add devices before generating logs.")
    print(f"Successfully fetched {len(REAL_DEVICE_DATA)} devices from the database.")
except Exception as e:
    print(f"Error connecting to MongoDB or fetching devices: {e}")
    exit()

# --- Data for Variation ---
EVENT_TYPES = ["Connection", "Sensor Reading", "Alert", "User action", "System"]


def generate_single_log(current_datetime: datetime) -> dict:
    """Generates a single log document using REAL device data."""
    device = choice(REAL_DEVICE_DATA)
    event_type = choice(EVENT_TYPES)

    event_status = None
    event_value = "Generic log message."

    if event_type == "Connection":
        event_status = choice(["Connected", "Disconnected"])
        event_value = f"Device status changed to {event_status}."

    elif event_type == "Sensor Reading":
        event_status = "Info"
        event_value = round(uniform(2.9, 3.4), 2)

    elif event_type == "Alert":
        event_status = choice(["Warning", "Error", "Critical"])
        event_value = choice(["High temperature alert", "Component failure detected", "Device offline"])
    elif event_type == "User action":
        event_status = choice(["Configured", "Reset"])
        event_value = "Device settings updated by admin."
    elif event_type == "System":
        event_status = "Info"
        event_value = "System firmware check complete."

    log_doc = {
        "device_id": device["id"],
        "device_name": device["name"],
        "mac_address": device["mac"],
        "installation_area": device["area"],
        "timestamp": int(current_datetime.timestamp() * 1000),
        "event": {
            "type": event_type,
            "status": event_status,
            "value": event_value
        }
    }
    return log_doc


# --- Main Script Execution ---
if __name__ == "__main__":
    print(f"Starting log generation for {NUM_LOGS_TO_GENERATE} logs...")

    latest_timestamp = datetime.now(timezone.utc)
    logs_to_output = []
    current_log_time = latest_timestamp

    for i in range(NUM_LOGS_TO_GENERATE):
        interval_seconds = randint(10, 3600)
        current_log_time -= timedelta(seconds=interval_seconds)

        if (latest_timestamp - current_log_time).days > MAX_DAYS_BACK:
            print(f"Reached max history of {MAX_DAYS_BACK} days. Stopping generation.")
            break

        log_doc = generate_single_log(current_log_time)
        logs_to_output.append(log_doc)

    logs_to_output.reverse()

    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(logs_to_output, f, ensure_ascii=False, indent=2)
        print(f"Successfully generated {len(logs_to_output)} log documents to '{OUTPUT_FILENAME}'.")
        print("You can now import this file into your 'historical_logs' collection.")
    except Exception as e:
        print(f"Error writing to JSON file: {e}")