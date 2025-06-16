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
    _mqtt_client.setServer(broker_ip, port);

    // Set other configurations like username/password if needed
    // _mqtt_client.setCredentials(Config::get_instance().get_mqtt_username(), Config::get_instance().get_mqtt_password());
}

void MqttClient::connect_to_broker() {
    Logger::get_instance().log_info("Connecting to MQTT broker...");
    _mqtt_client.connect();
}

void MqttClient::_on_connect(bool sessionPresent) {
    Logger::get_instance().log_info("Connected to MQTT Broker.");
    _mediator->notify(event_t::MQTT_CONNECTED);
    // Immediately try to publish any queued messages upon connection
    publish_from_queue(); 
}

void MqttClient::_on_disconnect(AsyncMqttClientDisconnectReason reason) {
    Logger::get_instance().log_warn("Disconnected from MQTT Broker. Reason: %d", (int)reason);
    _mediator->notify(event_t::MQTT_DISCONNECTED);
}

void MqttClient::publish_from_queue() {
    if (!_mqtt_client.connected() || _database->is_queue_empty()) {
        return;
    }

    Logger::get_instance().log_info("Found items in queue, preparing to publish...");

    String filename;
    if (_database->retrieve_oldest_reading_filename(filename)) {
        char payload_buffer[512];
        if (_database->read_file(filename, payload_buffer, sizeof(payload_buffer))) {
            
            String topic = "devices/" + WiFi.macAddress() + "/data";
            
            uint16_t packet_id = _mqtt_client.publish(topic.c_str(), 1, true, payload_buffer);

            if (packet_id != 0) {
                Logger::get_instance().log_info("Publishing message with packet ID %u from file %s", packet_id, filename.c_str());
                _last_published_filename = filename;
            } else {
                Logger::get_instance().log_warn("MQTT publish failed. Message remains in queue.");
            }
        }
    }
}

void MqttClient::_on_publish(uint16_t packet_id) {
    Logger::get_instance().log_info("MQTT Message with packet ID %u published successfully.", packet_id);
    
    // Message sent, now delete it from the queue
    _database->delete_file(_last_published_filename);
    _last_published_filename = "";
    
    _mediator->notify(event_t::MQTT_MESSAGE_PUBLISHED_SUCCESS);

    // After a successful publish, immediately check if there's more to send.
    // This creates a fast "chain reaction" to clear the queue.
    publish_from_queue();
}