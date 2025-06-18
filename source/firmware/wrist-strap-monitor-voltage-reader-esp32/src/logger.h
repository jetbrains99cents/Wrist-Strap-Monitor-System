#ifndef LOGGER_H
#define LOGGER_H

#include <Arduino.h>

// Forward declare the Mediator class to avoid circular dependencies
class Mediator;

class Logger {
public:
    static Logger& get_instance();

    void begin(unsigned long baud_rate = 115200);

    // MODIFIED: Logger is now initialized with a pointer to the Mediator
    void init(Mediator* mediator);

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
    Mediator* _mediator = nullptr; // MODIFIED: Pointer to the Mediator
};

#endif // LOGGER_H