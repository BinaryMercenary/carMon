#!/usr/bin/python
import config, time, sys, os
from threading import Thread
import obd
import numpy as np

# Globals
clearDTC = "DTC not cleared"
commandsReturn = "Return a list of all commands"
#incompleteMon = None
pending = None
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
fit = -1
frpd = -1
fuelRate = -1
ltft1 = -1
ltft2 = -1
o2bs1s1 = -1
o2bs1s2 = -1
o2Ltftb1 = -1
o2Ltftb2 = -1
o2Stftb1 = -1
o2Stftb2 = -1
stft1 = -1
stft2 = -1
## this value may belong in config
## it is a delay meant to reduce over polling of the ecu
## since we only see sparse updates every 1.25 seconds (avg 2.125s bulk)
## ktb1 testing if this will improve bluetooth stability - tho errors just need more handling
inECUdelay = 0.001

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
    #ktb2 maybe add a try here to handle the crashes?
    self.daemon = True
    self.start()

  def run(self):
    #time.sleep(inECUdelay)#
    #ktb2 maybe add a try here to handle the crashes?
    global connection
    ports = obd.scan_serial()
    print ports

    # DEBUG: Set debug logging so we can see everything that is happening.
    obd.logger.setLevel(obd.logging.DEBUG)

    # (weakly) Validate elmDevice has been attached to kernel
    try:
      os.stat(config.elmDev)
    except:
      config.elmDev = config.elmAlt
  
    # Connect to the ECU.
    try:
      connection = obd.Async(config.elmDev, 115200, "3", fast=False)
    except:
      print "INFO: 404 - Bluetooth or USB may not be connected?"
      config.tapCount = 404
      sys.exit()

  # Watch everything we care about.
   ## what happens of we "Care" too much?  M-VCI even warns 5 param... ktb3 to test reduced list pls
    ### actually ktb3 I want to make them layers QOS type metrics, with rpm at 1:1 pull and temp at 1:3 runs etc
    ### to see if we can read a bit faster for certain values??

    ### Gear seletion, ATF Temp etc worked with techstream and M-VCI cable / j2534 i
    ### Wonder if I'll need to get into this? ****https://github.com/keenanlaws/Python-J2534-Interface/blob/master/J2534.py
    ##FAILS/crashes ktb  ## connection.watch(obd.commands[0x02][0xB6], callback=self.new_intake_temp) #try running for atf temp?

    #ktb1 these will need wrapped in try/catch statments
    ##bluetooth elm327 failure to read comes back "dimensionless"
    ##Also of intersting note, when the connection dies, last value returns and logs endlessly
    ##There is also an issue that calling DTCs with a tap event currently crashes the routines ktb3
    connection.watch(obd.commands.RPM, callback=self.new_rpm)
    connection.watch(obd.commands.MAF, callback=self.new_MAF)
    connection.watch(obd.commands.INTAKE_TEMP, callback=self.new_intake_temp)
    connection.watch(obd.commands.SPEED, callback=self.new_speed)
    connection.watch(obd.commands.THROTTLE_POS, callback=self.new_throttle_position)
    connection.watch(obd.commands.ENGINE_LOAD, callback=self.new_engine_load)
    connection.watch(obd.commands[0x01][0x05], callback=self.new_coolant_temp)
    #connection.watch(obd.commands.COOLANT_TEMP, callback=self.new_coolant_temp)
    #this is an expensive call but is needed for my warning icons
    #connection.watch(obd.commands.GET_DTC, callback=self.new_dtc)
    #ktb3 add a less frequent level to these
    connection.watch(obd.commands[0x03][0], callback=self.new_dtc)
    connection.watch(obd.commands[0x07][0], callback=self.new_pending)
    # #connection.watch(obd.commands[0x03][0], callback=self.new_pending)

    # works # if config.autoclearSDTC:
    #if (config.autoclearSDTC) and (str(config.currentdtc) == str(config.selectdtc1)):
    if config.currentdtc == config.selectdtc1:
      connection.watch(obd.commands.CLEAR_DTC, callback=self.new_clearDTC)
      os.system('echo "(DTC) AUTOCLEARED select DTC(s) `date +%Y-%m-%d-%H%M.%S`" >> ../logs/INFO.`date +%Y-%m-%d-%H%M`.DTC.LOG')

    if config.deepMetrics:
      connection.watch(obd.commands.TIMING_ADVANCE, callback=self.new_timing_advance)
      ##no support on 2001 is300+elm327## connection.watch(obd.commands.FUEL_INJECT_TIMING, callback=self.new_fuel_inject_timing)

      connection.watch(obd.commands.SHORT_FUEL_TRIM_1, callback=self.new_short_fuel_trim_1)
      connection.watch(obd.commands.SHORT_FUEL_TRIM_2, callback=self.new_short_fuel_trim_2)

      #IF ecu puts out high rpms, assume its an emulator, and assume that emu should not call ltft
      if rpm > -1 and rpm < 9999:
        connection.watch(obd.commands.LONG_FUEL_TRIM_1, callback=self.new_long_fuel_trim_1)
        connection.watch(obd.commands.LONG_FUEL_TRIM_2, callback=self.new_long_fuel_trim_2)
      else:
        ltft1 = -2
        ltft2 = -2

      #Else return dummy -1 values
      #...

      connection.watch(obd.commands.O2_B1S1, callback=self.new_o2_b1s1)
      connection.watch(obd.commands.O2_B1S2, callback=self.new_o2_b1s2)

      ##no support on 2001 is300+elm327## connection.watch(obd.commands.SHORT_O2_TRIM_B1, callback=self.new_short_o2_trim_b1)
      ##no support on 2001 is300+elm327## connection.watch(obd.commands.SHORT_O2_TRIM_B2, callback=self.new_short_o2_trim_b2)

      ##no support on 2001 is300+elm327## connection.watch(obd.commands.LONG_O2_TRIM_B1, callback=self.new_long_o2_trim_b1)
      ##no support on 2001 is300+elm327## connection.watch(obd.commands.LONG_O2_TRIM_B2, callback=self.new_long_o2_trim_b2)

      ##no support on 2001 is300+elm327## connection.watch(obd.commands.FUEL_RAIL_PRESSURE_DIRECT, callback=self.new_fuel_rail_pressure_direct)
      ##no support on 2001 is300+elm327## connection.watch(obd.commands.FUEL_RATE, callback=self.new_fuel_rate)


    ##Thanks again Danny @ Ratchets And Wrenches - u rock https://youtu.be/pIJdCZgEiys
    #short term fuel trim percent will increase of your o2 sensor goes low (lean)
    #long term fuel trim percent will increase gradually as short term fuel trim percent trends
    #stft s/b ~+/-3%,
    #ltft s/b ~+/-3%,
    #sum of ltft + stft sb under ~+/-10%


    # Start the connection.
    connection.start()

    # Set the ready flag so we can boot the GUI.
    if config.gogoGadgetGUI:
      config.ecuReady = True

  def new_commandsReturn(self, r):
    time.sleep(inECUdelay)
    global commandsReturn
    commandsReturn = r
    print "ktb2 tbd output type/format FOR GET~ALL - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print commandsReturn

  def new_clearDTC(self, r):
    time.sleep(inECUdelay)
    global clearDTC
    clearDTC = r
    print "ktb2 tbd output type/format FOR clearDTC - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print clearDTC

  def new_rpm(self, r):
    time.sleep(inECUdelay)
    global rpm
    try:
      rpm = int(r.value.magnitude/config.redline_emu*config.redline_rpm)
    except:
      rpm = -1

  def new_speed(self, r):
    time.sleep(inECUdelay)
    global speed
    try:
      speed = r.value.to("mph")
    except:
      speed = 0 #config.lastSpeed
    else:
      ##~nvm~ this doesn't quite work still, better to explore the datatype and zero it out
      #config.lastSpeed = speed
      speed = int(round(speed.magnitude))

  def new_coolant_temp(self, r):
    time.sleep(inECUdelay)
    global coolantTemp
    coolantTemp = r.value

  def new_intake_temp(self, r):
    time.sleep(inECUdelay)
    global intakeTemp
    intakeTemp = r.value

  def new_MAF(self, r):
    time.sleep(inECUdelay)
    global MAF
    MAF = r.value

  def new_throttle_position(self, r):
    time.sleep(inECUdelay)
    global throttlePosition
    try:
      throttlePosition = int(round(r.value))
    except:
      throttlePosition = 111

  def new_timing_advance(self, r):
    time.sleep(inECUdelay)
    global timingAdvance
    timingAdvance = int(round(r.value))

  def new_engine_load(self, r):
    time.sleep(inECUdelay)
    global engineLoad
    try:
      engineLoad = int(round(r.value))
    except:
      engineLoad = 0

  def new_pending(self, r):
    time.sleep(inECUdelay)
    global pending
    pending = r.value

  def new_dtc(self, r):
    global dtc
    time.sleep(inECUdelay)
    dtc = r.value

  def new_fuel_inject_timing(self, r):
    time.sleep(inECUdelay)
    global fit
    fit = r.value

  def new_short_fuel_trim_1(self, r):
    time.sleep(inECUdelay)
    global stft1
    stft1 = r.value

  def new_short_fuel_trim_2(self, r):
    time.sleep(inECUdelay)
    global stft2
    stft2 = r.value

  def new_long_fuel_trim_1(self, r):
    time.sleep(inECUdelay)
    global ltft1
    ltft1 = r.value

  def new_long_fuel_trim_2(self, r):
    time.sleep(inECUdelay)
    global ltft2
    ltft2 = r.value

  def new_o2_b1s1(self, r):
    time.sleep(inECUdelay)
    global o2bs1s1
    o2bs1s1 = r.value

  def new_o2_b1s2(self, r):
    time.sleep(inECUdelay)
    global o2bs1s2
    o2bs1s2 = r.value

  def new_short_o2_trim_b1(self, r):
    time.sleep(inECUdelay)
    global o2Stftb1
    o2Stftb1 = r.value

  def new_short_o2_trim_b2(self, r):
    time.sleep(inECUdelay)
    global o2Stftb2
    o2Stftb2 = r.value

  def new_long_o2_trim_b1(self, r):
    time.sleep(inECUdelay)
    global o2Ltftb1
    o2Ltftb1 = r.value

  def new_long_o2_trim_b2(self, r):
    time.sleep(inECUdelay)
    global o2Ltftb2
    o2Ltftb2 = r.value

  def new_fuel_rail_pressure_direct(self, r):
    time.sleep(inECUdelay)
    global frpd
    frpd = r.value

  def new_fuel_rate(self, r):
    time.sleep(inECUdelay)
    global fuelRate
    fuelRate = r.value



