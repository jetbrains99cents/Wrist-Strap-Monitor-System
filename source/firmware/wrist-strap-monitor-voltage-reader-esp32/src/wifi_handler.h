#ifndef WIFI_HANDLER_H
#define WIFI_HANDLER_H

#include <Arduino.h>

class Mediator;
class AsyncWebServer;

class WifiHandler {
public:
    void init(Mediator* mediator);
    void begin_connection_process(); // NEW: Non-blocking trigger
    void start_access_point();
    void loop(); // MODIFIED: Now contains the connection logic

private:
    // NEW: Internal state machine for managing connections
    enum class wifi_state_t {
        IDLE,
        CONNECTING,
        CONNECTED,
        CONNECTION_FAILED
    };

    void setup_web_server();
    void log_mac_address();

    Mediator* _mediator;
    AsyncWebServer* _server;

    wifi_state_t _state = wifi_state_t::IDLE;
    int _current_network_index = 0;
    unsigned long _connection_start_time = 0;
    const long WIFI_CONNECT_TIMEOUT_MS = 20000; // 20 seconds
};

#endif // WIFI_HANDLER_H