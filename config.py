#!/usr/bin/python
import ecu
import datetime
import numpy as np

##  Globals.
## Inits to 0
logLength = 0
dtc_iter = 0
time_elapsed_since_last_action = 0
gui_test_time = 0
lastSpeed = 0 #I may not need this var anymore

## Inits to 1
logIter = 1

## Inits to other
## This doesn't have to be 50, as there are only 0-42 graduations,
## but higher value will have flash effect, especially with a padded rpm value
carrier = 21 #ktb test value - cleanup qqq
rpm_grads = 50
redline_rpm = 6450 #proper is300 value
#for normal mode, be sure these match!
redline_emu = 16383 #IMSB5010 http://www.imsapp.com/support.html max rpm=16383
rpm_weight = redline_rpm // rpm_grads
#splash_img = "b2f-480x320.png"
splash_rate = 2500
log_rate = 1000
dbg_rate = 0
## change the above dbg value for faster/slower playback
## otherwise, it is log_rate // logLength
disposition = "No P0440. 1 Inc. Stock AF. Warren Axle Back."

#### <Debug flag pairs
## Normal mode
debugFlag = False
exitOnDebug = False

## Do debug and persist (i.e., live demo)
#debugFlag = True
#exitOnDebug = False

## Do debug & exit
#debugFlag = True
#exitOnDebug = True

## This combo doesn't make sense (yet)
#debugFlag = False
#exitOnDebug = True
#### Debug flag pairs>

## Inits to False
ecuReady = False
settingsFlag = False

## Inits to True (when piTFT is used)
## basically means "FULLSCREEN" if true...
piTFT = False
#piTFT = True
##gogoGadgetGUI = False
gogoGadgetGUI = True
#ktb unc# gogoGadgetGUI = True

##Flag to print via obd call 0100
printCommands = True
##AutoClear if currentdtc matches selectdtc:
autoclearSDTC = False #uses 04: Clear DTCs and Freeze data
###autoclearSDTC = True

#Strings
startTime = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
##elm327 bluetooth reliability is not too hot... ktb9 branch this out and or try high version for odb lib
elmDev = "/dev/rfcomm0"
#
elmDev = "/dev/ttyUSB0"
####for rfcomm, from the cli:
##bluetoothctl
###scan on
###pair 78:9C:E7:04:9C:90
###paired-devices
##quit
##rfcomm bind 0 78:9C:E7:04:9C:90

#init to int 0, too:
dtc_error = 0 # 03: Get DTCs
dtc_pending = 0 # use 07: Get DTCs from the current/last driving cycle
dtc_inc = 0 #use 0600: Supported MIDs [01-20]
#dtc_inc = 4 

#lists
currentdtc = []
selectdtc = ["P0440"]
#selectdtc = ["P0440", "P0446"]
metrics = [0,0,0,0,0,0.11,0,0,0,222]
dumbLog = metrics

### ktb2 attn to piTFT RESOLUTION
## Screen settings
RESOLUTION = (480, 320)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


##M3 specific, tbd
# LUT representing the speeds at each of the five gears. Each entry is +200 RPM, and is directly linked to rpmList.
speedArr = np.array([[4, 7, 10, 14, 17], [5, 9, 14, 18, 23], [7, 11, 17, 23, 28], [8,14, 21, 28, 34], [9, 16, 24, 32, 40], [11, 18, 27, 37, 46], [12, 21, 31, 41, 51], [14, 23, 34, 46, 57], [15, 25, 38, 50, 63], [16, 27, 41, 55, 68], [18, 30, 45, 60,74], [19, 32, 48, 64, 80], [20, 34, 51, 69, 85], [22, 37, 55, 73, 91], [23, 39, 58,78, 97],[24, 41, 62, 83, 102], [26, 43, 65, 87, 108], [27, 46, 69, 92, 114], [28,48, 72, 96, 120], [30, 50, 75, 101, 125], [31, 53, 79, 106, 131], [33, 55, 82, 110,137], [34, 57, 86, 115, 142], [35, 59, 89, 119, 148], [37, 62, 93, 124, 154], [38,64, 96, 129, 159]])

# List of RPM values for above LUT.
rpmList = np.array([750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250,3500, 3750, 4000, 4250, 4500, 4750, 5000, 5250, 5500, 5750, 6000, 6250, 6500, 6750,7000])

## A Duty cycle LUT will be needed here for an active transcooler

