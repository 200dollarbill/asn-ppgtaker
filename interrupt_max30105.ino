#include <Wire.h>
#include "MAX30105.h"

MAX30105 particleSensor;

const byte interruptPin = 27; // LilyGO 27; ESP 2
unsigned long long start_time;
unsigned long long timestamp;
long total_samples = 0;
bool isCollecting = false;

void setup() {
  pinMode(interruptPin, INPUT_PULLUP);
  Serial.begin(115200);
  Serial.println("Initializing MAX30105...");

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30105 not found. Check wiring/power.");
    while (1);
  }
  const int brightness = 20; // max 50mA 
  byte ledBrightness = map(brightness, 0, 50, 0, 255);
  byte sampleAverage = 1;    // 1 sample average
  byte ledMode = 2;          // Red + IR
  int sampleRate = 200;      // 100 samples/sec
  int pulseWidth = 411;
  int adcRange = 16384;

  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);
  particleSensor.enableDATARDY(); // Enable Data Ready interrupt

  Serial.println("Sensor ready. Type 'START' to begin collecting, 'END' to stop.");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command.equalsIgnoreCase("START")) {
      startCollection();
    } 
    else if (command.equalsIgnoreCase("END")) {
      stopCollection();
    }
  }

  // Active collection
  if (isCollecting) {
    if (digitalRead(interruptPin) == LOW) {
      uint32_t red = particleSensor.getRed();
      uint32_t ir = particleSensor.getIR();
      timestamp = micros() - start_time;

      Serial.print(timestamp);
      Serial.print(",");
      Serial.print(red);
      Serial.print(",");
      Serial.println(ir);

      total_samples++;
    }
  }
}

void startCollection() {
  if (isCollecting) {
    Serial.println("Already collecting.");
    return;
  }

  isCollecting = true;
  start_time = micros();
  total_samples = 0;
  Serial.println("STARTED");
}

void stopCollection() {
  if (!isCollecting) {
    Serial.println("Not collecting.");
    return;
  }

  isCollecting = false;

  double duration = double(timestamp) / 1000000;
  double sampling_rate = double(total_samples) / duration;
  Serial.print("DONE. Total samples: ");
  Serial.println(total_samples);
  Serial.print("Total duration (s): ");
  Serial.println(duration);
  Serial.print("Sampling rate (Hz): ");
  Serial.println(sampling_rate);
}
