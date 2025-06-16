#include "config.h"
#include <LittleFS.h>

// This file implements the Config class using the snake_case convention.
// It is now guaranteed to look for the correct "/config.json" file path.

// Define the static instance for the Singleton pattern
Config Config::instance;

// Define a safe size for the JSON document in memory.
const int JSON_DOC_SIZE = 4096;


Config& Config::get_instance() {
    return instance;
}

void Config::begin() {
    if (!LittleFS.begin(true)) {
        Serial.println("FATAL: LittleFS Mount Failed. Check partitioning scheme.");
        return;
    }
    Serial.println("LittleFS mounted successfully.");

    if (LittleFS.exists("/config.json")) {
        Serial.println("Reading config file: /config.json");
        File config_file = LittleFS.open("/config.json", "r");
        if (config_file) {
            JsonDocument doc;
            DeserializationError error = deserializeJson(doc, config_file);
            if (error) {
                Serial.printf("FATAL: deserializeJson() failed: %s. Loading hardcoded defaults.\n", error.c_str());
                load_defaults();
                save();
            } else {
                Serial.println("Successfully parsed config.json. Loading values...");
                // Load all settings from the JSON document
                set_office_wifi_ssid(doc["office_wifi_ssid"] | "");
                set_office_wifi_password(doc["office_wifi_password"] | "");
                set_testing_wifi_ssid(doc["testing_wifi_ssid"] | "");
                set_testing_wifi_password(doc["testing_wifi_password"] | "");
                set_device_ap_wifi_ssid_prefix(doc["device_ap_wifi_ssid_prefix"] | "WristStrapMonitor-");
                set_device_ap_wifi_password(doc["device_ap_wifi_password"] | "password");
                set_factory_wifi_ssid(doc["factory_wifi_ssid"] | "");
                set_factory_wifi_password(doc["factory_wifi_password"] | "");
                set_mqtt_broker_ip(doc["mqtt_broker_ip"] | "127.0.0.1");
                set_mqtt_auto_reconnect_delay(doc["mqtt_auto_reconnect_delay"] | 5000);
                set_mqtt_username(doc["mqtt_username"] | "");
                set_mqtt_password(doc["mqtt_password"] | "");
                set_mqtt_port(doc["mqtt_port"] | 1883);
                set_mqtt_ws_port(doc["mqtt_ws_port"] | 8080);
                set_base_api_url(doc["base_api_url"] | "http://127.0.0.1:3002");
                set_voltage_threshold(doc["wrist_strap_monitor_output_voltage_threshold"] | 1.5f);

                set_working_time(doc["working_time"].as<JsonArray>());
                set_production_plan(doc["production_plan"].as<JsonArray>());
            }
            config_file.close();
        }
    } else {
        Serial.println("Config file not found. Loading defaults and creating file for the first time.");
        load_defaults();
        save();
    }
}

void Config::load_defaults() {
    set_office_wifi_ssid("smv-staff");
    set_office_wifi_password("8Q8wv&vo");
    set_testing_wifi_ssid("kiri");
    set_testing_wifi_password("101conchodom");
    set_device_ap_wifi_ssid_prefix("Wrist-Strap-Monitor-KD2001-AP-");
    set_device_ap_wifi_password("password");
    set_factory_wifi_ssid("");
    set_factory_wifi_password("");
    set_mqtt_broker_ip("172.16.9.183");
    set_mqtt_auto_reconnect_delay(5000);
    set_mqtt_username("");
    set_mqtt_password("");
    set_mqtt_port(1883);
    set_mqtt_ws_port(8080);
    set_base_api_url("http://172.16.9.183:3002");
    set_voltage_threshold(1.5f);

    for (int i = 0; i < MAX_SHIFTS; ++i) {
        snprintf(_settings.working_time[i].name, sizeof(_settings.working_time[i].name), "Shift %d", i + 1);
        _settings.working_time[i].from_time = {8 + i * 5, 0};
        _settings.working_time[i].to_time = {12 + i * 5, 0};
    }
    for (int i = 0; i < MAX_SHIFTS; ++i) {
        snprintf(_settings.production_plan[i].name, sizeof(_settings.production_plan[i].name), "Plan %d", i + 1);
        strlcpy(_settings.production_plan[i].date, "", sizeof(_settings.production_plan[i].date));
        _settings.production_plan[i].from_time = {0, 0};
        _settings.production_plan[i].to_time = {0, 0};
    }
}

