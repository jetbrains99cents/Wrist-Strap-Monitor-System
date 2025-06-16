#include "peripheral.h"
#include "mediator.h"
#include "ina219.h"
#include "config.h"
#include "logger.h"

void Peripheral::init(Mediator* mediator, Ina219* sensor) {
    _mediator = mediator;
    _sensor = sensor;
}

void Peripheral::begin() {
    Logger::get_instance().log_info("Initializing peripheral module...");
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

    reading_data_t reading;
    reading.voltage = _sensor->get_voltage();
    
    float threshold = Config::get_instance().get_voltage_threshold();

    if (reading.voltage > threshold) {
        reading.status = wrist_strap_status_t::STATUS_PASS;
    } else {
        reading.status = wrist_strap_status_t::STATUS_FAIL;
    }
    
    Logger::get_instance().log_info("New reading: Status=%s, Voltage=%.2fV", 
        (reading.status == wrist_strap_status_t::STATUS_PASS) ? "PASS" : "FAIL", 
        reading.voltage);

    _mediator->notify(event_t::WRIST_STRAP_STATE_UPDATED, &reading);
}