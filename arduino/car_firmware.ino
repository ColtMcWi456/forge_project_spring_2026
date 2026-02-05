/*
RC Maze Car Firmware (Arduino)

This Arduino receives movement commands from a Python program over USB Serial.

Python opens the Arduino serial port (ex: COM3 at 9600 baud) and sends commands
as text lines ending in '\n'.

Command format:
  "F,30\n"  -> forward 30 cm
  "R,90\n"  -> turn right 90 degrees
  "L,90\n"  -> turn left 90 degrees

Example sequence sent from Python:
  F,30
  R,90
  F,15

Arduino reads each line, parses it, and drives the motors accordingly.
Python does NOT control motors directly, it only sends the movement script.

(Optional) Arduino can reply "DONE" after each command so Python knows when
to send the next one.
*/

void setup() {
  Serial.begin(9600);
}

void loop() {
  // 1. Read command from Serial
  // 2. Parse command
  // 3. Execute motor movement
  // 4. Send confirmation back
}