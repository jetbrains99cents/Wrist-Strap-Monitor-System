#include "wifi_handler.h"
#include "mediator.h"
#include "config.h"
#include "logger.h"
#include <WiFi.h>
#include <LittleFS.h> // Required for serving files
#include <ESPAsyncWebServer.h>

void WifiHandler::init(Mediator* mediator) {
    _mediator = mediator;
    _server = new AsyncWebServer(80); // Initialize the web server
}

void WifiHandler::loop() {
    // For AsyncWebServer, _server->handleClient() is not needed in loop().
    // The AsyncWebServer handles requests asynchronously in its own context.
    // If you had any non-async HTTP server components, they would go here.
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

    // Log MAC address on startup, before attempting Wi-Fi connection
    log_mac_address(); // Log MAC address on startup [cite: wifi_handler.cpp]

    for (const auto& cred : known_networks) {
        if (strlen(cred.ssid) == 0) {
            continue;
        }

        Logger::get_instance().log_info("Attempting to connect to WiFi: %s", cred.ssid);
        WiFi.begin(cred.ssid, cred.pass);

        unsigned long start_time = millis();
        // Wait for connection with a timeout
        while (WiFi.status() != WL_CONNECTED) {
            if (millis() - start_time > 20000) { // 20-second timeout
                Logger::get_instance().log_warn("Connection attempt to %s timed out.", cred.ssid);
                break;
            }
            delay(500);
            Serial.print("."); // Indicate waiting
        }
        Serial.println(); // Newline after connection attempts for cleaner log

        if (WiFi.status() == WL_CONNECTED) {
            Logger::get_instance().log_info("Successfully connected to %s", cred.ssid);
            Logger::get_instance().log_info("IP Address: %s", WiFi.localIP().toString().c_str());
            return true; // Return true on first successful connection
        }
    }

    Logger::get_instance().log_error("Failed to connect to any known WiFi network.");
    WiFi.disconnect(true); // Disconnect fully if no connection was made
    return false;
}

void WifiHandler::start_access_point() {
    const char* prefix = Config::get_instance().get_device_ap_wifi_ssid_prefix();
    const char* password = Config::get_instance().get_device_ap_wifi_password();

    String mac_address = WiFi.macAddress();
    mac_address.replace(":", ""); // Remove colons from MAC for cleaner suffix
    String mac_suffix = mac_address.substring(6); // Get last 6 chars for uniqueness

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

    // Initialize LittleFS for web server only if starting AP
    if (!LittleFS.begin(true)) {
        Logger::get_instance().log_error("LittleFS Mount Failed for web server. Check partitioning scheme.");
        // Consider notifying mediator to prevent AP mode or fallback
    } else {
        Logger::get_instance().log_info("LittleFS mounted for web server.");
    }

    setup_web_server(); // Setup web server routes
    _server->begin();   // Start the web server
}

void WifiHandler::setup_web_server() {
    // Serve the root path with index.html from LittleFS
    _server->on("/", HTTP_GET, [](AsyncWebServerRequest *request){
        request->send(LittleFS, "/index.html", "text/html");
    });

    // Handle saving of configuration settings via POST request
    _server->on("/save", HTTP_POST, [this](AsyncWebServerRequest *request) {
        Logger::get_instance().log_info("Received new settings from web portal.");
        // In a full implementation, you would parse all parameters from the request here
        // For example:
        // if (request->hasParam("office_ssid", true)) {
        //     Config::get_instance().set_office_wifi_ssid(request->getParam("office_ssid", true)->value().c_str());
        // }
        // ... and so on for all settings

        // As per previous file, just calling save assumes settings are handled internally or not changed via web for now
        Config::get_instance().save(); // Save current config (assuming it might have been set elsewhere or defaults)

        String response_html = "<html><head><title>Settings Saved</title><meta http-equiv='refresh' content='5;url=/'></head><body><h1>Settings Saved!</h1><p>Device will restart in 5 seconds...</p></body></html>";
        request->send(200, "text/html", response_html);

        _mediator->notify(event_t::RESTART_REQUESTED); // Notify mediator to restart device
    });

    // Handle 404 Not Found errors
    _server->onNotFound([](AsyncWebServerRequest *request){
        request->send(404, "text/plain", "Not found");
    });
}

void WifiHandler::log_mac_address() {
    // Ensure WiFi is initialized before attempting to get MAC address
    // It's generally safe to call WiFi.macAddress() even if not connected,
    // as it returns the hardware MAC.
    Logger::get_instance().log_info("Device MAC Address: %s", WiFi.macAddress().c_str());
}