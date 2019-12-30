#!/usr/bin/python
import csv, os
from config import *

#Function to create a csv with the specified header.
def createLog(header):
  #Write the header of the csv file.
  with open('/home/pi/logs/' + startTime + '.csv', 'wb') as f:
    w = csv.writer(f)
    w.writerow(header)

# Function to append to the current log file.
def updateLog(data):
  with open('/home/pi/logs/' + startTime + '.csv', 'a') as f:
    w = csv.writer(f)
    w.writerow(data)

# Function to close the log and rename it to include end time.
def closeLog():
  endTime = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
  os.rename('/home/pi/logs/' + startTime + '.csv', '/home/pi/logs/' + startTime + "_" + endTime + '.csv')

# Debug function to read from log file for GUI testing.
def readLog(logFile):
  with open(logFile, 'rb') as f:
    reader = csv.reader(f)
    logList = list(reader)
  return logList

# Debug function that reads from log file and assigns to global values.
def getLogValues(logFile):
  global logIter
  global rpm
  global speed
  global coolantTemp
  global intakeTemp
  global MAF
  global throttlePosition
  global engineLoad
  rpm = int(logFile[logIter][1])
  speed = int(logFile[logIter][2])
  coolantTemp = logFile[logIter][3]
  intakeTemp = logFile[logIter][4]
  MAF = logFile[logIter][5]
  # Cludgy fix for issue where MAF was logged as really log float, causing clipping when displayed on GUI.
  MAF = format(float(MAF), '.2f')
  throttlePosition = logFile[logIter][6]
  engineLoad = logFile[logIter][7]
  logIter += 1
  # Reset iterator.
  if logIter == logLength:
    logIter = 1