bool Config::save() {
    JsonDocument doc;

    doc["office_wifi_ssid"] = _settings.office_wifi_ssid;
    doc["office_wifi_password"] = _settings.office_wifi_password;
    doc["testing_wifi_ssid"] = _settings.testing_wifi_ssid;
    doc["testing_wifi_password"] = _settings.testing_wifi_password;
    doc["device_ap_wifi_ssid_prefix"] = _settings.device_ap_wifi_ssid_prefix;
    doc["device_ap_wifi_password"] = _settings.device_ap_wifi_password;
    doc["factory_wifi_ssid"] = _settings.factory_wifi_ssid;
    doc["factory_wifi_password"] = _settings.factory_wifi_password;
    doc["mqtt_broker_ip"] = _settings.mqtt_broker_ip;
    doc["mqtt_auto_reconnect_delay"] = _settings.mqtt_auto_reconnect_delay;
    doc["mqtt_username"] = _settings.mqtt_username;
    doc["mqtt_password"] = _settings.mqtt_password;
    doc["mqtt_port"] = _settings.mqtt_port;
    doc["mqtt_ws_port"] = _settings.mqtt_ws_port;
    doc["base_api_url"] = _settings.base_api_url;
    doc["wrist_strap_monitor_output_voltage_threshold"] = _settings.wrist_strap_monitor_output_voltage_threshold;

    JsonArray working_time = doc["working_time"].to<JsonArray>();
    for (int i = 0; i < MAX_SHIFTS; ++i) {
        JsonObject shift = working_time.add<JsonObject>();
        shift["name"] = _settings.working_time[i].name;
        JsonObject from_time = shift["from_time"].to<JsonObject>();
        from_time["hour"] = _settings.working_time[i].from_time.hour;
        from_time["minute"] = _settings.working_time[i].from_time.minute;
        JsonObject to_time = shift["to_time"].to<JsonObject>();
        to_time["hour"] = _settings.working_time[i].to_time.hour;
        to_time["minute"] = _settings.working_time[i].to_time.minute;
    }

    JsonArray production_plan = doc["production_plan"].to<JsonArray>();
    for (int i = 0; i < MAX_SHIFTS; ++i) {
        JsonObject plan = production_plan.add<JsonObject>();
        plan["name"] = _settings.production_plan[i].name;
        if (strlen(_settings.production_plan[i].date) > 0) {
            plan["date"] = _settings.production_plan[i].date;
        } else {
            plan["date"] = nullptr;
        }
        JsonObject from_time = plan["from_time"].to<JsonObject>();
        from_time["hour"] = _settings.production_plan[i].from_time.hour;
        from_time["minute"] = _settings.production_plan[i].from_time.minute;
        JsonObject to_time = plan["to_time"].to<JsonObject>();
        to_time["hour"] = _settings.production_plan[i].to_time.hour;
        to_time["minute"] = _settings.production_plan[i].to_time.minute;
    }

    File config_file = LittleFS.open("/config.json", "w");
    if (!config_file) {
        Serial.println("Failed to open config file for writing");
        return false;
    }
    if (serializeJson(doc, config_file) == 0) {
        Serial.println("Failed to write to config file");
        config_file.close();
        return false;
    }
    config_file.close();
    Serial.println("Configuration saved successfully.");
    return true;
}

bool Config::is_wifi_configured() {
    return (strlen(_settings.factory_wifi_ssid) > 0 || strlen(_settings.office_wifi_ssid) > 0 || strlen(_settings.testing_wifi_ssid) > 0);
}

const char* Config::get_office_wifi_ssid() const { return _settings.office_wifi_ssid; }
const char* Config::get_office_wifi_password() const { return _settings.office_wifi_password; }
const char* Config::get_testing_wifi_ssid() const { return _settings.testing_wifi_ssid; }
const char* Config::get_testing_wifi_password() const { return _settings.testing_wifi_password; }
const char* Config::get_device_ap_wifi_ssid_prefix() const { return _settings.device_ap_wifi_ssid_prefix; }
const char* Config::get_device_ap_wifi_password() const { return _settings.device_ap_wifi_password; }
const char* Config::get_factory_wifi_ssid() const { return _settings.factory_wifi_ssid; }
const char* Config::get_factory_wifi_password() const { return _settings.factory_wifi_password; }
const char* Config::get_mqtt_broker_ip() const { return _settings.mqtt_broker_ip; }
int Config::get_mqtt_auto_reconnect_delay() const { return _settings.mqtt_auto_reconnect_delay; }
const char* Config::get_mqtt_username() const { return _settings.mqtt_username; }
const char* Config::get_mqtt_password() const { return _settings.mqtt_password; }
int Config::get_mqtt_port() const { return _settings.mqtt_port; }
int Config::get_mqtt_ws_port() const { return _settings.mqtt_ws_port; }
const char* Config::get_base_api_url() const { return _settings.base_api_url; }
float Config::get_voltage_threshold() const { return _settings.wrist_strap_monitor_output_voltage_threshold; }
const shift_setting_t* Config::get_working_time() const { return _settings.working_time; }
const production_plan_setting_t* Config::get_production_plan() const { return _settings.production_plan; }

