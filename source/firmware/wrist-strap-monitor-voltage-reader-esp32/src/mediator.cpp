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
#include <sys/time.h>
#include <time.h>

void Mediator::init() {
    _is_time_synced = false;
    _is_mqtt_connected = false;
    _next_time_sync_attempt_ms = 0;
    _next_mqtt_connect_attempt_ms = 0;
}

void Mediator::loop() {
    if (!_is_time_synced && WiFi.status() == WL_CONNECTED && millis() >= _next_time_sync_attempt_ms) {
        notify(event_t::TIME_SYNC_REQUESTED);
    }

    if (!_is_mqtt_connected && WiFi.status() == WL_CONNECTED && millis() >= _next_mqtt_connect_attempt_ms) {
        notify(event_t::MQTT_CONNECT_REQUESTED);
    }
}

void Mediator::register_wifi_handler(WifiHandler* handler) { _wifi_handler = handler; }
void Mediator::register_mqtt_client(MqttClient* client) { _mqtt_client = client; }
void Mediator::register_api_requests(ApiRequests* requests) { _api_requests = requests; }
void Mediator::register_ota_handler(OtaHandler* handler) { _ota_handler = handler; }
void Mediator::register_peripheral(Peripheral* peripheral) { _peripheral = peripheral; }
void Mediator::register_database(Database* database) { _database = database; }
void Mediator::register_logger(Logger* logger) { _logger = logger; }

void Mediator::notify(event_t event, void* data) {
    if (event != event_t::SENSOR_READ_REQUESTED && event != event_t::LOG_MESSAGE_CREATED) {
        _logger->log_info("Mediator received event: %d", (int)event);
    }

    switch (event) {
        case event_t::START_NORMAL_MODE:
            _wifi_handler->begin_connection_process();
            break;
        case event_t::START_CONFIG_MODE:
            _wifi_handler->start_access_point();
            break;
        case event_t::RESTART_REQUESTED:
            _logger->log_warn("Restart requested. Rebooting in 3 seconds...");
            delay(3000);
            ESP.restart();
            break;
        case event_t::WIFI_CONNECTED:
            _logger->log_info("Wi-Fi Connected. Initializing service connections...");
            _next_time_sync_attempt_ms = millis();
            _next_mqtt_connect_attempt_ms = millis();
            break;
        case event_t::WIFI_CONNECTION_FAILED:
            break;
        case event_t::WIFI_DISCONNECTED:
             _logger->log_warn("WiFi disconnected. Services will attempt to reconnect when Wi-Fi is restored.");
             _is_mqtt_connected = false;
            break;
        case event_t::TIME_SYNC_REQUESTED:
             _logger->log_info("Attempting to synchronize time...");
             _next_time_sync_attempt_ms = millis() + 60000;
             _api_requests->request_time_sync();
            break;
        case event_t::TIME_SYNC_SUCCESS: {
            _is_time_synced = true;
            time_t now;
            struct tm timeinfo;
            char buffer[80];
            time(&now);
            localtime_r(&now, &timeinfo);
            strftime(buffer, sizeof(buffer), "%A, %B %d %Y %H:%M:%S", &timeinfo);
            _logger->log_info("Time sync successful. Current time: %s", buffer);
            break;
        }
        case event_t::TIME_SYNC_FAILED: {
            long interval_ms = Config::get_instance().get_time_sync_retry_delay_seconds() * 1000L;
            _logger->log_warn("Time sync attempt failed. Retrying in %ld seconds.", interval_ms / 1000L);
            _next_time_sync_attempt_ms = millis() + interval_ms;
            break;
        }
        case event_t::MQTT_CONNECT_REQUESTED:
            _logger->log_info("Attempting to connect to MQTT broker...");
            _next_mqtt_connect_attempt_ms = millis() + 60000;
            _mqtt_client->connect_to_broker();
            break;
        case event_t::MQTT_CONNECTED:
             _is_mqtt_connected = true;
             _logger->log_info("MQTT Connected. Publishing any queued messages.");
             _mqtt_client->publish_from_queue();
            break;
        case event_t::MQTT_DISCONNECTED: {
            _is_mqtt_connected = false;
            long interval_ms = Config::get_instance().get_mqtt_auto_reconnect_delay();
            _logger->log_warn("MQTT disconnected. Retrying in %ldms.", interval_ms);
            _next_mqtt_connect_attempt_ms = millis() + interval_ms;
            break;
        }
        case event_t::MQTT_MESSAGE_PUBLISHED_SUCCESS:
             break;
        case event_t::WRIST_STRAP_STATE_UPDATED: {
            reading_data_t* reading = (reading_data_t*)data;
            JsonDocument doc;
            doc["mac_address"] = WiFi.macAddress();

            uint64_t timestamp_ms;
            if (_is_time_synced) {
                timeval tv;
                gettimeofday(&tv, nullptr);
                timestamp_ms = (uint64_t)tv.tv_sec * 1000L + (uint64_t)tv.tv_usec / 1000L;
            } else {
                timestamp_ms = 1735693200000ULL;
            }
            doc["timestamp"] = timestamp_ms;

            doc["voltage_value"] = reading->voltage;

            char json_buffer[256];
            serializeJson(doc, json_buffer);

            _database->append_reading(json_buffer);
            _mqtt_client->publish_from_queue();
            break;
        }
        case event_t::SENSOR_READ_REQUESTED:
            _peripheral->read_and_process_data();
            break;
        case event_t::OTA_CHECK_REQUESTED:
            _ota_handler->check_for_http_update();
            break;
        case event_t::LOG_MESSAGE_CREATED: {
            if (!Serial && _mqtt_client != nullptr && _mqtt_client->is_connected()) {
                _mqtt_client->publish_log((const char*)data);
            }
            break;
        }
        default:
            _logger->log_warn("Mediator received an unhandled event: %d", (int)event);
            break;
    }
}