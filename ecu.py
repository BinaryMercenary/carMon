#!/usr/bin/python
import config
from threading import Thread
import obd
import numpy as np

# Globals
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
  print "###########################################"
  print config.redline_rpm
  rpm_gauge = config.redline_rpm // config.rpm_grads
  print rpm_gauge
  print config.rpm_weight
  print "###########################################"
  if rpm == 0:
    tach_iter = 0
  elif (rpm >= 0) & (rpm < 200):
    tach_iter = 1
  elif (rpm >= 200) & (rpm < 400):
    tach_iter = 2
  elif (rpm >= 400) & (rpm < 600):
    tach_iter = 3
  elif (rpm >= 600) & (rpm < 800):
    tach_iter = 4
  elif (rpm >= 800) & (rpm < 1000):
    tach_iter = 5
  elif (rpm >= 1000) & (rpm < 1200):
    tach_iter = 6
  elif (rpm >= 1200) & (rpm < 1400):
    tach_iter = 7
  elif (rpm >= 1400) & (rpm < 1600):
    tach_iter = 8
  elif (rpm >= 1600) & (rpm < 1800):
    tach_iter = 9
  elif (rpm >= 1800) & (rpm < 2000):
    tach_iter = 10
  elif (rpm >= 2000) & (rpm < 2200):
    tach_iter = 11
  elif (rpm >= 2200) & (rpm < 2400):
    tach_iter = 12
  elif (rpm >= 2400) & (rpm < 2600):
    tach_iter = 13
  elif (rpm >= 2600) & (rpm < 2800):
    tach_iter = 14
  elif (rpm >= 2800) & (rpm < 3000):
    tach_iter = 15
  elif (rpm >= 3000) & (rpm < 3200):
    tach_iter = 16
  elif (rpm >= 3200) & (rpm < 3400):
    tach_iter = 17
  elif (rpm >= 3400) & (rpm < 3600):
    tach_iter = 18
  elif (rpm >= 3600) & (rpm < 3800):
    tach_iter = 19
  elif (rpm >= 3800) & (rpm < 4000):
    tach_iter = 20
  elif (rpm >= 4000) & (rpm < 4200):
    tach_iter = 21
  elif (rpm >= 4200) & (rpm < 4400):
    tach_iter = 22
  elif (rpm >= 4400) & (rpm < 4600):
    tach_iter = 23
  elif (rpm >= 4600) & (rpm < 4800):
    tach_iter = 24
  elif (rpm >= 4800) & (rpm < 5000):
    tach_iter = 25
  elif (rpm >= 5000) & (rpm < 5200):
    tach_iter = 26
  elif (rpm >= 5200) & (rpm < 5400):
    tach_iter = 27
  elif (rpm >= 5400) & (rpm < 5600):
    tach_iter = 28
  elif (rpm >= 5600) & (rpm < 5800):
    tach_iter = 29
  elif (rpm >= 5800) & (rpm < 6000):
    tach_iter = 30
  elif (rpm >= 6000) & (rpm < 6200):
    tach_iter = 31
  elif (rpm >= 6200) & (rpm < 6400):
    tach_iter = 32
  elif (rpm >= 6400) & (rpm < 6600):
    tach_iter = 33
  elif (rpm >= 6600) & (rpm < 6800):
    tach_iter = 34
  elif (rpm >= 6800) & (rpm < 7000):
    tach_iter = 35
  elif (rpm >= 7000) & (rpm < 7200):
    tach_iter = 36
  elif (rpm >= 7200) & (rpm < 7400):
    tach_iter = 37
  elif (rpm >= 7400) & (rpm < 7600):
    tach_iter = 38
  elif (rpm >= 7600) & (rpm < 7800):
    tach_iter = 39
  elif (rpm >= 7800) & (rpm < 8000):
    tach_iter = 40
  elif (rpm >= 8000):
    tach_iter = 41

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
    connection.watch(obd.commands.RPM, callback=self.new_rpm)
    connection.watch(obd.commands.SPEED, callback=self.new_speed)
    connection.watch(obd.commands.COOLANT_TEMP, callback=self.new_coolant_temp)
    connection.watch(obd.commands.INTAKE_TEMP, callback=self.new_intake_temp)
    connection.watch(obd.commands.MAF, callback=self.new_MAF)
    connection.watch(obd.commands.THROTTLE_POS, callback=self.new_throttle_position)
    connection.watch(obd.commands.ENGINE_LOAD, callback=self.new_engine_load)
    connection.watch(obd.commands.GET_DTC, callback=self.new_dtc)

    # Start the connection.
    connection.start()

    # Set the ready flag so we can boot the GUI.
    config.ecuReady = True

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

