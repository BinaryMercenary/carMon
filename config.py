#!/usr/bin/python
import ecu
import datetime
import numpy as np

##ktb0 hot ticket items:
#ktb3 - road time needed!
#ktb 2 - why does P0440 show up as C0600??? (in 07/pending mode)
#ktb 1 - INC status for the gray indicator discs
#I'm afraid the emulator is not fullfilling it's role 100% here :/ - looked so promising but too many bugs and speed issues

##  Globals.
## Inits to 0
logLength = 0
dtc_iter = 0
time_elapsed_since_last_action = 0
tapTimer = 0
tapCount = 0
holdCount = 0
gui_test_time = 0
lastSpeed = 0 #I may not need this var anymore

## Inits to 1
logIter = 1

## Inits to other
## This doesn't have to be 50, as there are only 0-42 graduations,
## but higher value will have flash effect, especially with a padded rpm value
rpm_grads = 50
tapTimerWindow = 900
##ect/engine coolant temperature WARNING threshold (will flash red)
ectWarn = 96

redline_rpm = 6450 #proper is300 value
#for normal mode, be sure these match!
redline_emu = 6450
#redline_emu = 16383 #IMSB5010 http://www.imsapp.com/support.html max rpm=16383

rpm_weight = redline_rpm // rpm_grads
i_have_an_emu_and_might_use_it = True
#splash_img = "b2f-480x320.png"
splash_rate = 2500
log_rate = 1000
dbg_rate = 0
## change the above dbg value for faster/slower playback
## otherwise, it is log_rate // logLength
disposition = ""
buildInfo = "Stock AF. Warren Axle Back."

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

## Inits to True (when fullscreen is used)
fullscreen = True
##gogoGadgetGUI = False
gogoGadgetGUI = True

logMetrics = True

#Set this value to False for fewer/faster metrics
deepMetrics = True

##Flag to print via obd call 0100
printCommands = True
##AutoClear if currentdtc matches selectdtc:
#uses 04: Clear DTCs and Freeze data
autoclearSDTC = True
autoclearECU = False

#clear the matched selectdtc1 regardless of how pending(s)
ignorePending = True

#Strings
startTime = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
##elm327 bluetooth reliability is not too hot... ktb9 branch this out and or try high version for odb lib
elmDev = "/dev/ttyUSB0"
elmAlt = "/dev/rfcomm0"
#The above setup assumes USB is primary device, and if absent, elmAlt is the standin
#Since we gratuitously bind rfcomm0, ttyUSB is the safe/logical primary as ecu.py is written

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
piTemp = 0
piVolt = 0

##These should probably be lists, not strings BUT really, how many codes do you want to ignore?
##You can ignore more than one if you know the order they present it, or feel free to do some code
#for single code matching we could do a 4-char string P044 matcher for any single P044X catch-all ktb88 
selectdtc1 = "P0440"
# #selectdtc1 = "U0101B0102C0032" #debug on ecu for matching
#ktb0 I need to sub this C0600 for P0440 - all other tools show P0440 but something in this setup is getting a C0600
substituteCodeFrom = "C0600"
substituteCodeTo = "P0440"
selectPending1 = "P0440P0446"
currentdtc = ""
currentPending = ""
currentIncomplete = ""

piWlan = "1.2.3.4"
piEth = "1.2.3.4"

#lists
# # currentdtc = []
# # selectdtc = ["P0440"]
#selectdtc = ["P0440", "P0446"]
metrics = [0,0,0,0,0,0.11,0,0,0,222]
dummyMetrics = metrics

### ktb2 attn to fullscreen RESOLUTION
## Screen settings
RESOLUTION = (480, 320)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255,112,00)
LIME = (102,255,00)
CHARCOAL = (54,69,79)

## the IS300 is a prettty close match to GW's m3 lut here, with this gearing and rear-diff spec:
#  1st 3.357	2nd 2.180	3rd 1.424	4th 1.000	5th 0.753	R3.431	3.91 final (2001, AT)*
#  1st 3.566	2nd 2.056	3rd 1.384	4th 1.000	5th 0.85	R4.091	3.73 final (2001, MT)*
#  1st 4.20	2nd 2.49	3rd 1.66	4th 1.24	5th 1.0 	RX.YYY	3.23 final 1997 BMW M3ii**
#    
#  it might be worth making an LUT generator function, if any of this gearing info is worth keeping around
#  *ESPECIALLY since tire diamater is dynamic and needs figured in
#  **336.13 (in/sec*pi for GW's EU dogleg)
#  on that regard, having a large red flashing slip-indicator would be great for people with AT's. ktb999

##M3 specific, tbd
# LUT representing the speeds at each of the five gears. Each entry is +200 RPM, and is directly linked to rpmList.
speedArr = np.array([[4, 7, 10, 14, 17], [5, 9, 14, 18, 23], [7, 11, 17, 23, 28], [8,14, 21, 28, 34], [9, 16, 24, 32, 40], [11, 18, 27, 37, 46], [12, 21, 31, 41, 51], [14, 23, 34, 46, 57], [15, 25, 38, 50, 63], [16, 27, 41, 55, 68], [18, 30, 45, 60,74], [19, 32, 48, 64, 80], [20, 34, 51, 69, 85], [22, 37, 55, 73, 91], [23, 39, 58,78, 97],[24, 41, 62, 83, 102], [26, 43, 65, 87, 108], [27, 46, 69, 92, 114], [28,48, 72, 96, 120], [30, 50, 75, 101, 125], [31, 53, 79, 106, 131], [33, 55, 82, 110,137], [34, 57, 86, 115, 142], [35, 59, 89, 119, 148], [37, 62, 93, 124, 154], [38,64, 96, 129, 159]])

# List of RPM values for above LUT.
rpmList = np.array([750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250,3500, 3750, 4000, 4250, 4500, 4750, 5000, 5250, 5500, 5750, 6000, 6250, 6500, 6750,7000])

## A Duty cycle LUT will be needed here for an active transcooler

