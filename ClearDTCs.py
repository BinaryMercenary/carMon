#!/usr/bin/python
#from threading import Thread
import obd
import numpy as np

# Globals

global connection
ports = obd.scan_serial()
print ports

# DEBUG: Set debug logging so we can see everything that is happening.
obd.logger.setLevel(obd.logging.DEBUG)

# Connect to the ECU.
#ktb7 bring the elmDev/elmAlt logic over here pls
connection = obd.Async("/dev/ttyUSB0", 115200, "3", fast=False)
##or
#connection = obd.Async("/dev/rfcomm0", 115200, "3", fast=False)
##where you ran a command this boot `sudo rfcomm bind 0 00:1D:A5:02:09:48`
##(sample mac address of paired bluetootctrl elm327 device)

# Start the connection.
connection.start()

def run(self):
  global connection
  #ports = obd.scan_serial()
  #print ports
  ##ktb6 add a manual clear command here pls
  


## a minimally intimidating rendition of ecu.py for showing POC/PIDs and cable to work, etc.
## BUT obd v061 needs hacked - ktbdoc (and obd v071 has some breaking changes)
## the change requires an edit to the obd file in /home/pi/.local/...
## where the count is returned, add a statement that prints the object, as follows:
## ktb7 - Document:

## Attention: a message about 7 Modes found means the cable is seen but NOT talking to your ecu
## your car needs to be at IGN (running, or no.  Granted, the battery drains in less than a few hours...)

