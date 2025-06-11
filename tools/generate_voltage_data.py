import os
from datetime import datetime, timedelta, timezone
from random import choice, randint, uniform
from pymongo import MongoClient, ASCENDING
from bson import ObjectId
from dotenv import load_dotenv

# --- Configuration ---
NUM_READINGS_PER_DEVICE = 500
MAX_DAYS_BACK = 90
BATCH_SIZE = 1000

# --- Load Environment Variables ---
load_dotenv()
MONGO_DETAILS_URI = os.getenv("MONGO_DETAILS")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
DEVICE_DB_NAME = os.getenv("DEVICE_DATABASE_NAME")

if not all([MONGO_DETAILS_URI, MONGO_USER, MONGO_PASSWORD, DEVICE_DB_NAME]):
    print("Error: Database environment variables are missing. Check your .env file.")
    exit()

# --- Main Script Execution ---
if __name__ == "__main__":
    try:
        print("Connecting to MongoDB...")
        client = MongoClient(
            MONGO_DETAILS_URI,
            username=MONGO_USER,
            password=MONGO_PASSWORD
        )
        db = client[DEVICE_DB_NAME]

        print("Fetching real device data...")
        devices_from_db = list(db.devices.find({}, {"_id": 1, "installation_area": 1}))
        REAL_DEVICE_DATA = [
            {"id": d["_id"], "area": d["installation_area"]} for d in devices_from_db
        ]

        if not REAL_DEVICE_DATA:
            raise Exception("No devices found in the database.")
        print(f"Found {len(REAL_DEVICE_DATA)} devices to generate data for.")

        voltage_collection = db.get_collection("voltage_readings")

        print("Clearing existing data from 'voltage_readings' collection...")
        voltage_collection.delete_many({})

        print("Starting voltage reading generation...")
        all_readings = []
        latest_timestamp = datetime.now(timezone.utc)

        for device in REAL_DEVICE_DATA:
            print(f"  - Generating {NUM_READINGS_PER_DEVICE} readings for device {device['id']}...")
            current_reading_time = latest_timestamp

            for _ in range(NUM_READINGS_PER_DEVICE):
                interval_seconds = randint(300, 1800)
                current_reading_time -= timedelta(seconds=interval_seconds)

                if (latest_timestamp - current_reading_time).days > MAX_DAYS_BACK:
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
                    # --- FINAL FIX: Convert datetime object to integer milliseconds ---
                    "timestamp": int(current_reading_time.timestamp() * 1000),
                    "voltage": voltage_value,
                    "status": status,
                }
                all_readings.append(reading_doc)

                if len(all_readings) >= BATCH_SIZE:
                    print(f"  ... inserting batch of {len(all_readings)} documents")
                    voltage_collection.insert_many(all_readings)
                    all_readings = []

        if all_readings:
            print(f"  ... inserting final batch of {len(all_readings)} documents")
            voltage_collection.insert_many(all_readings)

        total_inserted = voltage_collection.count_documents({})
        print(f"\nSuccessfully inserted {total_inserted} total documents into 'voltage_readings'.")

        print("Creating indexes on 'voltage_readings' for performance...")
        voltage_collection.create_index([("device_id", ASCENDING), ("timestamp", ASCENDING)])
        voltage_collection.create_index([("area", ASCENDING), ("timestamp", ASCENDING)])
        print("Indexes created successfully.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("Database connection closed.")