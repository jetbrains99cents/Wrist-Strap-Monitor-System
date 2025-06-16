#include "peripheral.h"
#include "mediator.h"
#include "ina219.h"
#include "config.h"
#include "logger.h"

void Peripheral::init(Mediator* mediator, Ina219* sensor) {
    _mediator = mediator;
    _sensor = sensor;
    _last_reported_status = wrist_strap_status_t::STATUS_UNKNOWN; // Initialize last reported status
}

void Peripheral::begin() {
    Logger::get_instance().log_info("Initializing peripheral module.");
    if (_sensor) {
        _sensor->begin();
    } else {
        Logger::get_instance().log_error("INA219 sensor driver not provided to Peripheral.");
    }
}

void Peripheral::read_and_process_data() {
    if (!_sensor) {
        Logger::get_instance().log_error("Cannot read data, sensor is not initialized.");
        return;
    }

    reading_data_t current_reading;
    current_reading.voltage = _sensor->get_voltage();

    float threshold = Config::get_instance().get_voltage_threshold();

    if (current_reading.voltage > threshold) {
        current_reading.status = wrist_strap_status_t::STATUS_PASS;
    } else {
        current_reading.status = wrist_strap_status_t::STATUS_FAIL;
    }

    // Log every reading, regardless of whether it's sent
    Logger::get_instance().log_info("New measurement: Status=%s, Voltage=%.2fV",
        (current_reading.status == wrist_strap_status_t::STATUS_PASS) ? "PASS" :
        (current_reading.status == wrist_strap_status_t::STATUS_FAIL) ? "FAIL" : "UNKNOWN",
        current_reading.voltage);

    // Only notify Mediator if the status has changed
    if (current_reading.status != _last_reported_status) {
        Logger::get_instance().log_info("Status change detected. Notifying Mediator.");
        _last_reported_status = current_reading.status; // Update last reported status
        _mediator->notify(event_t::WRIST_STRAP_STATE_UPDATED, &current_reading);
    }
}