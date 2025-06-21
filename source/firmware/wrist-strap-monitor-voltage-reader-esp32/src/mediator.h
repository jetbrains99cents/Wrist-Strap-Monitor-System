#ifndef MEDIATOR_H
#define MEDIATOR_H

#include "enums.h"

class WifiHandler;
class MqttClient;
class ApiRequests;
class OtaHandler;
class Peripheral;
class Database;
class Logger;

class Mediator {
public:
    void init();
    void loop();

    void register_wifi_handler(WifiHandler* handler);
    void register_mqtt_client(MqttClient* client);
    void register_api_requests(ApiRequests* requests);
    void register_ota_handler(OtaHandler* handler);
    void register_peripheral(Peripheral* peripheral);
    void register_database(Database* database);
    void register_logger(Logger* logger);

    void notify(event_t event, void* data = nullptr);

private:
    WifiHandler* _wifi_handler;
    MqttClient* _mqtt_client;
    ApiRequests* _api_requests;
    OtaHandler* _ota_handler;
    Peripheral* _peripheral;
    Database* _database;
    Logger* _logger;

    // --- State Management ---
    bool _is_time_synced = false;
    unsigned long _next_time_sync_attempt_ms = 0;

    bool _is_mqtt_connected = false;
    unsigned long _next_mqtt_connect_attempt_ms = 0;

    // ADDED: Failsafe mechanism variables
    unsigned long _last_online_heartbeat_ms;
};

#endif // MEDIATOR_H