import json
import os
from datetime import datetime, timedelta, timezone
from random import choice, randint, uniform
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
import argparse  # --- MODIFICATION: Added for command-line arguments

# --- Configuration ---
NUM_LOGS_TO_GENERATE = 5000
OUTPUT_FILENAME = "historical_logs_data_june_2025.json"

# --- MODIFICATION: Define the specific date range for June 2025 ---
START_DATE = datetime(2025, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
END_DATE = datetime(2025, 6, 30, 23, 59, 59, tzinfo=timezone.utc)
TOTAL_SECONDS_IN_RANGE = (END_DATE - START_DATE).total_seconds()

# --- Load Environment Variables ---
load_dotenv()
MONGO_DETAILS_URI = os.getenv("MONGO_DETAILS")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
DEVICE_DB_NAME = os.getenv("DEVICE_DATABASE_NAME")

# --- Data for Variation ---
EVENT_TYPES = ["Connection", "Sensor Reading", "Alert", "User action", "System"]


def generate_single_log(timestamp_dt: datetime, devices_list: list) -> dict:
    """Generates a single log document using a specific timestamp and a list of real devices."""
    device = choice(devices_list)
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

    return {
        "device_id": device["id"],
        "device_name": device["name"],
        "mac_address": device["mac"],
        "installation_area": device["area"],
        "timestamp": int(timestamp_dt.timestamp() * 1000),
        "event": {
            "type": event_type,
            "status": event_status,
            "value": event_value
        }
    }


def get_real_devices(client):
    """Fetches and formats device data from the database."""
    db = client[DEVICE_DB_NAME]
    devices_from_db = list(db.devices.find({}))
    if not devices_from_db:
        raise Exception("No devices found in the database. Please add devices before generating logs.")

    print(f"Successfully fetched {len(devices_from_db)} devices.")
    return [
        {"id": str(d["_id"]), "name": d["name"], "mac": d["mac_address"], "area": d["installation_area"]}
        for d in devices_from_db
    ]


# --- Main Script Execution ---
if __name__ == "__main__":
    # --- MODIFICATION: Setup command-line argument parsing ---
    parser = argparse.ArgumentParser(description="Generate sample historical log data for June 2025.")
    parser.add_argument('--output', choices=['direct', 'json'], default='direct',
                        help="Output method: 'direct' to MongoDB or 'json' to a file. (Default: direct)")
    args = parser.parse_args()

    print(f"Starting log generation for {NUM_LOGS_TO_GENERATE} logs for the month of June 2025.")
    print(f"Output mode selected: {args.output}")

    all_logs = []
    real_device_data = []

    # --- Generate Data ---
    try:
        # Fetch device data once
        print("Connecting to MongoDB to fetch real device data...")
        mongo_client = MongoClient(MONGO_DETAILS_URI, username=MONGO_USER, password=MONGO_PASSWORD)
        real_device_data = get_real_devices(mongo_client)
        mongo_client.close()  # Close connection after fetching devices

        print("Generating log documents in memory...")
        for i in range(NUM_LOGS_TO_GENERATE):
            random_offset_seconds = uniform(0, TOTAL_SECONDS_IN_RANGE)
            log_time = START_DATE + timedelta(seconds=random_offset_seconds)
            log_doc = generate_single_log(log_time, real_device_data)
            all_logs.append(log_doc)

        # Sort logs by timestamp before outputting
        all_logs.sort(key=lambda x: x['timestamp'])
        print(f"Generated {len(all_logs)} logs successfully.")

        # --- Output Data based on command-line argument ---
        if args.output == 'json':
            print(f"Writing data to JSON file: {OUTPUT_FILENAME}")
            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(all_logs, f, ensure_ascii=False, indent=2)
            print("Successfully created JSON file.")

        else:  # Default 'direct' output
            print("Connecting to MongoDB for data insertion...")
            mongo_client = MongoClient(MONGO_DETAILS_URI, username=MONGO_USER, password=MONGO_PASSWORD)
            db = mongo_client[DEVICE_DB_NAME]
            logs_collection = db.get_collection("historical_logs")

            print("Clearing existing data from 'historical_logs' collection...")
            logs_collection.delete_many({})

            print(f"Inserting {len(all_logs)} documents into the database...")
            logs_collection.insert_many(all_logs)

            total_inserted = logs_collection.count_documents({})
            print(f"\nSuccessfully inserted {total_inserted} total documents into 'historical_logs'.")

            print("Ensuring indexes on 'historical_logs' are present...")
            logs_collection.create_index([("device_id", ASCENDING), ("timestamp", ASCENDING)])
            print("Indexes verified successfully.")
            mongo_client.close()
            print("Database connection closed.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if 'mongo_client' in locals() and mongo_client:
            mongo_client.close()