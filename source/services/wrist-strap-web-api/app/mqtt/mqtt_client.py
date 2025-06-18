import asyncio
import json
import logging  # Ensure logging is imported to use its levels (DEBUG, INFO, WARNING, ERROR)
from datetime import datetime, timezone
from aiomqtt import Client, MqttError, TLSParameters
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.session import get_async_db_devices
from app.core.config import settings
from app.schemas.voltage_reading import DeviceReadingIn, VoltageReadingCreate, RealtimeDeviceStatusMessage
from app.websocket.websocket_manager import websocket_manager
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class MqttClient:
    def __init__(self):
        self._mqtt_params = {
            "hostname": settings.MQTT_BROKER_HOST,
            "port": settings.MQTT_BROKER_PORT,
            "username": settings.MQTT_USERNAME,
            "password": settings.MQTT_PASSWORD,
        }
        self._loop_task: asyncio.Task | None = None
        self._on_message_callback = None

    async def connect_and_subscribe(self, on_message_callback):
        self._on_message_callback = on_message_callback
        try:
            self._loop_task = asyncio.create_task(self._message_loop())
            logger.info(
                f"Scheduled MQTT message loop to start connecting to {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
            await asyncio.sleep(0.1)

        except Exception as e:
            logger.critical(f"Failed to initiate MQTT message loop task: {e}", exc_info=True)
            raise

    async def _message_loop(self):
        tls_params = None
        # if settings.MQTT_BROKER_HOST.startswith("wss://"):
        #     tls_params = TLSParameters(
        #         ca_certs="/path/to/your/ca.crt",
        #         certfile="/path/to/your/client.crt",
        #         keyfile="/path/to/your/client.key"
        #     )

        while True:
            try:
                async with Client(
                        hostname=self._mqtt_params["hostname"],
                        port=self._mqtt_params["port"],
                        username=self._mqtt_params["username"],
                        password=self._mqtt_params["password"],
                        # tls_params=tls_params, # Uncomment if using TLS
                ) as client:
                    logger.info(
                        f"Connected to MQTT broker: {self._mqtt_params['hostname']}:{self._mqtt_params['port']}")

                    await client.subscribe(f"{settings.MQTT_TOPIC_PREFIX}/#")
                    logger.info(f"Successfully subscribed to topic: {settings.MQTT_TOPIC_PREFIX}/#")

                    async for message in client.messages:
                        await self._process_mqtt_message(message)

            except MqttError as e:
                logger.error(f"MQTT connection lost or error: {e}. Attempting to reconnect in 5 seconds...",
                             exc_info=True)
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("MQTT message loop cancelled during shutdown.")
                break
            except Exception as e:
                logger.critical(f"Unhandled critical error in MQTT message loop: {e}. Exiting loop.", exc_info=True)
                break

    async def _process_mqtt_message(self, message):
        topic = message.topic.value
        payload_bytes = message.payload

        try:
            payload_str = payload_bytes.decode('utf-8')
            raw_device_data = json.loads(payload_str)
            # CHANGED: Use logger.debug for debug-level logs
            logger.debug(f"Received raw MQTT data on '{topic}': {raw_device_data}")

            device_reading_in = DeviceReadingIn(**raw_device_data)

            db_client_instance = get_async_db_devices()

            device_info = await db_client_instance.devices.find_one(
                {"mac_address": device_reading_in.mac_address},
                {
                    "_id": 1,
                    "name": 1,
                    "mac_address": 1,
                    "device_type": 1,
                    "installation_area": 1,
                    "firmware_version": 1,
                    "coordinates": 1,
                }
            )

            if not device_info:
                # CHANGED: Use logger.warning for warning-level logs
                logger.warning(
                    f"Device with MAC address '{device_reading_in.mac_address}' not found in DB. Skipping reading.")
                return

            status_evaluated = "Voltage reading ok"
            if not (3.0 <= device_reading_in.voltage_value <= 5):
                status_evaluated = "Voltage reading failed"

            # Construct the 'last_event' object for both DB update and WebSocket broadcast
            new_last_event = {
                "type": "Sensor Reading",
                "status": status_evaluated,
                "timestamp": device_reading_in.timestamp,
                "value": device_reading_in.voltage_value,
            }

            # --- Update the 'devices' collection with the new last_event ---
            await db_client_instance.devices.update_one(
                {"_id": device_info["_id"]},
                {"$set": {"last_event": new_last_event,
                          "updatedAt": int(datetime.now(timezone.utc).timestamp() * 1000)}}
            )
            logger.info(f"Updated 'last_event' for device {device_info['_id']} in 'devices' collection.")

            # --- Create document for MongoDB (voltage_readings collection) ---
            document_to_insert = {
                "device_id": device_info["_id"],
                "area": device_info["installation_area"],
                "timestamp": device_reading_in.timestamp,
                "voltage": device_reading_in.voltage_value,
                "status": status_evaluated,
            }

            # Create the rich payload for WebSocket broadcast
            realtime_payload_dict = {
                "id": device_info["_id"],
                "name": device_info.get("name", "N/A"),
                "mac_address": device_info.get("mac_address", "N/A"),
                "device_type": device_info.get("device_type", "N/A"),
                "installation_area": device_info.get("installation_area", "N/A"),
                "firmware_version": device_info.get("firmware_version"),
                "coordinates": device_info.get("coordinates"),

                "last_event": new_last_event,
            }

            # Validate the rich payload against the new schema
            final_realtime_message = RealtimeDeviceStatusMessage(**realtime_payload_dict)

            await db_client_instance.voltage_readings.insert_one(document_to_insert)
            logger.info(f"Saved enriched data for device {document_to_insert['device_id']} to MongoDB.")

            if self._on_message_callback:
                await self._on_message_callback(final_realtime_message.model_dump())
                # CHANGED: Use logger.debug for debug-level logs
                logger.debug(f"Broadcasted rich data for device {final_realtime_message.id} to WebSocket clients.")

        except json.JSONDecodeError:
            # CHANGED: Use logger.warning for warning-level logs
            logger.warning(f"Invalid JSON payload on topic '{topic}': {payload_str}")
        except ValidationError as e:
            # CHANGED: Use logger.warning for warning-level logs
            logger.warning(f"Validation error for MQTT message on topic '{topic}': {e.errors()}", exc_info=True)
        except RuntimeError as e:
            logger.error(f"MongoDB not connected while processing MQTT message: {e}. Skipping message.", exc_info=True)
        except Exception as e:
            logger.error(f"Unhandled error processing MQTT message from topic '{topic}': {e}", exc_info=True)

    async def disconnect(self):
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Error while waiting for MQTT loop task cancellation: {e}", exc_info=True)
            self._loop_task = None
        logger.info("MQTT client background task requested to stop.")


mqtt_client_instance = MqttClient()