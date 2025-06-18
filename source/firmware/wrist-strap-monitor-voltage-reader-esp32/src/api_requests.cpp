#include "api_requests.h"
#include "mediator.h"
#include "config.h"
#include "logger.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <sys/time.h>

void ApiRequests::init(Mediator* mediator) {
    _mediator = mediator;
}

void ApiRequests::request_time_sync() {
    if (WiFi.status() != WL_CONNECTED) {
        Logger::get_instance().log_error("Cannot sync time, WiFi not connected.");
        _mediator->notify(event_t::TIME_SYNC_FAILED);
        return;
    }

    Logger::get_instance().log_info("Requesting time synchronization (sync)...");

    HTTPClient http;
    WiFiClientSecure client;

    const char* server_url = Config::get_instance().get_base_api_url();
    String full_url = String(server_url) + "/api/v1/time/";

    Logger::get_instance().log_info("Time sync URL: %s", full_url.c_str());

    // This allows connecting to local servers with self-signed certs (for HTTPS)
    // It's safe and good practice to keep for flexibility.
    client.setInsecure();

    // Begin the connection using the secure client.
    http.begin(client, full_url);
    http.setConnectTimeout(5000); // 5-second timeout

    int http_code = http.GET();

    if (http_code == HTTP_CODE_OK) {
        String payload = http.getString();
        JsonDocument doc;
        DeserializationError error = deserializeJson(doc, payload);

        if (error) {
            Logger::get_instance().log_error("Failed to parse time sync JSON: %s", error.c_str());
            _mediator->notify(event_t::TIME_SYNC_FAILED);
        } else {
            int64_t timestamp_seconds = doc["timestamp_utc_seconds"];
            if (timestamp_seconds > 0) {
                timeval tv = { (time_t)timestamp_seconds, 0 };
                settimeofday(&tv, nullptr);
                _mediator->notify(event_t::TIME_SYNC_SUCCESS);
            } else {
                 Logger::get_instance().log_error("Invalid timestamp received from server.");
                _mediator->notify(event_t::TIME_SYNC_FAILED);
            }
        }
    } else {
        Logger::get_instance().log_error("Time sync HTTP request failed, error code: %d, message: %s", http_code, http.errorToString(http_code).c_str());
        _mediator->notify(event_t::TIME_SYNC_FAILED);
    }

    http.end();
}