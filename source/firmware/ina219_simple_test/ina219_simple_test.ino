#include <Wire.h>
#include <Adafruit_INA219.h>

// Create an INA219 sensor object
Adafruit_INA219 ina219;

void setup() {
  // Start the Serial Monitor at 115200 baud rate
  Serial.begin(115200);
  while (!Serial) {
      // wait for serial port to connect. Needed for native USB port only
  }

  Serial.println("INA219 Voltage Sensor Test");
  Serial.println("--------------------------");

  // Initialize the INA219.
  // By default, the library assumes the sensor is at I2C address 0x40.
  // If your sensor has a different address, you can pass it to begin(): ina219.begin(0x41)
  if (!ina219.begin()) {
    Serial.println("Failed to find INA219 chip. Check your wiring!");
    while (1) { delay(10); } // Halt forever if sensor not found
  }

  Serial.println("INA219 sensor found and initialized.");
}

void loop() {
  // Declare variables to hold the measurements
  float bus_voltage = 0;

  // Read the "Bus Voltage". This measures the voltage on the Vin- pin relative to GND.
  // Since you have Vin- connected to GND, this effectively reads the voltage at Vin+.
  bus_voltage = ina219.getBusVoltage_V();

  // Print the results to the Serial Monitor
  Serial.print("Bus Voltage: ");
  Serial.print(bus_voltage);
  Serial.println(" V");

  // Wait for a second before taking the next measurement
  delay(1000);
}