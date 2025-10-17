save semua data ke folder data yh

# MAX30105

### collector.py
A Python GUI application for collecting, visualizing, and saving PPG data from the MAX30105 sensor via serial communication (Should works on MAX30102 too).

- **Features:**
  - CustomTkinter GUI
  - Select COM port and output filename
  - Start/stop data collection, save to CSV
  - Real-time plotting of RED and IR signals (scrolling last 5 seconds)
- **Usage:**
  1. Connect the MAX30105 device and select the correct COM port.
  2. Enter desired filename.
  3. Click 'Start' to begin collection (5 min, discards first 5s).
  4. Click 'Save' to export data to CSV.
  5. Use 'Send END' to manually stop device collection if needed.

### interrupt_max30105.ino
An Arduino sketch for ESP32/LilyGO boards to collect PPG data from the MAX30105 sensor and communicate with a host via serial.

Connection:

VCC --> 3.3V\
GND --> GND\
SDA --> D21\
SCL --> D22\
INT --> D27

- **Features:**
  - Waits for 'START' command to begin data collection
  - Streams timestamp, RED, and IR values at 100 Hz
  - Stops collection on 'END' command
  - Reports total samples, duration, and sampling rate after stopping
- **Usage:**
  1. ESP32 with MAX30105 connected.
  2. Open serial terminal at 115200 baud.
  3. Send 'START' to begin, 'END' to stop.
  4. Data is streamed in CSV format: `<timestamp>,<red>,<ir>`

### Note: Since MAX30105 configuration is using 2 LED (RED and IR), the sampling rate for each LED is half the sensor sampling rate (e.g. 200Hz -> 100Hz for each LED), adjust accordingly, or just downsample the collected data to 50Hz or desired sampling rate.
### ADJUST SAMPLING RATE ON BOTH collector.py and interrupt_max30105.ino!
---