void Config::set_office_wifi_ssid(const char* value) { strlcpy(_settings.office_wifi_ssid, value, sizeof(_settings.office_wifi_ssid)); }
void Config::set_office_wifi_password(const char* value) { strlcpy(_settings.office_wifi_password, value, sizeof(_settings.office_wifi_password)); }
void Config::set_testing_wifi_ssid(const char* value) { strlcpy(_settings.testing_wifi_ssid, value, sizeof(_settings.testing_wifi_ssid)); }
void Config::set_testing_wifi_password(const char* value) { strlcpy(_settings.testing_wifi_password, value, sizeof(_settings.testing_wifi_password)); }
void Config::set_device_ap_wifi_ssid_prefix(const char* value) { strlcpy(_settings.device_ap_wifi_ssid_prefix, value, sizeof(_settings.device_ap_wifi_ssid_prefix)); }
void Config::set_device_ap_wifi_password(const char* value) { strlcpy(_settings.device_ap_wifi_password, value, sizeof(_settings.device_ap_wifi_password)); }
void Config::set_factory_wifi_ssid(const char* value) { strlcpy(_settings.factory_wifi_ssid, value, sizeof(_settings.factory_wifi_ssid)); }
void Config::set_factory_wifi_password(const char* value) { strlcpy(_settings.factory_wifi_password, value, sizeof(_settings.factory_wifi_password)); }
void Config::set_mqtt_broker_ip(const char* value) { strlcpy(_settings.mqtt_broker_ip, value, sizeof(_settings.mqtt_broker_ip)); }
void Config::set_mqtt_auto_reconnect_delay(int value) { _settings.mqtt_auto_reconnect_delay = value; }
void Config::set_mqtt_username(const char* value) { strlcpy(_settings.mqtt_username, value, sizeof(_settings.mqtt_username)); }
void Config::set_mqtt_password(const char* value) { strlcpy(_settings.mqtt_password, value, sizeof(_settings.mqtt_password)); }
void Config::set_mqtt_port(int value) { _settings.mqtt_port = value; }
void Config::set_mqtt_ws_port(int value) { _settings.mqtt_ws_port = value; }
void Config::set_base_api_url(const char* value) { strlcpy(_settings.base_api_url, value, sizeof(_settings.base_api_url)); }
void Config::set_voltage_threshold(float value) { _settings.wrist_strap_monitor_output_voltage_threshold = value; }

void Config::set_working_time(const JsonArray& shifts) {
    if (shifts.isNull()) return;
    int i = 0;
    for (JsonObject shift : shifts) {
        if (i >= MAX_SHIFTS) break;
        strlcpy(_settings.working_time[i].name, shift["name"] | "", sizeof(_settings.working_time[i].name));
        _settings.working_time[i].from_time.hour = shift["from_time"]["hour"] | 0;
        _settings.working_time[i].from_time.minute = shift["from_time"]["minute"] | 0;
        _settings.working_time[i].to_time.hour = shift["to_time"]["hour"] | 0;
        _settings.working_time[i].to_time.minute = shift["to_time"]["minute"] | 0;
        i++;
    }
}

void Config::set_production_plan(const JsonArray& plans) {
    if (plans.isNull()) return;
    int i = 0;
    for (JsonObject plan : plans) {
        if (i >= MAX_SHIFTS) break;
        strlcpy(_settings.production_plan[i].name, plan["name"] | "", sizeof(_settings.production_plan[i].name));
        strlcpy(_settings.production_plan[i].date, plan["date"] | "", sizeof(_settings.production_plan[i].date));
        _settings.production_plan[i].from_time.hour = plan["from_time"]["hour"] | 0;
        _settings.production_plan[i].from_time.minute = plan["from_time"]["minute"] | 0;
        _settings.production_plan[i].to_time.hour = plan["to_time"]["hour"] | 0;
        _settings.production_plan[i].to_time.minute = plan["to_time"]["minute"] | 0;
        i++;
    }
}