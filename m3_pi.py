#!/usr/bin/python
# -*- coding: utf-8 -*-
import config, ecu, log, time, datetime, sys
import pygame, time, os, csv
import obd
from pygame.locals import *

##ktb4 if you want to move this to config, maybe add some logic
#where RPMP 0 means never use RPMP, else do use RPMP
RPMP = 0;

#this is part of the repo and there for NOT in config
imgdir = "/home/pi/carMon/images/"


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
    try:
      launchy = ecu.ecuThread()
    except:
      #shoot, this doesn't work -- you need some kind of watchdog or sth tricky ktb5
      print "It's just too much, I can't handle it anymore -- anon"
      sys.exit()

    # Give time for the ECU to connect before we start the GUI.
    while not config.ecuReady:
      ## a careful if statement with a toggler var could get me flashing gauge at startup qqq ktb6
      time.sleep(.03) #is 100fps a goal when GW's POC was 55fps? ktb4 slow the roll?
      ##if you want to watch values write them to the logs and use watch with ls -t and tail #ktbdoc
# Load all of our tach images into an array so we can easily access them.
background_dir = 'tach/'
background_files = ['%i.png' % i for i in range(0, config.rpm_grads + 1)]
ground = [pygame.image.load(os.path.join("/home/pi/carMon/images/", file)) for file in background_files]


# Load the Logo image.
splasher = pygame.image.load("/home/pi/carMon/images/b2f-480x320.png")

# Set up the window.If fullscreen flag is set, set up the window for the screen.Else create it normally for use on normal monitor.
##small screen + fullscreen
## I was going to assigned two-taps to toggle fullscreen BUT why? Exit is better
if config.fullscreen:
    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    pygame.mouse.set_visible(0)
    windowSurface = pygame.display.set_mode(config.RESOLUTION, FULLSCREEN)
