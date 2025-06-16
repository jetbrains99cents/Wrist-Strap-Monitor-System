#ifndef MEDIATOR_H
#define MEDIATOR_H

#include "enums.h"

// Forward declarations to avoid circular includes
class WifiHandler;
class MqttClient;
class ApiRequests;
class OtaHandler;
class Peripheral;
class Database;
class Logger;

// The Mediator is the central communication hub.
// It receives events and directs commands to the appropriate modules.
class Mediator {
public:
    void init();

    // Registration methods called by main() to wire up the system
    void register_wifi_handler(WifiHandler* handler);
    void register_mqtt_client(MqttClient* client);
    void register_api_requests(ApiRequests* requests);
    void register_ota_handler(OtaHandler* handler);
    void register_peripheral(Peripheral* peripheral);
    void register_database(Database* database);
    void register_logger(Logger* logger);

    // The main notification function
    void notify(event_t event, void* data = nullptr);

private:
    // Pointers to all the modules it controls
    WifiHandler* _wifi_handler;
    MqttClient* _mqtt_client;
    ApiRequests* _api_requests;
    OtaHandler* _ota_handler;
    Peripheral* _peripheral;
    Database* _database;
    Logger* _logger;

    // Timer for MQTT reconnect logic
    unsigned long _mqtt_reconnect_time;
};

#endif // MEDIATOR_H