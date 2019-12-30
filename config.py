#!/usr/bin/python
import ecu
import datetime
import numpy as np

# Globals.
logLength = 0
dtc_iter = 0
time_elapsed_since_last_action = 0
gui_test_time = 0
logIter = 1
ecuReady = False
#debugFlag = False
debugFlag = True
settingsFlag = False
piTFT = True
startTime = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
#ktb attn to piTFT RESOLUTION
RESOLUTION = (480, 320)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# LUT representing the speeds at each of the five gears. Each entry is +200 RPM, and is directly linked to rpmList.
speedArr = np.array([[4, 7, 10, 14, 17], [5, 9, 14, 18, 23], [7, 11, 17, 23, 28], [8,14, 21, 28, 34], [9, 16, 24, 32, 40], [11, 18, 27, 37, 46], [12, 21, 31, 41, 51], [14, 23, 34, 46, 57], [15, 25, 38, 50, 63], [16, 27, 41, 55, 68], [18, 30, 45, 60,74], [19, 32, 48, 64, 80], [20, 34, 51, 69, 85], [22, 37, 55, 73, 91], [23, 39, 58,78, 97],[24, 41, 62, 83, 102], [26, 43, 65, 87, 108], [27, 46, 69, 92, 114], [28,48, 72, 96, 120], [30, 50, 75, 101, 125], [31, 53, 79, 106, 131], [33, 55, 82, 110,137], [34, 57, 86, 115, 142], [35, 59, 89, 119, 148], [37, 62, 93, 124, 154], [38,64, 96, 129, 159]])

# List of RPM values for above LUT.
rpmList = np.array([750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250,3500, 3750, 4000, 4250, 4500, 4750, 5000, 5250, 5500, 5750, 6000, 6250, 6500, 6750,7000])

