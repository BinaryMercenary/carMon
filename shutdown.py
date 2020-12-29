#!/usr/bin/python
import RPi.GPIO as GPIO
import os, time

#You can add a switch here to do this
#but I've been a cowboy with 100's of unsafe shutdowns and ntf

## Moved from pin 17 to pin 13 as the ili9486 screen takes up all pins 1-26
# Set GPIO pin 13 as input for shutdown signal.
GPIO.setmode(GPIO.BCM)
GPIO.setup(13, GPIO.IN)

# Print message to console.
print("Running shutdown script...")

while True:
  if (GPIO.input(17)):
    os.system('sudo shutdown -h now')
    break
