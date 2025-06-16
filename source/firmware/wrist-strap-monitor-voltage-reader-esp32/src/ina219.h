#ifndef INA219_H
#define INA219_H

#include <Adafruit_INA219.h>

class Ina219 {
public:
    bool begin();
    float get_voltage();

private:
    Adafruit_INA219 _ina219;
};

#endif // INA219_H