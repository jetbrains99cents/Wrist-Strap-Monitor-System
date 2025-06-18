#ifndef PERIPHERAL_H
#define PERIPHERAL_H

#include "enums.h"

class Mediator;
class Ina219;

struct reading_data_t {
    wrist_strap_status_t status;
    float voltage;
};

class Peripheral {
public:
    void init(Mediator* mediator, Ina219* sensor);
    void begin();
    void read_and_process_data();

private:
    Mediator* _mediator;
    Ina219* _sensor;

    wrist_strap_status_t _last_reported_status;
    wrist_strap_status_t _pending_status;
    unsigned long _state_change_timestamp;
    bool _is_in_debounce_period;
    // MODIFIED: Hardcoded constant is removed
};

#endif // PERIPHERAL_H