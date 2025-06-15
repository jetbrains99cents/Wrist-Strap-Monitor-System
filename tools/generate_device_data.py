import os
import random
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
import argparse

# --- Configuration ---
NUM_DEVICES_TO_CREATE = 50
INSTALLATION_AREAS = [
    "POL", "FLW", "CG", "OQC Lighting", "D Inspection",
    "Warehouse Z", "Logistics", "Packaging", "Testing Y"
]
# --- MODIFICATION: Define the two device types ---
DEVICE_TYPE_1 = "WristStrapMonitorKD2001"
DEVICE_TYPE_2 = "WristStrapMonitorKD2002"
NUM_TYPE_2_DEVICES = 7  # The number of special KD2002 devices to create

# --- Load Environment Variables ---
load_dotenv()
MONGO_DETAILS_URI = os.getenv("MONGO_DETAILS")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
DEVICE_DB_NAME = os.getenv("DEVICE_DATABASE_NAME")


def generate_mac_address(index: int) -> str:
    """Generates a unique, formatted MAC address based on an index."""
    hex_string = f"{index:012x}"
    return ":".join(hex_string[i:i + 2] for i in range(0, 12, 2)).upper()


def generate_firmware_version() -> str:
    """Generates a random semantic version string."""
    return f"{random.randint(1, 3)}.{random.randint(0, 5)}.{random.randint(0, 10)}"


def generate_last_event() -> dict:
    """Generates a realistic sample for the last_event field."""
    event_type = random.choice(["Connection", "Sensor Reading", "Alert"])
    status = None
    value = "N/A"

    if event_type == "Connection":
        status = random.choice(["Connected", "Disconnected"])
        value = "Heartbeat received" if status == "Connected" else "Connection timed out"
    elif event_type == "Sensor Reading":
        status = "Info"
        value = round(random.uniform(3.0, 3.4), 2)
    elif event_type == "Alert":
        status = random.choice(["Warning", "Error", "Critical"])
        value = "High temperature detected" if status == "Warning" else "Component failure"

    return {
        "type": event_type,
        "status": status,
        "timestamp": int((datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 60))).timestamp() * 1000),
        "value": value
    }


def create_device_documents(num_devices: int) -> list:
    """Creates a list of device documents."""
    devices = []
    now = datetime.now(timezone.utc)

    for i in range(1, num_devices + 1):
        created_at_dt = now - timedelta(days=random.randint(10, 365))
        installation_date_dt = created_at_dt + timedelta(days=random.randint(1, 5))
        updated_at_dt = installation_date_dt + timedelta(minutes=random.randint(30, 20000))

        created_at_ts = int(created_at_dt.timestamp() * 1000)
        installation_date_ts = int(installation_date_dt.timestamp() * 1000)
        updated_at_ts = int(updated_at_dt.timestamp() * 1000)

        has_coordinates = random.random() < 0.8

        # --- MODIFICATION: Assign device type based on the configured numbers ---
        if i <= NUM_TYPE_2_DEVICES:
            device_type = DEVICE_TYPE_2
        else:
            device_type = DEVICE_TYPE_1

        device_doc = {
            "name": f"Device {i}",
            "mac_address": generate_mac_address(i),
            "device_type": device_type,  # Use the assigned type
            "installation_area": random.choice(INSTALLATION_AREAS),
            "coordinates": {
                "row": random.randint(0, 20),
                "col": random.randint(0, 20)
            } if has_coordinates else None,
            "scale_at_creation_time": round(random.uniform(1.0, 5.0), 1) if has_coordinates else None,
            "last_event": generate_last_event(),
            "firmware_version": generate_firmware_version(),
            "installation_date": installation_date_ts,
            "createdAt": created_at_ts,
            "updatedAt": updated_at_ts
        }
        devices.append(device_doc)

    return devices


# --- Main Script Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sample device data for the devices collection.")
    parser.add_argument('--count', type=int, default=NUM_DEVICES_TO_CREATE,
                        help=f"Total number of devices to create. (Default: {NUM_DEVICES_TO_CREATE})")
    args = parser.parse_args()

    if args.count < NUM_TYPE_2_DEVICES:
        print(
            f"\nWarning: Total count ({args.count}) is less than the number of Type 2 devices ({NUM_TYPE_2_DEVICES}). All generated devices will be Type 2.")

    if not all([MONGO_DETAILS_URI, MONGO_USER, MONGO_PASSWORD, DEVICE_DB_NAME]):
        print("\nError: Database environment variables are missing. Please check your .env file.")
        exit(1)

    client = None
    try:
        print(f"\nGenerating {args.count} sample device documents in memory...")
        devices_to_insert = create_device_documents(args.count)
        print("Generation complete.")

        confirm = input(
            f"\nThis will DELETE ALL existing documents in the 'devices' collection and insert {args.count} new ones.\nAre you sure you want to continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled.")
            exit(0)

        print("\nConnecting to MongoDB...")
        client = MongoClient(MONGO_DETAILS_URI, username=MONGO_USER, password=MONGO_PASSWORD)
        db = client[DEVICE_DB_NAME]
        devices_collection = db.get_collection("devices")

        print("Clearing existing data from 'devices' collection...")
        delete_result = devices_collection.delete_many({})
        print(f"Deleted {delete_result.deleted_count} documents.")

        print(f"Inserting {len(devices_to_insert)} new documents...")
        insert_result = devices_collection.insert_many(devices_to_insert)
        print(f"Successfully inserted {len(insert_result.inserted_ids)} new documents.")

        print("\nCreating index on 'mac_address' for performance...")
        devices_collection.create_index("mac_address", unique=True)
        print("Index created successfully.")

    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if client:
            client.close()
            print("\nDatabase connection closed.")