# Purpose
This is the homeautomation "brain". The Controller is based upon a Raspberry. Arbitrary modules can be connected via I2C.
The Controller runs the software that contains the home automation logic which switches Relais, reads sensors and so on.

Controllermodul_A is deprecated. Please see the new hardware [Controllermodul_B](https://github.com/tinytronix/homeautomation/tree/master/Hardware/Controllermodul_B)

### Features
- Raspberry B+ with Ethernet 
- Atmel ATTiny85 as a backup safety processor
- Watchdog
- 2 Relais
- 1-wire
- UART interface 3.3V

### Watchdog
The module needs a programmed watchdog controller. Else the Raspberry I2C interface is being disabled.
The watchdog is toggled by Raspberry devicesrv.py (https://github.com/tinytronix/homeautomation/blob/master/Software/devicesrv.py)
If this program does not run on the Raspi, the watchdog controller disables I2C from Raspberry and takes control over the I2C bus.
