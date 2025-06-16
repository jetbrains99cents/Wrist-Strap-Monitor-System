#ifndef ENUMS_H
#define ENUMS_H

// A complete list of all possible events that can be passed through the Mediator.
enum class event_t {
    // System Lifecycle Events
    START_NORMAL_MODE,
    START_CONFIG_MODE,
    RESTART_REQUESTED,

    // Wi-Fi Events
    WIFI_CONNECTED,
    WIFI_CONNECTION_FAILED,
    WIFI_DISCONNECTED,

    // Time Sync Events
    TIME_SYNC_REQUESTED,
    TIME_SYNC_SUCCESS,
    TIME_SYNC_FAILED,

    // MQTT Events
    MQTT_CONNECT_REQUESTED,
    MQTT_CONNECTED,
    MQTT_DISCONNECTED,
    MQTT_MESSAGE_PUBLISHED_SUCCESS,

    // Sensor & Data Events
    WRIST_STRAP_STATE_UPDATED,

    // Periodic Timer Events from main()
    SENSOR_READ_REQUESTED,
    OTA_CHECK_REQUESTED
};

// Represents the interpreted status of the wrist strap.
enum class wrist_strap_status_t {
    STATUS_PASS,
    STATUS_FAIL,
    STATUS_UNKNOWN
};

#endif // ENUMS_H