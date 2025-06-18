#include "peripheral.h"
#include "mediator.h"
#include "ina219.h"
#include "config.h"
#include "logger.h"

void Peripheral::init(Mediator* mediator, Ina219* sensor) {
    _mediator = mediator;
    _sensor = sensor;
    _last_reported_status = wrist_strap_status_t::STATUS_UNKNOWN;
    _pending_status = wrist_strap_status_t::STATUS_UNKNOWN;
    _is_in_debounce_period = false;
    _state_change_timestamp = 0;
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
        return;
    }

    reading_data_t current_reading;
    current_reading.voltage = _sensor->get_voltage();

    // MODIFIED: Get latest config values on every check
    float threshold = Config::get_instance().get_fail_voltage_threshold();
    long debounce_ms = Config::get_instance().get_debounce_duration() * 1000;

    if (current_reading.voltage > threshold) {
        current_reading.status = wrist_strap_status_t::STATUS_PASS;
    } else {
        current_reading.status = wrist_strap_status_t::STATUS_FAIL;
    }

    if (_is_in_debounce_period) {
        if (current_reading.status != _pending_status) {
            _is_in_debounce_period = false;
            Logger::get_instance().log_info("State change reverted within debounce period. Cancelling event.");
        } else if (millis() - _state_change_timestamp > debounce_ms) {
            _last_reported_status = _pending_status;
            _is_in_debounce_period = false;

            Logger::get_instance().log_warn("State change CONFIRMED to %s. Notifying Mediator.",
                (_last_reported_status == wrist_strap_status_t::STATUS_PASS) ? "PASS" : "FAIL");

            _mediator->notify(event_t::WRIST_STRAP_STATE_UPDATED, &current_reading);
        }
    } else {
        if (current_reading.status != _last_reported_status) {
            Logger::get_instance().log_info("Potential state change detected. Starting %ldms debounce timer...", debounce_ms);
            _is_in_debounce_period = true;
            _pending_status = current_reading.status;
            _state_change_timestamp = millis();
        }
    }
}