#include "logger.h"
#include "mediator.h" // Include Mediator to call notify

Logger Logger::instance;

Logger& Logger::get_instance() {
    return instance;
}

void Logger::begin(unsigned long baud_rate) {
    Serial.begin(baud_rate);
    delay(100);
    _is_active = true;
}

// MODIFIED: Implementation for the new init method
void Logger::init(Mediator* mediator) {
    _mediator = mediator;
    log_info("Logger initialized and connected to Mediator.");
}

// MODIFIED: This function now notifies the Mediator after printing
void Logger::print_log(const char* level, const char* format, va_list args) {
    char message[256];
    vsnprintf(message, sizeof(message), format, args);

    // 1. Always print to the local Serial port if it's active
    if (_is_active) {
        char buffer[256];
        snprintf(buffer, sizeof(buffer), "[%lu] [%s] %s", millis(), level, message);
        Serial.println(buffer);
    }

    // 2. Notify the Mediator that a log was created.
    // The Mediator will decide if it needs to be sent over MQTT.
    if (_mediator != nullptr) {
        _mediator->notify(event_t::LOG_MESSAGE_CREATED, (void*)message);
    }
}

void Logger::log_info(const char* format, ...) {
    va_list args;
    va_start(args, format);
    print_log("INFO", format, args);
    va_end(args);
}

void Logger::log_warn(const char* format, ...) {
    va_list args;
    va_start(args, format);
    print_log("WARN", format, args);
    va_end(args);
}

void Logger::log_error(const char* format, ...) {
    va_list args;
    va_start(args, format);
    print_log("ERROR", format, args);
    va_end(args);
}