#!/bin/bash
## This launcher is for "production"/live mode
## For debug/dev mode, just launch `m3_pi.py` directly

## To start on boot, add this to line:
## @bash /home/pi/carMon/carMon.sh &
## to
## vi ~/.config/lxsession/LXDE-pi/autostart

## insert the MAC address of your bluetooth here (ktb7 see ...)
sudo rfcomm bind 0 00:1D:A5:02:09:48
#this will not work in `multi-user.target` #ktb0 add logic
lxterminal --geometry=56x14 -e python /home/pi/carMon/m3_pi.py
## for larger screeens:
#lxterminal -e python /home/pi/carMon/m3_pi.py
