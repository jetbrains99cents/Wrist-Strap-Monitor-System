#include "mqtt_client.h"
#include "mediator.h"
#include "database.h"
#include "config.h"
#include "logger.h"
#include <WiFi.h>

void MqttClient::init(Mediator* mediator, Database* database) {
    _mediator = mediator;
    _database = database;

    _mqtt_client.onConnect(std::bind(&MqttClient::_on_connect, this, std::placeholders::_1));
    _mqtt_client.onDisconnect(std::bind(&MqttClient::_on_disconnect, this, std::placeholders::_1));
    _mqtt_client.onPublish(std::bind(&MqttClient::_on_publish, this, std::placeholders::_1));

    const char* broker_ip = Config::get_instance().get_mqtt_broker_ip();
    uint16_t port = Config::get_instance().get_mqtt_port();

    Logger::get_instance().log_info("Setting MQTT server to: %s:%d", broker_ip, port);

    _mqtt_client.setServer(broker_ip, port);
}

void MqttClient::connect_to_broker() {
    if (_mqtt_client.connected()) {
        return;
    }
    _mqtt_client.connect();
}

bool MqttClient::is_connected() const {
    return _mqtt_client.connected();
}

void MqttClient::_on_connect(bool sessionPresent) {
    _mediator->notify(event_t::MQTT_CONNECTED);
}

void MqttClient::_on_disconnect(AsyncMqttClientDisconnectReason reason) {
    // This function's only job is to notify the mediator.
    // The mediator handles all retry scheduling.
    _mediator->notify(event_t::MQTT_DISCONNECTED);
}

void MqttClient::publish_from_queue() {
    if (!_mqtt_client.connected() || _database->is_queue_empty()) {
        return;
    }

    if (_pending_publishes.size() >= 5) {
        Logger::get_instance().log_warn("Too many unconfirmed MQTT messages pending. Waiting...");
        return;
    }

    String filename;
    if (_database->retrieve_oldest_reading_filename(filename)) {
        char payload_buffer[512];
        if (_database->read_file(filename, payload_buffer, sizeof(payload_buffer))) {

            String topic_prefix = Config::get_instance().get_mqtt_topic_prefix();
            String topic = topic_prefix + WiFi.macAddress();

            Logger::get_instance().log_info("Attempting to publish to topic: %s", topic.c_str());
            uint16_t packet_id = _mqtt_client.publish(topic.c_str(), 1, true, payload_buffer);

            if (packet_id != 0) {
                _pending_publishes[packet_id] = filename;
                Logger::get_instance().log_info("Publishing message with packet ID %u from file %s", packet_id, filename.c_str());
            } else {
                Logger::get_instance().log_warn("MQTT publish failed locally. Message remains in queue.");
            }
        }
    }
}

void MqttClient::publish_log(const char* message) {
    if (!_mqtt_client.connected()) {
        return;
    }

    String topic_prefix = Config::get_instance().get_mqtt_topic_prefix();
    String topic = topic_prefix + "log/" + WiFi.macAddress();

    JsonDocument doc;
    doc["message"] = message;
    char json_buffer[256];
    serializeJson(doc, json_buffer);

    _mqtt_client.publish(topic.c_str(), 0, false, json_buffer);
}


void MqttClient::_on_publish(uint16_t packet_id) {
    Logger::get_instance().log_info("MQTT Message with packet ID %u acknowledged by broker.", packet_id);

    auto it = _pending_publishes.find(packet_id);
    if (it != _pending_publishes.end()) {
        String filename_to_delete = it->second;
        _database->delete_file(filename_to_delete);
        _pending_publishes.erase(it);

        _mediator->notify(event_t::MQTT_MESSAGE_PUBLISHED_SUCCESS);
        publish_from_queue();
    } else {
        if (packet_id != 0) {
            Logger::get_instance().log_warn("Received publish confirmation for an unknown packet ID: %u", packet_id);
        }
    }
}