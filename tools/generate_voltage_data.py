import os
from datetime import datetime, timedelta, timezone
from random import choice, randint, uniform
from pymongo import MongoClient, ASCENDING
from dotenv import load_dotenv
import argparse  # --- MODIFICATION: Added for command-line arguments

# --- Configuration ---
NUM_READINGS_PER_DEVICE = 500
BATCH_SIZE = 1000
OUTPUT_FILENAME = "voltage_readings_data_june_2025.json"

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


def get_real_devices(client):
    """Fetches and formats device data from the database."""
    db = client[DEVICE_DB_NAME]
    devices_from_db = list(db.devices.find({}, {"_id": 1, "installation_area": 1}))
    if not devices_from_db:
        raise Exception("No devices found in the database.")

    print(f"Found {len(devices_from_db)} devices to generate data for.")
    return [{"id": d["_id"], "area": d["installation_area"]} for d in devices_from_db]


# --- Main Script Execution ---
if __name__ == "__main__":
    # --- MODIFICATION: Setup command-line argument parsing ---
    parser = argparse.ArgumentParser(description="Generate sample voltage reading data for June 2025.")
    parser.add_argument('--output', choices=['direct', 'json'], default='direct',
                        help="Output method: 'direct' to MongoDB or 'json' to a file. (Default: direct)")
    args = parser.parse_args()

    print("Starting voltage reading generation for June 2025.")
    print(f"Output mode selected: {args.output}")

    all_readings = []

    try:
        # Fetch device data once
        print("Connecting to MongoDB to fetch real device data...")
        client = MongoClient(MONGO_DETAILS_URI, username=MONGO_USER, password=MONGO_PASSWORD)
        real_device_data = get_real_devices(client)
        client.close()

        print("Generating voltage reading documents in memory...")
        for device in real_device_data:
            print(f"  - Generating {NUM_READINGS_PER_DEVICE} readings for device {device['id']}...")

            # --- MODIFICATION: Generate timestamps within the June 2025 range ---
            # To make it realistic, we give each device a random "active" period within the month.
            active_period_start = START_DATE + timedelta(seconds=uniform(0, TOTAL_SECONDS_IN_RANGE * 0.8))
            active_period_end = active_period_start + timedelta(seconds=uniform(0, TOTAL_SECONDS_IN_RANGE * 0.2))

            if active_period_end > END_DATE:
                active_period_end = END_DATE

            current_reading_time = active_period_end

            for _ in range(NUM_READINGS_PER_DEVICE):
                interval_seconds = randint(300, 1800)
                current_reading_time -= timedelta(seconds=interval_seconds)

                if current_reading_time < START_DATE:
                    break

                voltage_value = float(round(uniform(2.8, 3.5), 2))
                status = "Connected"
                if voltage_value < 3.0:
                    status = "Fault"
                elif voltage_value > 3.4:
                    status = "Warning"

                reading_doc = {
                    "device_id": device["id"],
                    "area": device["area"],
                    "timestamp": int(current_reading_time.timestamp() * 1000),
                    "voltage": voltage_value,
                    "status": status,
                }
                all_readings.append(reading_doc)

        # Sort all readings by timestamp before outputting
        all_readings.sort(key=lambda x: x['timestamp'])
        print(f"Generated a total of {len(all_readings)} readings.")

        # --- Output Data based on command-line argument ---
        if args.output == 'json':
            print(f"Writing data to JSON file: {OUTPUT_FILENAME}")
            # We need to handle ObjectId for JSON serialization
            from bson.json_util import dumps

            with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
                f.write(dumps(all_readings, indent=2))
            print("Successfully created JSON file.")

        else:  # Default 'direct' output
            print("Connecting to MongoDB for data insertion...")
            client = MongoClient(MONGO_DETAILS_URI, username=MONGO_USER, password=MONGO_PASSWORD)
            db = client[DEVICE_DB_NAME]
            voltage_collection = db.get_collection("voltage_readings")

            print("Clearing existing data from 'voltage_readings' collection...")
            voltage_collection.delete_many({})

            print("Inserting documents in batches...")
            for i in range(0, len(all_readings), BATCH_SIZE):
                batch = all_readings[i:i + BATCH_SIZE]
                print(f"  ... inserting batch of {len(batch)} documents")
                voltage_collection.insert_many(batch)

            total_inserted = voltage_collection.count_documents({})
            print(f"\nSuccessfully inserted {total_inserted} total documents into 'voltage_readings'.")

            print("Ensuring indexes on 'voltage_readings' are present...")
            voltage_collection.create_index([("device_id", ASCENDING), ("timestamp", ASCENDING)])
            voltage_collection.create_index([("area", ASCENDING), ("timestamp", ASCENDING)])
            print("Indexes verified successfully.")
            client.close()
            print("Database connection closed.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if 'client' in locals() and client:
            client.close()