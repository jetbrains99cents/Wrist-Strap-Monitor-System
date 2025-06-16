#ifndef LOGGER_H
#define LOGGER_H

#include <Arduino.h>

class Logger {
public:
    static Logger& get_instance();

    void begin(unsigned long baud_rate = 115200);
    
    void log_info(const char* format, ...);
    void log_warn(const char* format, ...);
    void log_error(const char* format, ...);

private:
    Logger() {};
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    void print_log(const char* level, const char* format, va_list args);

    static Logger instance;
    bool _is_active = false;
};

#endif // LOGGER_H