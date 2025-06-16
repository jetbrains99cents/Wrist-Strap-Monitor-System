#ifndef WIFI_HANDLER_H
#define WIFI_HANDLER_H

#include <Arduino.h>

class Mediator;
class AsyncWebServer;

class WifiHandler {
public:
    void init(Mediator* mediator);
    bool connect_to_known_networks();
    void start_access_point();
    void loop();

private:
    void setup_web_server();

    Mediator* _mediator;
    AsyncWebServer* _server;
};

#endif // WIFI_HANDLER_H