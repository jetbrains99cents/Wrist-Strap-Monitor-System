#include "wifi_handler.h"
#include "mediator.h"
#include "config.h"
#include "logger.h"
#include <WiFi.h>
#include <LittleFS.h> // ADDED: Required for serving files
#include <ESPAsyncWebServer.h>

void WifiHandler::init(Mediator* mediator) {
    _mediator = mediator;
    _server = new AsyncWebServer(80);
}

void WifiHandler::loop() {
    // Not needed for async server
}

bool WifiHandler::connect_to_known_networks() {
    struct wifi_cred {
        const char* ssid;
        const char* pass;
    };

    wifi_cred known_networks[] = {
        {Config::get_instance().get_factory_wifi_ssid(), Config::get_instance().get_factory_wifi_password()},
        {Config::get_instance().get_office_wifi_ssid(), Config::get_instance().get_office_wifi_password()},
        {Config::get_instance().get_testing_wifi_ssid(), Config::get_instance().get_testing_wifi_password()}
    };

    WiFi.mode(WIFI_STA);

    for (const auto& cred : known_networks) {
        if (strlen(cred.ssid) == 0) {
            continue;
        }

        Logger::get_instance().log_info("Attempting to connect to WiFi: %s", cred.ssid);
        WiFi.begin(cred.ssid, cred.pass);

        unsigned long start_time = millis();
        while (WiFi.status() != WL_CONNECTED) {
            if (millis() - start_time > 20000) {
                Logger::get_instance().log_warn("Connection attempt to %s timed out.", cred.ssid);
                break;
            }
            delay(500);
            Serial.print(".");
        }
        Serial.println();

        if (WiFi.status() == WL_CONNECTED) {
            Logger::get_instance().log_info("Successfully connected to %s", cred.ssid);
            Logger::get_instance().log_info("IP Address: %s", WiFi.localIP().toString().c_str());
            return true;
        }
    }

    Logger::get_instance().log_error("Failed to connect to any known WiFi network.");
    WiFi.disconnect();
    return false;
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

    WiFi.mode(WIFI_AP);
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
        // In a full implementation, you would parse all parameters here
        Config::get_instance().save();
        
        String response_html = "<html><head><title>Settings Saved</title><meta http-equiv='refresh' content='5;url=/'></head><body><h1>Settings Saved!</h1><p>Device will restart in 5 seconds...</p></body></html>";
        request->send(200, "text/html", response_html);

        _mediator->notify(event_t::RESTART_REQUESTED);
    });

    _server->onNotFound([](AsyncWebServerRequest *request){
        request->send(404, "text/plain", "Not found");
    });
}