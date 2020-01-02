#!/usr/bin/python
# -*- coding: utf-8 -*-
import config, ecu, log, time, datetime, sys
import pygame, time, os, csv
from pygame.locals import *

#this is part of the repo and there for NOT in config
imgdir = "/home/pi/images/"

#Helper function to draw the given string at coordinate x, y, relative to center.
def drawText(string, x, y, font):
  if font == "readout":
    text = readoutFont.render(string, True, config.WHITE)
  elif font == "label":
    text = labelFont.render(string, True, config.WHITE)
  elif font == "fps":
    text = fpsFont.render(string, True, config.WHITE)
  textRect = text.get_rect()
  textRect.centerx = windowSurface.get_rect().centerx + x
  textRect.centery = windowSurface.get_rect().centery + y
  windowSurface.blit(text, textRect)

# Connect to the ECU.
if not config.debugFlag:
    ecu.ecuThread()

    # Give time for the ECU to connect before we start the GUI.
    while not config.ecuReady:
      time.sleep(.01)

# Load all of our tach images into an array so we can easily access them.
background_dir = 'tach/'
background_files = ['%i.png' % i for i in range(0, config.rpm_grads + 1)]
ground = [pygame.image.load(os.path.join("/home/pi/tach/", file)) for file in background_files]

# Load the M3 PI image.
try:
    img = pygame.image.load(imgdir + "logo-"  + str(config.dtc_error)  + str(config.dtc_pending)  + str(config.dtc_inc) + ".png")
except pygame.error:
    img = pygame.image.load(imgdir + "logo-330.png")
img_button = img.get_rect(topleft = (135, 220))

# Load the M3 PI image.
splasher = pygame.image.load("/home/pi/images/b2f-480x320.png")

# Set up the window.If piTFT flag is set, set up the window for the screen.Else create it normally for use on normal monitor.
if config.piTFT:
    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    pygame.mouse.set_visible(0)
    windowSurface = pygame.display.set_mode(config.RESOLUTION)
else :
    windowSurface = pygame.display.set_mode(config.RESOLUTION, 0, 32)

# Set up fonts
readoutFont = pygame.font.Font("/home/pi/carMon/fonts/TitilliumWeb-Light.ttf", 40)
labelFont = pygame.font.Font("/home/pi/carMon/fonts/TitilliumWeb-Light.ttf", 30)
fpsFont = pygame.font.Font("/home/pi/carMon/fonts/TitilliumWeb-Light.ttf", 20)

# Set the caption.
pygame.display.set_caption('M3 PI')

# Create a clock object to use so we can log every second.
clock = pygame.time.Clock()

# Create the csv log file with the specified header.
log.createLog(["TIME", "RPM", "SPEED", "COOLANT_TEMP", "INTAKE_TEMP", "MAF", "THROTTLE_POS", "ENGINE_LOAD"])

# Debug: Instead of reading from the ECU, read from a log file.
if  config.debugFlag:
    #Read the log file into memory.
    list = log.readLog('/home/pi/carMon/debug/debug_log.csv')
    ##list = log.readLog('/logs/debug_log.csv')
    # Get the length of the log.
    logLength = len(list)

