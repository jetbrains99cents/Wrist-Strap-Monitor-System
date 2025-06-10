import json
from datetime import datetime, timedelta, timezone
from random import choice, randint, uniform

# --- Configuration for Data Generation ---
NUM_LOGS_TO_GENERATE = 5000  # Total number of log entries to generate
MAX_DAYS_BACK = 365 * 2 + 30  # Generate logs for the last ~2 years and a month (to cover all time ranges)
MIN_SECONDS_INTERVAL = 10  # Minimum time difference between consecutive logs (for spread)
MAX_SECONDS_INTERVAL = 300  # Maximum time difference between consecutive logs
OUTPUT_FILENAME = "historical_logs_data.json"

# --- Fixed Lists for Data Variation ---
# Using consistent device IDs/names/MACs for realistic logs
DEVICE_DATA = []
NUM_UNIQUE_DEVICES = 30
DEVICE_ID_PREFIX = "ESP32-"
DEVICE_MAC_PREFIX = "00:1A:2B:3C:DD:"

for i in range(1, NUM_UNIQUE_DEVICES + 1):
    DEVICE_DATA.append({
        "id": f"{DEVICE_ID_PREFIX}{100 + i}",
        "name": f"Device {i}",
        "mac": f"{DEVICE_MAC_PREFIX}{i:02X}"
    })

AREAS = [
    "POL", "FLW", "CG A", "CG B", "Testing Alpha", "Warehouse Main",
    "D Inspection", "Assembly X", "Testing Y", "Warehouse Z",
    "Receiving Dock", "Shipping Bay", "Production Line 1", "Production Line 2"
]
EVENT_TYPES = ["Connection", "Sensor Reading", "Alert", "User action", "System"]
STATUSES = [
    "Connected", "Disconnected", "Voltage reading failed", "Info",
    "Warning", "Error", "Critical", "Configured", "Reset"
]


# --- Helper Function to Generate a Single Log Document ---
def generate_single_log(current_datetime: datetime) -> dict:
    device = choice(DEVICE_DATA)
    area = choice(AREAS)
    event_type = choice(EVENT_TYPES)

    event_status = None
    event_value = "Generic log message."

    # Make event status and value more realistic based on event_type
    if event_type == "Connection":
        event_status = choice(["Connected", "Disconnected"])
        event_value = "Device " + event_status.lower() + " successfully." if event_status == "Connected" else "Connection lost."
    elif event_type == "Sensor Reading":
        event_status = choice(["Info", "Warning", "Voltage reading failed"])
        if event_status == "Info":
            event_value = f"Temperature: {uniform(20.0, 35.0):.1f}C"
        elif event_status == "Warning":
            event_value = f"Humidity high: {uniform(70.0, 90.0):.1f}%"
        else:
            event_value = "Sensor read error."
    elif event_type == "Alert":
        event_status = choice(["Warning", "Error", "Critical"])
        event_value = choice([
            "Unauthorized access attempt detected.",
            "Component failure imminent.",
            "Critical system overload."
        ])
    elif event_type == "User action":
        event_status = choice(["Configured", "Reset"])
        event_value = choice([
            "User settings updated by Admin.",
            "Device reconfigured.",
            "System initiated reset."
        ])
    elif event_type == "System":
        event_status = choice(["Info", "Error"])
        event_value = choice([
            "System startup complete.",
            "Software update applied.",
            "Unexpected shutdown."
        ])

    # Construct the log document as a dictionary
    log_doc = {
        "timestamp": {"$numberLong": str(int(current_datetime.timestamp() * 1000))},  # MongoDB's Long type
        "device_id": device["id"],
        "device_name": device["name"],
        "mac_address": device["mac"],
        "installation_area": area,
        "event": {
            "type": event_type,
            "status": event_status,
            "value": event_value
        }
    }
    return log_doc


# --- Main Script Execution ---
if __name__ == "__main__":
    print(f"Starting log generation script for {NUM_LOGS_TO_GENERATE} logs...")
    print(
        f"Logs will span up to {MAX_DAYS_BACK} days into the past from current time in Tan Uyen, Binh Duong, Vietnam.")

    # Get current time in Tan Uyen (UTC+7)
    tan_uyen_tz = timezone(timedelta(hours=7))
    latest_timestamp = datetime.now(tan_uyen_tz)

    logs_to_output = []

    # Generate logs backwards from the latest time for better time distribution
    current_log_time = latest_timestamp
    for i in range(NUM_LOGS_TO_GENERATE):
        log_doc = generate_single_log(current_log_time)
        logs_to_output.append(log_doc)

        # Decrement time for the next log by a random interval
        interval_seconds = randint(MIN_SECONDS_INTERVAL, MAX_SECONDS_INTERVAL)
        current_log_time -= timedelta(seconds=interval_seconds)

        # Optional: stop generating if we go too far back, to avoid excessive data for very old ranges
        if (latest_timestamp - current_log_time).days > MAX_DAYS_BACK:
            print(
                f"Stopped generating logs as max historical depth ({MAX_DAYS_BACK} days) reached at {len(logs_to_output)} logs.")
            break

    # Reverse the list so logs are in chronological order (oldest first)
    logs_to_output.reverse()

    if not logs_to_output:
        print("No logs were generated.")
        exit()

    # Write the generated logs to a JSON file
    try:
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(logs_to_output, f, ensure_ascii=False, indent=2)
        print(f"Successfully generated {len(logs_to_output)} log documents to '{OUTPUT_FILENAME}'.")
    except Exception as e:
        print(f"Error writing logs to JSON file: {e}")

    print("Log generation script finished.")