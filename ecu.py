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

# Function to figure out what tach image we should display based on the RPM.
def getTach():
  global tach_iter
  ##print "###########################################"
  if rpm == 0:
    tach_iter = 0
  elif (rpm > 0) & (rpm < config.redline_rpm):
    tach_iter = rpm // config.rpm_weight
  elif (rpm >= config.redline_rpm):
    tach_iter = 50
  elif (rpm < 0):
    tach_iter = -1

# Given an array and a value, find what array value our value is closest to and return the index of it.
def find_nearest(array, value):
  idx = (np.abs(array-value)).argmin()
  return idx

# Given RPM and speed, calculate what gear we're probably in.
def calcGear(rpm, speed):
  global gear
  # We're stopped, so we're obviously in neutral.
  if speed == 0:
    gear = 'N'

  # We're moving but the RPM is really low, so we must be in neutral.
  # M3 seems to idle at around 800 rpm
  elif (rpm < 875) & (speed > 0):
    gear = 'N'

  # We must be in gear.
  else:
    # Find the index of the closest RPM to our current RPM.
    closestRPMIndx = find_nearest(config.rpmList, rpm)
    # Find the index of the closest speed to our speed.
    closestSpeedIndx = find_nearest(config.speedArr[closestRPMIndx], speed)
    gear = str (closestSpeedIndx + 1)

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
    connection.watch(obd.commands.RPM, callback=self.new_rpm)
    connection.watch(obd.commands.SPEED, callback=self.new_speed)
    connection.watch(obd.commands.COOLANT_TEMP, callback=self.new_coolant_temp)
    connection.watch(obd.commands.INTAKE_TEMP, callback=self.new_intake_temp)
    connection.watch(obd.commands.MAF, callback=self.new_MAF)
    connection.watch(obd.commands.THROTTLE_POS, callback=self.new_throttle_position)
    connection.watch(obd.commands.ENGINE_LOAD, callback=self.new_engine_load)
    connection.watch(obd.commands.TIMING_ADVANCE, callback=self.new_timing_advance)

### ktb0 issue here
###    if printCommands:
###      config.disposition = "ATTN: Commands fetched"
###      printCommands = False
###      print "ecu.py printing 0100 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
###      connection.watch(obd.print_commands, callback=self.new_commandsReturn)
    ## if deepscan: #... no need to run DTC checks every cycle ... ktb2
    connection.watch(obd.commands.GET_DTC, callback=self.new_dtc)
    connection.watch(obd.commands.GET_CURRENT_DTC, callback=self.new_pending)
    #connection.watch(obd.commands. for Incomplete monitors - tbd ktb2
    
    ## ktb2 - would it be safer to clear this at idle/acc mode (only)???
    #config.autoclearSDTC = True
    #config.currentdtc = [""]
    #config.selectdtc  = [""]
    if config.autoclearSDTC and (config.currentdtc  == config.selectdtc):
      config.disposition = "ATTN: DTC cleared"
      print "log these resets, pls - ktb2 - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
      print clearDTC
      print " ^^^^ un-init value"
      connection.watch(obd.commands.CLEAR_DTC, callback=self.new_clearDTC)
      print " vvvv populated value"
      print clearDTC
      print "log these resets, pls - ktb2 - <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

    # Start the connection.
    connection.start()

    # Set the ready flag so we can boot the GUI.
    config.ecuReady = True

  def new_commandsReturn(self, r):
    global commandsReturn
    commandsReturn = r
    print "ktb2 tbd output type/format FOR GET~ALL - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print commandsReturn

  def new_pending(self, r):
    global pending
    pending = r
    print "ktb2 tbd output type/format FOR PENDING - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print pending

  def new_clearDTC(self, r):
    global clearDTC
    clearDTC = r
    print "ktb2 tbd output type/format FOR clearDTC - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print clearDTC

  def new_rpm(self, r):
    global rpm
    rpm = int(r.value.magnitude)

  def new_speed(self, r):
    global speed
    speed = r.value.to("mph")
    speed = int(round(speed.magnitude))

  def new_coolant_temp(self, r):
    global coolantTemp
    coolantTemp = r.value.magnitude

  def new_intake_temp(self, r):
    global intakeTemp
    intakeTemp = r.value.magnitude

  def new_MAF(self, r):
    global MAF
    MAF = r.value.magnitude

  def new_throttle_position(self, r):
    global throttlePosition
    throttlePosition = int(round(r.value.magnitude))

  def new_timing_advance(self, r):
    global timingAdvance
    timingAdvance = int(round(r.value.magnitude))

  def new_engine_load(self, r):
    global engineLoad
    engineLoad = int(round(r.value.magnitude))

  def new_dtc(self, r):
    global dtc
    dtc = r.value

