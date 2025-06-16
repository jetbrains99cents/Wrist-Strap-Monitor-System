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

// Create global instances of all our modules
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

// Timers for periodic tasks
unsigned long last_sensor_read_time = 0;
unsigned long last_ota_check_time = 0;
const long SENSOR_READ_INTERVAL = 5000; // 5 seconds
const long OTA_CHECK_INTERVAL = 4 * 60 * 60 * 1000; // 4 hours

void setup() {
    // 1. Initialize Logger first
    logger.begin(115200);
    logger.log_info("======================================");
    logger.log_info("Wrist Strap Monitor Device Starting...");
    logger.log_info("Firmware Version: %s", FW_VERSION);
    logger.log_info("======================================");

    // 2. Initialize core services
    config.begin();
    database.begin();

    // 3. Initialize the Mediator
    mediator.init();

    // 4. "Wire up" the system by registering modules with the Mediator
    logger.log_info("Registering modules with Mediator...");
    mediator.register_logger(&logger);
    mediator.register_database(&database);
    mediator.register_peripheral(&peripheral);
    mediator.register_wifi_handler(&wifi_handler);
    mediator.register_mqtt_client(&mqtt_client);
    mediator.register_api_requests(&api_requests);
    mediator.register_ota_handler(&ota_handler);

    // 5. Initialize modules, injecting dependencies
    logger.log_info("Initializing modules...");
    peripheral.init(&mediator, &ina219_sensor);
    wifi_handler.init(&mediator);
    mqtt_client.init(&mediator, &database);
    api_requests.init(&mediator);
    ota_handler.init(&mediator);

    // 6. Begin hardware-level modules
    peripheral.begin();

    // 7. Make the first critical decision
    logger.log_info("Checking for saved Wi-Fi configuration...");
    if (config.is_wifi_configured()) {
        mediator.notify(event_t::START_NORMAL_MODE);
    } else {
        mediator.notify(event_t::START_CONFIG_MODE);
    }
}

void loop() {
    // Handlers that need to be called on every loop
    ota_handler.loop(); // For ArduinoOTA

    // Non-blocking timers for periodic events
    unsigned long current_time = millis();

    // Trigger sensor read
    if (current_time - last_sensor_read_time > SENSOR_READ_INTERVAL) {
        last_sensor_read_time = current_time;
        mediator.notify(event_t::SENSOR_READ_REQUESTED);
    }

    // Trigger OTA check
    if (current_time - last_ota_check_time > OTA_CHECK_INTERVAL) {
        last_ota_check_time = current_time;
        mediator.notify(event_t::OTA_CHECK_REQUESTED);
    }
}