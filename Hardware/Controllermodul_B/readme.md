# Purpose
This is the homeautomation "brain". The Controller is based upon a Raspberry. Arbitrary modules can be connected via I2C.
The Controller runs the software that contains the home automation logic which switches Relais, reads sensors and so on.

### Features
- Raspberry B+ with Ethernet 
- Atmel ATMega328 as a backup safety processor
- ATMega328 is in-circuit programmable
- Watchdog
- 2 Relais
- 1-wire
- UART interface 3.3V
- additional ISP interface at pcb edge

### Watchdog
The backup safety processor serves as watchdog for the Raspberry PI. The watchdog is toggled by Raspberry devicesrv.py (https://github.com/tinytronix/homeautomation/blob/master/Software/devicesrv.py). If this program does not run on the Raspi, the backup safety processor disables I2C from Raspberry and takes control over the I2C bus. 

### Comparision Controllermodul_A and Controllermodul_B
The only difference is the backup safety processor. Controllermodul_A has a ATTiny85 and Controllermodul_B has a ATMega328.
With Controllermodul_B the ATMega328 can be flashed in-circuit by the Raspberry PI with avrdude and it can trace debug strings to the Pi. Therefore (with Controllermodul_B) it is not necessary to dispount the device from the automation system when reprogramming the safety processor.

### Software compatibility Controllermodul_A and Controllermodul_B
Software developed for Controllermodul_A does run on Controllermodul_B without modification.
