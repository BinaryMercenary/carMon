#!/usr/bin/python
import RPi.GPIO as GPIO
import os, time

# Set GPIO pin 17 as input for shutdown signal.
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

# Print message to console.
print("Running shutdown script...")

while True:
  if (GPIO.input(17)):
    os.system("sudo shutdown -h now")
    break
