# Purpose
This is the homeautomation "brain". The Controller is based upon a Raspberry. Arbitrary modules are connected via I2C.

### Features
- Raspberry B+ with Ethernet 
- Atmel ATMega328 as a backup safety processor
- Watchdog
- 2 Relais
- 1-wire
- UART interface 3.3V

### Comparision Controllermodul_A and Controllermodul_B
The only difference is the backup safety processor. Controllermodul_A has a ATTiny85 and Controllermodul_B has a ATMega328.
With Controllermodul_B the ATMega328 can be flashed in-circuit by the Raspberry PI and it can trace debug strings to the Pi. Therefore (with Controllermodul_B) it is not necessary to dispount the device from the automation system when reprogramming the safety processor.