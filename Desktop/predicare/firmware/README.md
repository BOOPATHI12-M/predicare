# PrediCare firmware

The sketch emits one newline-delimited JSON measurement every five seconds at
115200 baud. The demo values are intentionally safe placeholders until the
MAX30102 and MLX90614 libraries are wired to the board. Keep the payload shape
identical when replacing the sensor reads.

Install the ESP32 Arduino board package, select the ESP32 board and COM port,
then upload `predicare_esp32.ino`. Close Serial Monitor before the backend opens
the port.
