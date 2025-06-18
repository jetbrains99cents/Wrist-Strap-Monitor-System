#include "wifi_handler.h"
#include "mediator.h"
#include "config.h"
#include "logger.h"
#include <WiFi.h>
#include <LittleFS.h>
#include <ESPAsyncWebServer.h>

void WifiHandler::init(Mediator* mediator) {
    _mediator = mediator;
    _server = new AsyncWebServer(80);
}

void WifiHandler::begin_connection_process() {
    log_mac_address();
    _current_network_index = 0;
    _state = wifi_state_t::CONNECTING;
    Logger::get_instance().log_info("Starting non-blocking WiFi connection process...");
}

void WifiHandler::loop() {
    if (_state != wifi_state_t::CONNECTING) {
        return; // Do nothing if not in the connecting state
    }

    // This is our non-blocking state machine for connecting to Wi-Fi
    struct wifi_cred {
        const char* ssid;
        const char* pass;
    };
    wifi_cred known_networks[] = {
        {Config::get_instance().get_factory_wifi_ssid(), Config::get_instance().get_factory_wifi_password()},
        {Config::get_instance().get_office_wifi_ssid(), Config::get_instance().get_office_wifi_password()},
        {Config::get_instance().get_testing_wifi_ssid(), Config::get_instance().get_testing_wifi_password()}
    };
    const int num_networks = sizeof(known_networks) / sizeof(wifi_cred);

    // Check for success
    if (WiFi.status() == WL_CONNECTED) {
        Logger::get_instance().log_info("Successfully connected to %s", WiFi.SSID().c_str());
        Logger::get_instance().log_info("IP Address: %s", WiFi.localIP().toString().c_str());
        _state = wifi_state_t::CONNECTED;
        _mediator->notify(event_t::WIFI_CONNECTED);
        return;
    }

    // Check for timeout on the current attempt
    if (_connection_start_time != 0 && (millis() > _connection_start_time + WIFI_CONNECT_TIMEOUT_MS)) {
        Logger::get_instance().log_warn("Connection attempt to %s timed out.", known_networks[_current_network_index].ssid);
        _current_network_index++; // Move to the next network
        _connection_start_time = 0; // Reset timer to trigger a new attempt
        WiFi.disconnect();
    }

    // Check if we've run out of networks to try
    if (_current_network_index >= num_networks) {
        Logger::get_instance().log_error("Failed to connect to any known WiFi network.");
        _state = wifi_state_t::CONNECTION_FAILED;
        _mediator->notify(event_t::WIFI_CONNECTION_FAILED);
        return;
    }

    // If timer is reset, it's time to start a new connection attempt
    if (_connection_start_time == 0) {
        const char* current_ssid = known_networks[_current_network_index].ssid;
        if (strlen(current_ssid) > 0) {
            Logger::get_instance().log_info("Attempting to connect to WiFi: %s", current_ssid);
            WiFi.mode(WIFI_STA);
            WiFi.begin(current_ssid, known_networks[_current_network_index].pass);
            _connection_start_time = millis();
        } else {
            _current_network_index++; // Skip empty SSID and try next one on the next loop
        }
    }
}

void WifiHandler::start_access_point() {
    const char* prefix = Config::get_instance().get_device_ap_wifi_ssid_prefix();
    const char* password = Config::get_instance().get_device_ap_wifi_password();
    String mac_address = WiFi.macAddress();
    mac_address.replace(":", "");
    String mac_suffix = mac_address.substring(6);
    char full_ssid[64];
    snprintf(full_ssid, sizeof(full_ssid), "%s%s", prefix, mac_suffix.c_str());

    Logger::get_instance().log_info("Starting Access Point...");
    Logger::get_instance().log_info("==========================================");
    Logger::get_instance().log_info("SSID: %s", full_ssid);
    Logger::get_instance().log_info("Password: %s", password);
    Logger::get_instance().log_info("Connect and go to http://192.168.4.1");
    Logger::get_instance().log_info("==========================================");

    WiFi.softAP(full_ssid, password);
    setup_web_server();
    _server->begin();
}

void WifiHandler::setup_web_server() {
    _server->on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(LittleFS, "/index.html", "text/html");
    });
    _server->on("/save", HTTP_POST, [this](AsyncWebServerRequest *request) {
        Logger::get_instance().log_info("Received new settings from web portal.");
        // A full implementation would parse all POST parameters here and set the config
        Config::get_instance().save();
        String response_html = "<html><head><title>Settings Saved</title><meta http-equiv='refresh' content='5;url=/'></head><body><h1>Settings Saved!</h1><p>Device will restart in 5 seconds...</p></body></html>";
        request->send(200, "text/html", response_html);
        _mediator->notify(event_t::RESTART_REQUESTED);
    });
    _server->onNotFound([](AsyncWebServerRequest *request){
        request->send(404, "text/plain", "Not found");
    });
}

void WifiHandler::log_mac_address() {
    Logger::get_instance().log_info("Device MAC Address: %s", WiFi.macAddress().c_str());
}