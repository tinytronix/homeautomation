# Purpose
This is the homeautomation "brain". The Controller is based upon a Raspberry. Arbitrary modules are connected via I2C.

# Features
- Raspberry B+ with Ethernet 
- Atmel ATMega328 as a backup safety processor
- Watchdog
- 2 Relais
- 1-wire
- UART interface 3.3V

# Comparision Controllermodul_A and Controllermodul_B
The only differnce is the backup safety processor. Controllermodul_A has a ATTiny85 and Controllermodul_B has a ATMega328
which can be flashed in-circuit by the Raspberry PI. The ATMega can also trace debug strings to the Pi. 
to the Controller. The Controller runs the software that contains the home automation logic which switches Relais, reads sensors and so on.

It as well has two Relais on its own and a RS232 and a 1wire interface.
