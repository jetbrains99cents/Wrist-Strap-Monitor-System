#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>
#include <ArduinoJson.h>

#define FW_VERSION "1.3.0"
#define DEVICE_TYPE "WristStrapMonitorKD2001"
#define SCL_PIN 22
#define SDA_PIN 21
#define MAX_SHIFTS 3

struct time_setting_t {
    int hour;
    int minute;
};

struct shift_setting_t {
    char name[50];
    time_setting_t from_time;
    time_setting_t to_time;
};

struct production_plan_setting_t {
    char name[50];
    char date[11];
    time_setting_t from_time;
    time_setting_t to_time;
};

struct device_settings_t {
    char office_wifi_ssid[64];
    char office_wifi_password[64];
    char testing_wifi_ssid[64];
    char testing_wifi_password[64];
    char device_ap_wifi_ssid_prefix[64];
    char device_ap_wifi_password[64];
    char factory_wifi_ssid[64];
    char factory_wifi_password[64];
    char mqtt_broker_ip[64];
    int mqtt_auto_reconnect_delay;
    char mqtt_username[64];
    char mqtt_password[64];
    int mqtt_port;
    int mqtt_ws_port;
    char base_api_url[128];
    float wrist_strap_monitor_output_voltage_threshold;
    shift_setting_t working_time[MAX_SHIFTS];
    production_plan_setting_t production_plan[MAX_SHIFTS];
};

class Config {
public:
    static Config& get_instance();
    void begin();
    bool save();
    bool is_wifi_configured();

    const char* get_office_wifi_ssid() const;
    const char* get_office_wifi_password() const;
    const char* get_testing_wifi_ssid() const;
    const char* get_testing_wifi_password() const;
    const char* get_device_ap_wifi_ssid_prefix() const;
    const char* get_device_ap_wifi_password() const;
    const char* get_factory_wifi_ssid() const;
    const char* get_factory_wifi_password() const;
    const char* get_mqtt_broker_ip() const;
    int get_mqtt_auto_reconnect_delay() const;
    const char* get_mqtt_username() const;
    const char* get_mqtt_password() const;
    int get_mqtt_port() const;
    int get_mqtt_ws_port() const;
    const char* get_base_api_url() const;
    float get_voltage_threshold() const;
    const shift_setting_t* get_working_time() const;
    const production_plan_setting_t* get_production_plan() const;

    void set_office_wifi_ssid(const char* value);
    void set_office_wifi_password(const char* value);
    void set_testing_wifi_ssid(const char* value);
    void set_testing_wifi_password(const char* value);
    void set_device_ap_wifi_ssid_prefix(const char* value);
    void set_device_ap_wifi_password(const char* value);
    void set_factory_wifi_ssid(const char* value);
    void set_factory_wifi_password(const char* value);
    void set_mqtt_broker_ip(const char* value);
    void set_mqtt_auto_reconnect_delay(int value);
    void set_mqtt_username(const char* value);
    void set_mqtt_password(const char* value);
    void set_mqtt_port(int value);
    void set_mqtt_ws_port(int value);
    void set_base_api_url(const char* value);
    void set_voltage_threshold(float value);
    void set_working_time(const JsonArray& shifts);
    void set_production_plan(const JsonArray& plans);

private:
    Config() {};
    Config(const Config&) = delete;
    Config& operator=(const Config&) = delete;

    void load_defaults();
    device_settings_t _settings;
    static Config instance;
};

#endif // CONFIG_H