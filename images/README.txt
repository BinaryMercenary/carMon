##Please note that for the 480x320 size displays, the png files for the tach images need to be about 300x270.
#I may be running this at 1280x800 the images at present are not scaled for ANY screen size yet, except 0.png
#Color is TBD, altho, GW's white look is quite nice...

##You'll also want to do this in the cli:
ln -s /home/pi/carMon/images/ /home/pi/
mv /home/pi/images /home/pi/tach
ln -s /home/pi/carMon/images/ /home/pi/

##likewise, there could be color and res folders, here:
/home/pi/images/tach/1280white/
/home/pi/images/tach/1280aqua/
/home/pi/images/tach/1280lime/
/home/pi/images/tach/1280lime/
/home/pi/images/tach/800lime/
/home/pi/images/tach/600lime/
/home/pi/images/tach/480lime/
/home/pi/images/tach/320lime/
/home/pi/images/tach/240lime/
#etc., which could be copied to /home/pi/images/tach/ and:
cp -R /home/pi/images/tach/1280white/ /home/pi/carMon/tach/
ln -sf /home/pi/carMon/tach/ /home/pi/images/tach/

##best approach would be to manage the selection from conf, which might mean:
/home/pi/images/tach/1280i-white/
/home/pi/images/tach/RES-COLOR/
#etc.
