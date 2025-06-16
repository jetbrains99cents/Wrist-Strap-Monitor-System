#include "logger.h"

Logger Logger::instance;

Logger& Logger::get_instance() {
    return instance;
}

void Logger::begin(unsigned long baud_rate) {
    Serial.begin(baud_rate);
    // A small delay to allow serial monitor to connect
    delay(100); 
    _is_active = true;
    log_info("Logger initialized at %lu baud.", baud_rate);
}

void Logger::print_log(const char* level, const char* format, va_list args) {
    if (!_is_active) return;
    
    char buffer[256];
    char message[256];
    
    vsnprintf(message, sizeof(message), format, args);
    
    snprintf(buffer, sizeof(buffer), "[%lu] [%s] %s", millis(), level, message);
    
    Serial.println(buffer);
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