#assume larger LCD and run windowed
else :
    os.putenv('SDL_FBDEV', '/dev/fb1')
    pygame.init()
    pygame.mouse.set_visible(0)
    windowSurface = pygame.display.set_mode(config.RESOLUTION)
    ## Not sure what GW was doing with this original else:
    # #windowSurface = pygame.display.set_mode(config.RESOLUTION, 0, 32)

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
    #ecu.connection.stop
    #time.sleep(0.375)
    #ecu.connection.start
    if ecu.dtc:
      config.dtc_error = len(ecu.dtc)
    else:
      config.dtc_error = 0

    if ecu.pending:
      config.dtc_pending = len(ecu.pending)
    else:
      config.dtc_pending = 0

    #if config.incompleteMon:
    #  config.dtc_inc = len(ecu.incompleteMon)
    #else:
    #  config.dtc_inc = 0



    #ktb1 I need to make the disposition string functions ALL += pls

    # Load the Logo image.
    try:
      img = pygame.image.load(imgdir + "logo-"  + str(config.dtc_error)  + str(config.dtc_pending)  + str(config.dtc_inc) + ".png")
    except pygame.error:
      img = pygame.image.load(imgdir + "logo-330.png")
    img_button = img.get_rect(topleft = (135, 220))


    #this will need wrapped up better pls ktb
    #ktb1 config.dtc_inc need to be built
    #ktb2 wrap this with if not 0 0 0 later pls (sum them up)
    config.disposition = config.disposition + "  CODES(" + str(config.dtc_error) + str(config.dtc_pending) + str(config.dtc_inc) + ") DTC(" + config.currentdtc + ") PEN(" + config.currentPending + ")"

    for event in pygame.event.get():
      if event.type == MOUSEBUTTONDOWN:
        #Toggle the settings flag when the screen is touched.
        config.settingsFlag = not config.settingsFlag
        config.tapCount += 1
        # kb events splash mode -- playback the dummy/debug file again
        #
        ## This is working as expected now
        config.debugFlag = True
      if event.type == QUIT or config.tapCount > 2:
        #Rename our CSV to include end time.
        log.closeLog()
        # Close the connection to the ECU.
        ecu.connection.close()
        pygame.quit()
        sys.exit()

    if config.tapTimer > config.tapTimerWindow:
      if config.tapCount == 2:
        ## let's do something on double tap
        #https://www.pygame.org/wiki/toggle_fullscreen?parent=CookBook pygame.display.toggle fullscreen ? Nah.
        #Toggle to deeper metrics will suffice for now
        config.deepMetrics = not config.deepMetrics
      config.tapTimer = 0
      config.tapCount = 0

    if not config.debugFlag:
      #Figure out what tach image should be.
      ecu.getTach()

      # Figure out what gear we're *theoretically* in.
      ecu.calcGear(int(float(ecu.rpm)), int(ecu.speed))

    # Clear the screen
    windowSurface.fill(config.BLACK)


    # Load your logo
    windowSurface.blit(img, (windowSurface.get_rect().centerx - 105, windowSurface.get_rect().centery + 60))
    # If the settings button has been pressed:
    if (config.settingsFlag):
      drawText("Settings", -160, -145, "readout")
      # Print all the DTCs
      ##debug method
      if ecu.dtc or ecu.pending:
        config.dtc_iter = 0
        if ecu.pending:
          for codes, desc in ecu.pending:
            drawText(codes, 120, -80 + (config.dtc_iter * 50), "label")
            config.dtc_iter += 1
            if config.dtc_iter == len(ecu.pending):
              config.dtc_iter = 0
        config.dtc_iter = 0
        if ecu.dtc:
          for codes, desc in ecu.dtc:
            drawText(codes, -120, -80 + (config.dtc_iter * 50), "label")
            config.dtc_iter += 1
            if config.dtc_iter == len(ecu.dtc):
              config.dtc_iter = 0
      else :
        windowSurface.blit(splasher, (0,0))
        drawText("No DTCs found", 140, 140, "label")
    else :
      #Calculate coordinates so tachometer is in middle of screen. (gross)
      coords = (windowSurface.get_rect().centerx - 200, windowSurface.get_rect().centery - 200)


      # Load the tach image
      if ecu.tach_iter >= 0:
        windowSurface.blit(ground[ecu.tach_iter], coords)
      ## Attention listeners at home - this device's code is hinged around RPM, so we use it as the "Proof of Life"
      ## when it is absent, the display will be lifeless and the logs will be full of the below warning/error
      if ecu.tach_iter < 0:
        print "WARNING - negative RPMs are reserved for dark matter engines"
        if ecu.rpm == -1:
          #I don't think this line is legal ktb5
          ecu.tach = 50
          ##not audible## os.system('speaker-test -c2 -twav -l3')
          #sound
          os.system('tput bel')
          os.system('echo "(BT) RPM -1 `date +%Y-%m-%d-%H%M.%S`" >> ../logs/ERROR.`date +%Y-%m-%d-%H%M`.BT.LOG')
          #ktb0.5 there is a gap/bug here still - will get mad print and not back to bt connect (watchdog needed)
          #ktb8 def add the light show trigger here, not an exit
          ##and some https://www.pygame.org/docs/ref/mixer.html
          #sys.exit()
          #-1 is a "magice number for exit, other negative are for below "light show"
        #let's do something else fun here some other time
        #windowSurface.blit(splasher, (0,0))
        #time.sleep(2.5)

      # Draw the RPM readout and label.
      drawText(str(ecu.rpm), 0, 0, "readout")
      drawText("RPM", 0, 50, "label")
      # ktb1 pls add logic to draw a EMU MODE WARNING label when config.redline_emu !=1

      # Draw the coolant temp readout and label.
      drawText(str(ecu.coolantTemp) + "\xb0", -160, 105, "readout") #"\xb0C" adding work - Need config.ktb C/F (hack - grab left 3 in to.string qqq??)
      drawText("Coolant", -170, 140, "label")

      # Draw the intake temp readout and label.i
      drawText(str(ecu.intakeTemp) + "", 190, 105, "readout") #"\xb0C" not want - Need ecu.ktb3 routine for abs<>magn pass/set "-" or sth
      drawText("Intake", 190, 140, "label")

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
      drawText(str(ecu.MAF) + "", -150, -145, "readout") #no g/s label, gps is fine
      drawText("MAF", -190, -110, "label")

      # Draw the engine load readout and label.
      drawText(str(ecu.engineLoad) + " %", 0, -145, "readout")
      drawText("Load", 0, -110, "label")

      # If debug flag is set, feed fake Data so we can test the GUI.
      if config.debugFlag:
        try:
          logLength
        except:
          # #this is a really edge case
          print "Mr. Two-Taps, you're a bad liar"
          list = config.dummyMetrics
          logLength = len(list)
        #Debug gui display refresh 10 times a second.
        if config.gui_test_time > config.dbg_rate:
          #attn ktb0 - there is a logLength issue here after click event
          print config.debugFlag
          print logLength
          try:
            config.metrics = log.getLogValues(list,logLength)
          except:
            config.metrics = config.dummyMetrics
            ## ktb7 this is horrible, not the way.  Use neg rpms and some range + timer approach
            #list = log.readLog('/home/pi/carMon/debug/Demo_log.csv')
          config.debugFlag = config.metrics[0]
          #log.getLogValues(list,logLength)
          # Closes after showing all debug values IF config.exitOnDebug is true
          if config.exitOnDebug and not config.debugFlag:
             log.closeLog()
             pygame.quit()
             sys.exit()
          if not config.exitOnDebug and not config.debugFlag:
             #Do some work...
             print "Not exiting debug mode"
             ## T/T plays debug forever # ktb2
             # config.debugFlag = True
             # ktb2 ktb2 toggled
             #config.ecuReady = True
          ##dbg
          ecu.rpm = config.metrics[1]
          ecu.speed = config.metrics[2]
          ecu.coolantTemp =  config.metrics[3]
          ecu.intakeTemp =  config.metrics[4]
          ecu.MAF =  config.metrics[5]
          ecu.throttlePosition =  config.metrics[6]
          ecu.engineLoad =  config.metrics[7]
          ecu.timingAdvance = config.metrics[8]
          ecu.transmissionTemp = config.metrics[9]
          ##ktb keep an eye on this during testing
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


    ##ktb3 8 seconds for screen only. 18 seconds with other metrics - need more RT.
    ##seems some part of the code is delaying reads
    ##If it is not this, then what???

    config.time_elapsed_since_last_action += dt
    config.gui_test_time += dt
    config.tapTimer += dt

    # Do logs per the specified asynch interval
    if config.time_elapsed_since_last_action > config.log_rate and config.logMetrics:
      os.system("echo ERROR=%s PENDING=%s INCOMPLETE=%s >> ../logs/TEMP.DTCS.LOG" % (config.currentdtc, config.currentPending, config.currentIncomplete))
      #Log all of our Data.
      ##ktb4 I still need to do something with config.disposition for output AND proper population
      config.disposition += config.buildInfo
      config.disposition = config.disposition.replace(',', '')
      #RPMP
      RPMP = int(ecu.rpm*100/config.redline_rpm) #log as RPM Perentage
      ##this is too static, something dynamic at later time ktb8

      ##ktb1 add if statement here to control - this needs polling levels, still
      ##if fast screen mode then:
      ##LCD minimum
      if not config.deepMetrics:
        data = [datetime.datetime.today().strftime('%Y%m%d%H%M%S'), RPMP, ecu.speed, ecu.coolantTemp, ecu.intakeTemp, ecu.MAF, ecu.throttlePosition, ecu.engineLoad, config.disposition]
      else:
        ##Good metrics for an  2001 is300#
        data = [datetime.datetime.today().strftime('%Y%m%d%H%M%S'), RPMP, ecu.speed, ecu.coolantTemp, ecu.intakeTemp, ecu.MAF, ecu.throttlePosition, ecu.engineLoad, ecu.ltft1, ecu.ltft2, ecu.o2bs1s1, ecu.o2bs1s2, ecu.stft1, ecu.stft2, config.disposition]
        ##else long log mode -- this is pretty slow in iso-9141-2
        #data = [datetime.datetime.today().strftime('%Y%m%d%H%M%S'), RPMP, ecu.speed, ecu.coolantTemp, ecu.intakeTemp, ecu.MAF, ecu.throttlePosition, ecu.engineLoad, ecu.fit, ecu.frpd, ecu.fuelRate, ecu.ltft1, ecu.ltft2, ecu.o2bs1s1, ecu.o2bs1s2, ecu.o2Ltftb1, ecu.o2Ltftb2, ecu.o2Stftb1, ecu.o2Stftb2, ecu.stft1, ecu.stft2, config.disposition]

      #ktb11 note that adding text here will flash (badly)
      #ktb4 add an "exiting..." string like this when triple tapped
      #ktb9 overload/rewrite drawText to handle color?
      #If I don't want this to flash I can move it back to the space between Cooland and Intake
      ##The logic here should be the opposite of the default mode, ktb3 tbd if I want 15 pids or 10.  *10 was fast on car vs emu.*
      config.buildInfo = ""
      if not config.deepMetrics:
        string = str(len(data)) + " PIDs"
        text = readoutFont.render(string, True, config.ORANGE)
        textRect = text.get_rect()
      # flashes here
        textRect.centerx = windowSurface.get_rect().centerx + 0
        textRect.centery = windowSurface.get_rect().centery + 140
        windowSurface.blit(text, textRect)

      ##Log speed events based on the below thresholds
      if not config.debugFlag:
        log.updateLog(data)
        if ecu.speed > 110:
          os.system('echo "DEADLY SPEEDING `date +%Y-%m-%d-%H%M`" >> ../logs/AUDIT.SPEED.110.LOG')
        elif ecu.speed > 100:
          os.system('echo "CRAZY SPEEDING `date +%Y-%m-%d-%H%M`" >> ../logs/AUDIT.SPEED.100.LOG')
        elif ecu.speed > 90:
          os.system('echo "STUPID SPEEDING `date +%Y-%m-%d-%H%M`" >> ../logs/AUDIT.SPEED.90.LOG')
        elif ecu.speed > 85:
          os.system('echo "MORONIC SPEEDING `date +%Y-%m-%d-%H%M`" >> ../logs/AUDIT.SPEED.85.LOG')
        elif ecu.speed > 80:
          os.system('echo "RESTRICTED SPEEDING `date +%Y-%m-%d-%H%M`" >> ../logs/AUDIT.SPEED.80.LOG')
        elif ecu.speed > 75:
          os.system('echo "CALI-NORM SPEEDING `date +%Y-%m-%d-%H%M`" >> ../logs/AUDIT.SPEED.75.LOG')
        #if ecu.temp.... #ktb4 log some AUDIT values for temperature or whatever
      # Reset time.
      config.time_elapsed_since_last_action = 0

    ##truncate config.disposition
    config.disposition = ""
    # draw the window onto the screen
    pygame.display.update()

    #ecu.dtc = "P0440"
    
    # #os.system("echo '!!!' M3 sees ECU.CON details AS=%s >> ../logs/TEMP.DTCDBG.LOG" % ((dir(ecu.connection))))
    if ecu.dtc or ecu.pending:
      if ecu.pending:
        config.currentPending = ""
        config.dtc_iter = 0
        for codes, desc in ecu.pending:
          config.currentPending = str(config.currentPending) + str(codes)
          config.dtc_iter += 1
          if config.dtc_iter == len(ecu.pending):
            config.dtc_iter = 0
      if ecu.dtc:
        config.currentdtc = ""
        config.dtc_iter = 0
        for codes, desc in ecu.dtc:
          config.currentdtc = str(config.currentdtc) + str(codes)
          config.dtc_iter += 1
          if config.dtc_iter == len(ecu.dtc):
            config.dtc_iter = 0

      #if config.currentdtc == config.selectdtc1:
      # # config.autoclearSDTC = False
      #ktb000 can't seem to operate on these
      #if len(config.currentdtc) == len(config.selectdtc1):
    if config.autoclearSDTC and ecu.dtc:
      config.dtc_iter = 0
      if ecu.dtc and str(config.currentdtc) == str(config.selectdtc1):
        os.system("echo  ERRORS - EQUAL GET=%i EXP=%i >> ../logs/TEMP.DTCDBG.LOG" % ((len(config.currentdtc)), (len(config.selectdtc1))))
        os.system("echo  '                              EQUAL PENDINGS --' GOT=%i EXP=%i >> ../logs/TEMP.DTCDBG.LOG" % ((len(config.currentPending)), (len(config.selectPending1))))

        ##dear ~god~ globalInterpreter of  python with multiThreading...
        ##This is the same technique that would be needed to toggle the deepMetrics, I'll pass...
        ecu.connection.close()
        time.sleep(11)
        config.autoclearECU = True
        config.ecuReady = False
        ecu.ecuThread()
        while not config.ecuReady:
          time.sleep(.03) #is 100fps a goal when GW's POC was 55fps? ktb4 slow the roll?

        time.sleep(11)

        ecu.connection.close()
        time.sleep(11)
        config.autoclearECU = False
        config.ecuReady = False
        ecu.ecuThread()
        while not config.ecuReady:
          time.sleep(.03) #is 100fps a goal when GW's POC was 55fps? ktb4 slow the roll?

        # #os.system("echo 'welcome to the while loop' >> ../logs/TEMP.DTCDBG.LOG")
        #A code reset should only once per app start pls, to avoid anything nasty from being hidden
        config.autoclearSDTC = False
        config.autoclearECU = False #kinda repetitive...
        ecu.dtc = None
        os.system("echo 'MAYBE CLEARed CODES' %i >> ../logs/TEMP.DTCDBG.LOG" % (int(config.dtc_iter)))
        

