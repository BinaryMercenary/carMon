# carMon
  ATTN - runs fullscreen by default - triple click or triple tap to exit the app.

  Fork of Geoffrey Wacker's (GW) Cal Poly SLO project, initially for M3 but will be adapting to IS300 and making more generic/portable as time permits.
(See https://digitalcommons.calpoly.edu/cpesp/235)

  N.B./nota bene/ATTENTION: Generic OBD2/ISO-9141-2 (and even M-VCI) is NOT a realtime system, as is noted be the original author RE using this display:


  From GW's PDF, "As for the hardware, I’d like to transition from the Raspberry Pi 3 to a Raspberry Pi Zero W.  I have no need for the extra processing power that the Pi 3 provides, so the Zero W would be a great choice due to its extremely small form factor and even lower cost.  I’d also like to explore the possibility of directly connecting to the vehicle’s CAN (controller area network) bus instead of OBD-II.  The response time of OBD-II is somewhat lacking, and it can take up to a second to get new data.  This is acceptable for data that doesn’t change often like temperatures, but terrible for things like RPM, throttle position, and speed.  Connecting directly over CAN would hopefully eliminate the response time issues, and would open up the door to actually controlling things in the car that communicate over CAN bus (lock the doors, switch on lights, etc.)." -- GW

  With this first commit, I have the same proof of concept level as did GW, but will be adapting the code to do thresholding, warnings, etc.   RPM watermarking comes to mind (like a good AEM), among others.   Another major intent is for dealing with a single code, the dreaded P0440 (or maybe multi P044X codes?), as those could get a cry-wolf situation to form in which a nagging CEL will mask a more serious code from being checked.   If that is the only DTC found, an auto-clear option in the config will allow the Pi carMon to clear that Maintenance Indicator Light (MIL), and or a touch-to-clear yellow light indicator.   I may go as far as to managing the CEL with a tap, for related reasons.   It's worth noting that in California, you can have ONLY a pending Vapor Canister code BUT not a CEL...

  Considering the parts I've replaced (my VSV's and many hoses, and):
77300-53010 Gas cap;
77390-53010 Fuel fill check valve;
77177-12020 Fuel fill check valve gasket;
90910-12243 VSV, Purge / Front Man.;
90910-12224 VSV, Tank Bypass / Rear can assy;
90910-12220 VSV, Canister / Intake post-filter;
89460-33010 SENSOR (5v) (replaced before I had techstream access);
As small/slow take-side vacuum persists, I'm not keen on replacing the 77740-53011 itself for further debug.   All the other parts are good cheap spares but the canister itself is not on my menu.   If anything I'm rather liking the popcorn tune effect that generous in-chamber gas vapor is providing and can't wait to see how that TorqAmp from Jelke Hoekstra and Daniël Hilgersom will fare in a rich state.

  From my tests, the silent pending/warn comes on around 70 miles after clearing MLI, and the solid CEL comes on at about 150 miles total.  I'll be logging this and other aspects of the vehicle for debug purposes and repeatability/reproducibility.

  After hacking the web-posted code into a working state (cursed html characters, indentation, missing part of log.py, etc.), I tested with the trusty Mini-Vci/M-vci interface cable (Toyota J2354).   The M-VCI cable is not an ELM327 device, afterall, and will not work as-is (if specs/python class can be made to work at all?).   Pity, as I noticed when using the M-VCI cable with Tis Techstream Diagnostic Cable Toyota Firmware V1.4.1, there are many desirable PIDs not seen on my other scanners.   One important value is the ATF temperature.   I've installed an analogue gauge but want to make a thermostat routine in this carMon code that considers ATF fluid value and runs my fan-tap relay at a LUT'd duty cycle.

  My ScanTool OBDLink SX 425801 cable will arrive just after new year, hoping that at least the ATF temperature can be found from that - my new years wish!  The cable arrived... the advanced readings _have not_.

  Update: Getting the automatic transmission's Temperature PID (listed or exposted) for the Is300 from 2001-2005 is proving troublesome from ISO-9141-2 protocols.  After I get the rest of the POC working, I may have to double back (pretty far) to see how any K-line type CAN bus dialogues can take place and what PID's are exposed.  I'll be asking tech savvy gearheads in person and on line for insights, in the meantime.  Especially note that there is NOT an exposed powertrain ECU on this car (no split bus/no second address/likely all-in one given the OEM ECU PN schedules).  M-VCI does indeed see many more values than any other obd approach can (even with elm327) so special guidance is needed - perhaps from the pdf I found recently -- Drew Technologies, Inc. SAE J2534 API REFERENCE http://www.drewtech.com/support/passthru.html (the relead DLL that I have from techscrtream wil not port to python easily, tho).

ISO 9141-2 (5 baud init, 10.4 kbit/s)              <------ POC works
SAE J-1850-PWM (41.6 kbit/s)                       <--- tbd
ISO 15765-4 CAN (11||29 bit ID, 250||500 kbit/s)   <-- tbd - unlikely since this was standardized circa 2008
ISO 14230-4 KWP (5 baud init, 10.4 kbit/s)         <- tbd - contemparary to ISO 9141-2
ISO 14230-4 KWP (fast init, 10.4 kbit/s)           <- tbd - contemparary to ISO 9141-2

See excerpt ./library/tbd_powertrain.api

