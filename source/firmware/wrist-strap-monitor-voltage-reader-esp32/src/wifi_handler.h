#ifndef WIFI_HANDLER_H
#define WIFI_HANDLER_H

#include <Arduino.h>
#include <ESPAsyncWebServer.h> // Include for AsyncWebServer

class Mediator;

class WifiHandler {
public:
    void init(Mediator* mediator);
    bool connect_to_known_networks();
    void start_access_point();
    void log_mac_address(); // Declaration for logging MAC address
    void loop(); // Added for consistency, even if empty for async server

private:
    void setup_web_server(); // Declare this private helper method

    Mediator* _mediator;
    AsyncWebServer* _server; // Pointer to the AsyncWebServer instance
};

#endif // WIFI_HANDLER_H