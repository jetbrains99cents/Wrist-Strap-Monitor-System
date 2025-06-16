#include "api_requests.h"
#include "mediator.h"
#include "config.h"
#include "logger.h"
#include <WiFi.h>
#include <HTTPClient.h>
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

    Logger::get_instance().log_info("Requesting time synchronization...");
    
    HTTPClient http;
    // NOTE: For production, use WiFiClientSecure and verify the server certificate.
    // This current implementation is for local development with HTTP.
    const char* time_server_url = Config::get_instance().get_base_api_url();
    String full_url = String(time_server_url) + "/api/v1/time/";
    
    Logger::get_instance().log_info("Time sync URL: %s", full_url.c_str());

    http.begin(full_url);
    int http_code = http.GET();

    if (http_code == HTTP_CODE_OK) {
        String payload = http.getString();
        JsonDocument doc;
        DeserializationError error = deserializeJson(doc, payload);

        if (error) {
            Logger::get_instance().log_error("Failed to parse time sync JSON: %s", error.c_str());
            _mediator->notify(event_t::TIME_SYNC_FAILED);
        } else {
            long timestamp_seconds = doc["timestamp_utc_seconds"];
            if (timestamp_seconds > 0) {
                timeval tv = { timestamp_seconds, 0 };
                settimeofday(&tv, nullptr);
                Logger::get_instance().log_info("System time synchronized successfully.");
                _mediator->notify(event_t::TIME_SYNC_SUCCESS);
            } else {
                 Logger::get_instance().log_error("Invalid timestamp received from server.");
                _mediator->notify(event_t::TIME_SYNC_FAILED);
            }
        }
    } else {
        Logger::get_instance().log_error("Time sync HTTP request failed, error: %s", http.errorToString(http_code).c_str());
        _mediator->notify(event_t::TIME_SYNC_FAILED);
    }

    http.end();
}