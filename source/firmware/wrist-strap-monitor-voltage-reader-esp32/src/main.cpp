#include <Arduino.h>
#include "config.h"
#include "logger.h"
#include "enums.h"
#include "mediator.h"
#include "wifi_handler.h"
#include "mqtt_client.h"
#include "api_requests.h"
#include "ota_handler.h"
#include "peripheral.h"
#include "ina219.h"
#include "database.h"

Config& config = Config::get_instance();
Logger& logger = Logger::get_instance();
Mediator mediator;
WifiHandler wifi_handler;
MqttClient mqtt_client;
ApiRequests api_requests;
OtaHandler ota_handler;
Peripheral peripheral;
Ina219 ina219_sensor;
Database database;

unsigned long last_ota_check_time = 0;
const long OTA_CHECK_INTERVAL = 30 * 1000;

void setup() {
    Serial.begin(115200);
    delay(100);

    logger.begin();
    config.begin();
    database.begin();
    mediator.init();

    mediator.register_logger(&logger);
    mediator.register_database(&database);
    mediator.register_peripheral(&peripheral);
    mediator.register_wifi_handler(&wifi_handler);
    mediator.register_mqtt_client(&mqtt_client);
    mediator.register_api_requests(&api_requests);
    mediator.register_ota_handler(&ota_handler);

    logger.init(&mediator);
    peripheral.init(&mediator, &ina219_sensor);
    wifi_handler.init(&mediator);
    mqtt_client.init(&mediator, &database);
    api_requests.init(&mediator);
    ota_handler.init(&mediator);

    logger.log_info("======================================");
    logger.log_info("Wrist Strap Monitor Device Starting...");
    logger.log_info("Firmware Version: %s", FW_VERSION);
    logger.log_info("======================================");

    peripheral.begin();

    logger.log_info("Checking for saved Wi-Fi configuration...");
    if (config.is_wifi_configured()) {
        mediator.notify(event_t::START_NORMAL_MODE);
    } else {
        mediator.notify(event_t::START_CONFIG_MODE);
    }
}

void loop() {
    ota_handler.loop();
    wifi_handler.loop();
    mediator.loop(); // ADDED: Call the mediator's loop to check for scheduled tasks

    mediator.notify(event_t::SENSOR_READ_REQUESTED);

    unsigned long current_time = millis();
    if (current_time - last_ota_check_time > OTA_CHECK_INTERVAL) {
        last_ota_check_time = current_time;
        mediator.notify(event_t::OTA_CHECK_REQUESTED);
    }

    delay(10);
}