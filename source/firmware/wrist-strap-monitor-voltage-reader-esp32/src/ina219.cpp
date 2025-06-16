#include "ina219.h"
#include "logger.h"

bool Ina219::begin() {
    if (!_ina219.begin()) {
        Logger::get_instance().log_error("Failed to find INA219 chip. Check wiring.");
        return false;
    }
    Logger::get_instance().log_info("INA219 sensor initialized.");
    return true;
}

float Ina219::get_voltage() {
    // Reads the voltage on the Vin+ pin relative to the Vin- pin.
    // In our circuit, this gives us the protected voltage from the monitor.
    return _ina219.getBusVoltage_V();
}