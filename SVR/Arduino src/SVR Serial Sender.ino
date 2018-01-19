/*
 * Sub vocal recognition sensor Serial printing to python
 * Based off the Arduino ReadAnalogVoltage example.
 */

const int inputPin = A5;  // Change to whatever pin yours is.

void setup() {
  Serial.begin(115200);  // Gotta go fast
}

void loop() {
  Serial.println(analogRead(inputPin));
  Serial.flush();
}
