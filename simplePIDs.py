#!/usr/bin/python
import config
from threading import Thread
import obd
import numpy as np

# Globals
clearDTC = "DTC not cleared"
commandsReturn = "Return a list of all commands"
pending = "P9999"
rpm = 0
speed = 0
coolantTemp = 0
intakeTemp = 0
MAF = 0
throttlePosition = 0
timingAdvance = 0
engineLoad = 0
tach_iter = 0
gear = 0
connection = None
dtc = None
rpm_gauge = 0


class ecuThread(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.daemon = True
    self.start()

  def run(self):
    global connection
    ports = obd.scan_serial()
    print ports

    # DEBUG: Set debug logging so we can see everything that is happening.
    obd.logger.setLevel(obd.logging.DEBUG)

    # Connect to the ECU.
    connection = obd.Async("/dev/ttyUSB0", 115200, "3", fast=False)

    # Watch everything we care about.
    ## what happens of we "Care" too much?  M-VCI even warns 5 param... ktb3 to test reduced list pls
    connection.watch(obd.commands.COOLANT_TEMP, callback=self.new_coolant_temp)

    ## if deepscan: #... no need to run DTC checks every cycle ... ktb2
    ##connection.watch(obd.commands.GET_DTC, callback=self.new_dtc)
    ##connection.watch(obd.commands.GET_CURRENT_DTC, callback=self.new_pending)
    ####connection.watch(obd.commands. for Incomplete monitors - tbd ktb2


  def new_coolant_temp(self, r):
    global coolantTemp
    coolantTemp = r.value.magnitude