# Run the game loop
while True:
    for event in pygame.event.get():
      if event.type == QUIT:
        #Rename our CSV to include end time.
        log.closeLog()
        # Close the connection to the ECU.
        ecu.connection.close()
        pygame.quit()
        sys.exit()
      if event.type == MOUSEBUTTONDOWN:
        #Toggle the settings flag when the screen is touched.
        config.settingsFlag = not config.settingsFlag
        # kb events splash mode -- will playback the log file again
        config.debugFlag = True

    if not config.debugFlag:
      #Figure out what tach image should be.
      ecu.getTach()

      # Figure out what gear we're *theoretically* in.
      ecu.calcGear(int(float(ecu.rpm)), int(ecu.speed))

    # Clear the screen
    windowSurface.fill(config.BLACK)

    ## ktb this will be a whole new module, dtc.py with def parseDTCs(list,list)
    #probably a 3d array paged by gray, yellow, red, or 2d with 0123 values
    ##all this logic is for test only:
    #if config.dtc_inc = 4 and (config.gui_test_time > config.dbg_rate):
    if config.dtc_inc == 4:
      img = pygame.image.load("/home/pi/images/logo-1111.png")
      ##logo-1110.png
      ##logo-1100.png
      ##logo-1000.png
      #config.dtc_pending == 0
      ##images/logo-2100.png
      #config.dtc_error == 0
      ##logo-3100.png
      ##logo-3000.png
      ###add logic handler here for 3xxx state to check for *ONLY* P0440 in config.dtc or ecu.xxx AND THEN auto clear

    # Load the M3 logo
    windowSurface.blit(img, (windowSurface.get_rect().centerx - 105, windowSurface.get_rect().centery + 60))
    # If the settings button has been pressed:
    if (config.settingsFlag):
      drawText("Settings", -160, -145, "readout")
      # Print all the DTCs
      if ecu.dtc:
        for code, desc in ecu.dtc:
          drawText(code, 0, -80 + (dtc_iter * 50), "label")
          dtc_iter += 1
          if dtc_iter == len(dtc):
            dtc_iter = 0
      else :
        windowSurface.blit(splasher, (0,0))
        drawText("No DTCs found", 140, 140, "label")
    else :
      #Calculate coordinates so tachometer is in middle of screen. (gross)
      coords = (windowSurface.get_rect().centerx - 200, windowSurface.get_rect().centery - 200)

      # Load the tach image
      if ecu.tach_iter >= 0:
        windowSurface.blit(ground[ecu.tach_iter], coords)
      if ecu.tach_iter < 0:
        print "WARNING - negative RPMs are reserved for dark matter engines"
        #let's do something else fun here some other time
        #windowSurface.blit(splasher, (0,0))
        #time.sleep(2.5)

      # Draw the RPM readout and label.
      drawText(str(ecu.rpm), 0, 0, "readout")
      drawText("RPM", 0, 50, "label")

      # Draw the intake temp readout and label.
      drawText(str(ecu.intakeTemp) + "\xb0C", 190, 105, "readout")

      drawText("Intake", 190, 140, "label")
      # Draw the coolant temp readout and label.

      drawText(str(ecu.coolantTemp) + "\xb0C", -160, 105, "readout")
      drawText("Coolant", -170, 140, "label")

      # Draw the gear readout and label.
      drawText(str(ecu.gear), -190, 0, "readout")
      drawText("Gear", -190, 50, "label")

      # Draw the speed readout and label.
      drawText(str(ecu.speed) + " mph", 170, 0, "readout")
      drawText("Speed", 180, 50, "label")

      # Draw the throttle position readout and label.
      drawText(str(ecu.throttlePosition) + " %", 190, -145, "readout")
      drawText("Throttle", 190, -110, "label")

      # Draw the MAF readout and label.
      drawText(str(ecu.MAF) + " g/s", -150, -145, "readout")
      drawText("MAF", -190, -110, "label")

      # Draw the engine load readout and label.
      drawText(str(ecu.engineLoad) + " %", 0, -145, "readout")
      drawText("Load", 0, -110, "label")

      # If debug flag is set, feed fake data so we can test the GUI.
      if config.debugFlag:
        #Debug gui display refresh 10 times a second.
        if config.gui_test_time > config.dbg_rate:
          config.lcd = log.getLogValues(list,logLength)
          config.debugFlag = config.lcd[0]
          #log.getLogValues(list,logLength)
          # Closes after showing all debug values IF config.exitOnDebug is true
          if config.exitOnDebug and not config.debugFlag:
             log.closeLog()
             pygame.quit()
             sys.exit()
          # ktb set conditions to run ecu connect AFTER debug if so desired
          if not config.exitOnDebug and not config.debugFlag:
             # T/T plays debug forever # ktb
             config.debugFlag = False
             # ktb ktb toggled
             config.ecuReady = True
          ##dbg
          ecu.rpm = config.lcd[1]
          ecu.speed = config.lcd[2]
          ecu.coolantTemp =  config.lcd[3]
          ecu.intakeTemp =  config.lcd[4]
          ecu.MAF =  config.lcd[5]
          ecu.throttlePosition =  config.lcd[6]
          ecu.engineLoad =  config.lcd[7]
          ##ktb I will want to log the timing value for my next engine mods...
          #ecu.timingAdvance =  config.lcd[8]
          #ecu.dtc = None
          ecu.calcGear(ecu.rpm, ecu.speed)
          ecu.getTach()
          print "< Tracking realtime variance during debug:"
          ###print config.logIter
          ###print logLength
          print config.gui_test_time
          print ">"
          config.gui_test_time = 0
          if config.dbg_rate == 0:
            config.dbg_rate = config.log_rate // (logLength + 1)
          print config.dbg_rate
          print config.debugFlag

    # Update the clock.
    dt = clock.tick()

    config.time_elapsed_since_last_action += dt
    config.gui_test_time += dt

    # Do logs per the specified asynch interval
    if config.time_elapsed_since_last_action > config.log_rate:
      #Log all of our data.
      data = [datetime.datetime.today().strftime('%Y%m%d%H%M%S'), ecu.rpm, ecu.speed, ecu.coolantTemp, ecu.intakeTemp, ecu.MAF, ecu.throttlePosition, ecu.engineLoad]
      log.updateLog(data)
      # Reset time.
      config.time_elapsed_since_last_action = 0
    # draw the window onto the screen
    pygame.display.update()



