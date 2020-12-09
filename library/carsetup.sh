echo '#!/bin/bash


## phasing this out:
# the mausberry I bought failed very early on.  I was unable to get respectable (any) reply from the vendor.
# I wish him well but can't patronize nor recommend the vendor.
# SURPRISINGLY, I've been running with no shutdown for over a year now without incident.
# Unsafe shutdown's aren't as big a deal in this lineup.
# So, as an alternative, you can just hardwire a 12v-5v DC-DC PUPS (2.5A!) to IGN and ground and viola.
# I use a jumper to defeat this script, but better yet, don't use it.  (was keeping my options open)

## pressing on? ok:
#this is the GPIO pin connected to the lead on switch labeled OUT
GPIOpin1=5 # This is pin 29, I promise.
##ALSO NOTE - in the absence of the mausberry signals
##you can simply ground ping 29 to anything (including neighbor pin -- GROUND)
##That will keep the power on, long enough to disable the script

#this is the GPIO pin connected to the lead on switch labeled IN
GPIOpin2=6 # This is pin 31, I promise.

#Enter the shutdown delay in minutes
delay=0

echo "$GPIOpin1" > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio$GPIOpin1/direction
echo "$GPIOpin2" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio$GPIOpin2/direction
echo "1" > /sys/class/gpio/gpio$GPIOpin2/value
let minute=$delay*60
SD=0
SS=0
SS2=0
while [ 1 = 1 ]; do
##this janky - nvm
#chmod 700 /home/pi/carMon/m3_pi.py
### does not show in the right screen space/tty
##ps -C m3_pi.py >/dev/null || /home/pi/carMon/m3_pi.py
### spawns and dies where the same state works in local term - meh
##ps -C m3_pi.py >/dev/null || runuser -l pi  -c "/home/pi/carMon/m3_pi.py &"
power=$(cat /sys/class/gpio/gpio$GPIOpin1/value)
uptime=$(</proc/uptime)
uptime=${uptime%%.*}
current=$uptime
if [ $power = 1 ] && [ $SD = 0 ]
then
SD=1
SS=${uptime%%.*}
fi

if [ $power = 1 ] && [ $SD = 1 ]
then
SS2=${uptime%%.*}
fi

if [ "$((uptime - SS))" -gt "$minute" ] && [ $SD = 1 ] && [ $power = 1 ]
then
poweroff
SD=3
fi

if [ "$((uptime - SS2))" -gt '20' ] && [ $SD = 1 ]
then
SD=0
fi

sleep 1
done' > /etc/switch.sh
sudo chmod 777 /etc/switch.sh
sudo sed -i '/etc\/switch.sh &/d' /etc/rc.local
sudo sed -i '$ i /etc/switch.sh &' /etc/rc.local

