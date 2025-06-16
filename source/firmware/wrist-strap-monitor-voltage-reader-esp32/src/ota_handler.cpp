#include "ota_handler.h"
#include "mediator.h"
#include "logger.h"
#include "config.h"
#include <WiFi.h>
#include <ArduinoOTA.h> // Using the standard, built-in OTA library
#include <HTTPUpdate.h>

void OtaHandler::init(Mediator* mediator) {
    _mediator = mediator;
}

void OtaHandler::setup_local_ota() {
    Logger::get_instance().log_info("Setting up local OTA (espota)...");

    // Set the hostname for the OTA service.
    ArduinoOTA.setHostname(DEVICE_TYPE);

    // Optional: Set a password for OTA updates for security
    // ArduinoOTA.setPassword("your_ota_password");

    ArduinoOTA
        .onStart([]() {
            Logger::get_instance().log_warn("OTA Start! Updating firmware...");
            // Optional: You could notify the mediator here to stop other tasks if needed
        })
        .onEnd([]() {
            Logger::get_instance().log_info("\nOTA End. Rebooting...");
        })
        .onProgress([](unsigned int progress, unsigned int total) {
            Serial.printf("OTA Progress: %u%%\r", (progress / (total / 100)));
        })
        .onError([](ota_error_t error) {
            Logger::get_instance().log_error("OTA Error[%u]: ", error);
            if (error == OTA_AUTH_ERROR) Logger::get_instance().log_error("Auth Failed");
            else if (error == OTA_BEGIN_ERROR) Logger::get_instance().log_error("Begin Failed");
            else if (error == OTA_CONNECT_ERROR) Logger::get_instance().log_error("Connect Failed");
            else if (error == OTA_RECEIVE_ERROR) Logger::get_instance().log_error("Receive Failed");
            else if (error == OTA_END_ERROR) Logger::get_instance().log_error("End Failed");
        });

    ArduinoOTA.begin();

    Logger::get_instance().log_info("Local OTA listener started. Hostname: %s", DEVICE_TYPE);
}

void OtaHandler::loop() {
    // This must be called in the main loop to handle incoming OTA requests.
    ArduinoOTA.handle();
}

void OtaHandler::check_for_http_update() {
    Logger::get_instance().log_info("Checking for firmware updates via HTTP (placeholder)...");
    // Placeholder for remote update logic using the HTTPUpdate library
}