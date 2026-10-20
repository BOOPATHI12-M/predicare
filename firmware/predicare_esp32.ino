#include <Arduino.h>
#include "config.h"

void setup() {
  Serial.begin(SERIAL_BAUD);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  // Replace these deterministic demo values with MAX30102/MLX90614 reads.
  const float heartRate = 72.0;
  const float spo2 = 98.0;
  const float temperature = 36.6;
  Serial.printf("{\"type\":\"measurement\",\"heart_rate\":%.1f,\"spo2\":%.1f,\"temperature\":%.1f,\"source\":\"device\",\"timestamp\":%lu}\n",
                heartRate, spo2, temperature, millis());
  digitalWrite(LED_GREEN_PIN, HIGH);
  delay(5000);
}
