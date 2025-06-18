#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#include <AsyncMqttClient.h>
#include <map>

class Mediator;
class Database;

class MqttClient {
public:
    void init(Mediator* mediator, Database* database);
    void connect_to_broker();
    void publish_from_queue();
    void publish_log(const char* message);
    bool is_connected() const; // ADDED

private:
    void _on_connect(bool sessionPresent);
    void _on_disconnect(AsyncMqttClientDisconnectReason reason);
    void _on_publish(uint16_t packet_id);

    Mediator* _mediator;
    Database* _database;
    AsyncMqttClient _mqtt_client;

    std::map<uint16_t, String> _pending_publishes;
};

#endif // MQTT_CLIENT_H