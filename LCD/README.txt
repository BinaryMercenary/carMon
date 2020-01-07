I grabbed the low priced ili9486
  Pros
Low cpu usage
Reasonable screen quality
  Cons
Low refresh rate
  Unsure:
No type of HDMI cable needed (matter of GPIO needs)
Quality of the actual component (mixed reviews, tbd)

  I have enough GPIO pins left for the transcooler relay controller at whatever point I can read the value like techstream+M-VCI cable can...

  Anyway, I installed the driver per:
https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(A)#Image

git clone https://github.com/waveshare/LCD-show.git
cd LCD-show/
chmod +x LCD35-show
./LCD35-show
#./LCD-hdmi ## to change back

sudo raspi-config #was not needed in my use case
(the alternate disk image offerred but waveshare may not see use by me)

  PS - for full screen, examples from online
DISPLAYSURF = pygame.display.set_mode((400, 300), FULLSCREEN) #worked kinda like this in carmon
Vs
pygame.display.toggle_fullscreen ## not seeing what i'd expect here
