#ifndef OTA_HANDLER_H
#define OTA_HANDLER_H

class Mediator;

class OtaHandler {
public:
    void init(Mediator* mediator);
    void setup_local_ota();
    void check_for_http_update();
    void loop();

private:
    Mediator* _mediator;
};

#endif // OTA_HANDLER_H