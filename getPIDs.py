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
connection = obd.Async("/dev/ttyUSB0", 115200, "3", fast=False)

# Start the connection.
connection.start()

def run(self):
  global connection
  ports = obd.scan_serial()
  print ports


## a minimally intimidating rendition of ecu.py for showing POC/PIDs and cable to work, etc.
## BUT obd v061 needs hacked - ktbdoc (and obd v071 has some breaking changes)
