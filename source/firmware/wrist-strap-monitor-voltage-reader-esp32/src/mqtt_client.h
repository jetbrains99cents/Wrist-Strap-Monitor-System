#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#include <AsyncMqttClient.h>

class Mediator;
class Database;

class MqttClient {
public:
    void init(Mediator* mediator, Database* database);
    void connect_to_broker();
    void publish_from_queue();

private:
    void _on_connect(bool sessionPresent);
    void _on_disconnect(AsyncMqttClientDisconnectReason reason);
    void _on_publish(uint16_t packet_id);

    Mediator* _mediator;
    Database* _database;
    AsyncMqttClient _mqtt_client;
    String _last_published_filename;
};

#endif // MQTT_CLIENT_H