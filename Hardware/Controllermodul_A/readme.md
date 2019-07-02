The Controller is based upon a Raspberry. All modules are connected via I2C to the Controller.
The Controller runs the software that contains the home automation logic which switches Relais, reads
sensors and so on.

It as well has two Relais on its own and a RS232 and a 1wire interface.

### Watchdog
The Raspberry needs a programmed watchdog controller. Else the Raspberry I2C interface is being disabled.
The watchdog is toggled by devicesrv.py (https://github.com/tinytronix/homeautomation/blob/master/Software/devicesrv.py)
If this program does not run, the watchdog controller disables I2C from Raspberry and takes control over the I2C bus.
