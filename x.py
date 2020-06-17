#!/usr/bin/python
# -*- coding: utf-8 -*-
## this script can test the 
import config, log, time, datetime, sys
import pygame, time, os, csv, commands
#import obd, ecu
from pygame.locals import *

##ktb4 if you want to move this to config, maybe add some logic
#where RPMP 0 means never use RPMP, else do use RPMP
RPMP = 0
peakMAF = 0

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

# Load the Logo image.
try:
  img = pygame.image.load(imgdir + "logo-"  + str(config.dtc_error)  + str(config.dtc_pending)  + str(config.dtc_inc) + ".png")
except pygame.error:
  img = pygame.image.load(imgdir + "logo-330.png")
img_button = img.get_rect(topleft = (135, 220))

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

# Load all of our tach images into an array so we can easily access them.
background_dir = 'tach/'
background_files = ['%i.png' % i for i in range(0, config.rpm_grads + 1)]
ground = [pygame.image.load(os.path.join("/home/pi/carMon/images/", file)) for file in background_files]

# image test for pygame (seeing problems in no-X/multi-user.target mode, ktb8):
# Flash the screen black and white, with log, SLOWLY
tcount = 0
while tcount < 50:
    tcount += 1
    windowSurface.fill(config.BLACK)
    windowSurface.blit(img, (windowSurface.get_rect().centerx - 105, windowSurface.get_rect().centery + 60))
    #splasher = pygame.image.load("/home/pi/carMon/images/b2f-480x320.png")
    #windowSurface.blit(splasher, (0,0))
    pygame.display.update()
    time.sleep(.25)

    windowSurface.fill(config.WHITE)
    windowSurface.blit(img, (windowSurface.get_rect().centerx - 105, windowSurface.get_rect().centery + 60))
    #splasher = pygame.image.load("/home/pi/carMon/images/b2f-480x320.png")
    #windowSurface.blit(splasher, (0,0))
    pygame.display.update()
    time.sleep(.25)

# Flash the screen black and white, with log, quickly
tcount = 0
while tcount < 1000:
    tcount += 1
    windowSurface.fill(config.BLACK)
    windowSurface.blit(img, (windowSurface.get_rect().centerx - 105, windowSurface.get_rect().centery + 60))
    #splasher = pygame.image.load("/home/pi/carMon/images/b2f-480x320.png")
    #windowSurface.blit(splasher, (0,0))
    pygame.display.update()
    time.sleep(config.frameSleep)

    windowSurface.fill(config.WHITE)
    windowSurface.blit(img, (windowSurface.get_rect().centerx - 105, windowSurface.get_rect().centery + 60))
    #splasher = pygame.image.load("/home/pi/carMon/images/b2f-480x320.png")
    #windowSurface.blit(splasher, (0,0))
    pygame.display.update()
    time.sleep(config.frameSleep)

sys.exit()
