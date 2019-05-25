# homeautomation
several din rail modules such as Analog inputs, Relays Switching outputs, RS232, 1wire, I2C, LoRa

Controller Module with watchdog:
- Raspberry B+ (read only file system)
- 2 Relais
- watchdog controller ATTiny85
- 1wire
- RS232
- RTC

The watchdog controller needs to be triggered by Raspi. If Raspi hangs or crashed, the watchdog controller
gains access to the I2C Bus. It then can read AD values and switch Relais in order to keep vital functions
alive and prevent damages to house installation.

Analog Module:
- 16 AD channels
- channel 16 can be configured to read back sensor supply voltage
- signal conditioning for each channel with 16 Rail-2-Rail OP Amps
- maximum of 2 analog modules per controller (I2C adressing constraint)

Switching Module:
- 11 Relais outputs 230VAC, 5A max.
- maximum of 8 switching modules per controller (I2C adressing constraint) 

LoRa:
- The LoRa module bridges I2C ommands from the controller module to modules located in the garden.
- It will later (planned for future extensions!) also send data to small devices which can be placed behind wall power outlets or 
wall switches.
- On the photos you may see a little hand soldered wire. This is due to some misinterpretation of the datasheet ;)
The schematic is already the corrected version and will work!
