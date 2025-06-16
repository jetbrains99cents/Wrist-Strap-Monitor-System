#include "mediator.h"
#include "config.h"
#include "logger.h"
#include "wifi_handler.h"
#include "mqtt_client.h"
#include "api_requests.h"
#include "ota_handler.h"
#include "peripheral.h"
#include "database.h"
#include <ArduinoJson.h>
#include <WiFi.h>

void Mediator::init() {
    _mqtt_reconnect_time = 0;
}

void Mediator::register_wifi_handler(WifiHandler* handler) { _wifi_handler = handler; }
void Mediator::register_mqtt_client(MqttClient* client) { _mqtt_client = client; }
void Mediator::register_api_requests(ApiRequests* requests) { _api_requests = requests; }
void Mediator::register_ota_handler(OtaHandler* handler) { _ota_handler = handler; }
void Mediator::register_peripheral(Peripheral* peripheral) { _peripheral = peripheral; }
void Mediator::register_database(Database* database) { _database = database; }
void Mediator::register_logger(Logger* logger) { _logger = logger; }

void Mediator::notify(event_t event, void* data) {
    _logger->log_info("Mediator received event: %d", (int)event);

    switch (event) {
        case event_t::START_NORMAL_MODE:
            if (_wifi_handler->connect_to_known_networks()) {
                notify(event_t::WIFI_CONNECTED);
            } else {
                notify(event_t::WIFI_CONNECTION_FAILED);
            }
            break;

        case event_t::START_CONFIG_MODE:
            _wifi_handler->start_access_point();
            break;

        case event_t::WIFI_CONNECTED:
            _ota_handler->setup_local_ota();
            notify(event_t::TIME_SYNC_REQUESTED);
            notify(event_t::MQTT_CONNECT_REQUESTED);
            break;

        case event_t::WIFI_CONNECTION_FAILED:
            notify(event_t::START_CONFIG_MODE);
            break;

        case event_t::TIME_SYNC_REQUESTED:
            _api_requests->request_time_sync();
            break;

        case event_t::TIME_SYNC_SUCCESS:
            _logger->log_info("Time sync successful, system is fully operational.");
            break;

        case event_t::MQTT_CONNECT_REQUESTED:
            _mqtt_client->connect_to_broker();
            break;

        case event_t::MQTT_DISCONNECTED:
            _logger->log_warn("MQTT disconnected. Async client will handle reconnect.");
            break;

        case event_t::MQTT_CONNECTED:
             _mqtt_client->publish_from_queue();
             break;

        case event_t::WRIST_STRAP_STATE_UPDATED: {
            reading_data_t* reading = (reading_data_t*)data;

            JsonDocument doc;
            doc["mac_address"] = WiFi.macAddress();

            timeval tv;
            gettimeofday(&tv, nullptr);
            uint64_t timestamp_ms = (uint64_t)tv.tv_sec * 1000L + (uint64_t)tv.tv_usec / 1000L;
            doc["timestamp"] = timestamp_ms;

            doc["voltage_value"] = reading->voltage;
            // Removed: doc["status"] = (reading->status == wrist_strap_status_t::STATUS_PASS) ? "PASS" : "FAIL";

            char json_buffer[256];
            serializeJson(doc, json_buffer);

            _database->append_reading(json_buffer);
            _mqtt_client->publish_from_queue();
            break;
        }

        case event_t::MQTT_MESSAGE_PUBLISHED_SUCCESS:
             break;

        case event_t::SENSOR_READ_REQUESTED:
            _peripheral->read_and_process_data();
            break;
        
        case event_t::OTA_CHECK_REQUESTED:
            _ota_handler->check_for_http_update();
            break;

        case event_t::RESTART_REQUESTED:
            _logger->log_warn("Restart requested. Rebooting in 3 seconds...");
            delay(3000);
            ESP.restart();
            break;
        
        default:
            _logger->log_warn("Mediator received an unhandled event: %d", (int)event);
            break;
    }
}