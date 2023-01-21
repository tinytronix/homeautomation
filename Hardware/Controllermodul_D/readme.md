![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/ControllerC2.jpg)

# Purpose
This module can be used as a homeautomation "brain". The Controller is based upon a ATMega328 with a WIZnet W5500 ethernet controller. The ethernet controller implements TCP/IP/DHCP/UDP 
in hardware and ist connected to the ATMega328 via SPI. Arbitrary modules can be connected via I2C on the side of the housing. The I2C interface has
the same layout as all the other controller modules so it can interface to all sensor actor modules in a compatible way. The module may as well be used as a 
bridge: Receive I2C commands from the raspberry controller module and forward to the sensor or actor modules.
[Schematic](https://github.com/tinytronix/homeautomation/blob/master/Hardware/Controllermodul_D/Schematic.pdf)
[Gerber files](https://github.com/tinytronix/homeautomation/blob/master/Hardware/Controllermodul_D/Gerber.zip)

### Features
- compatible to Arduino Uno 
- ATMega328 Microcontroller 5V/16MHz
- WIZnet W5500 Ethernet controller with hardwired TCP/IP/UDP/DHCP protocol support
- Software update via ethernet tftp
- I2C master or slave
- 1 Relais
- 1-wire
- 1 PWM output
- 1 digital input

### Comparison to Controllermodul_B and ESP07 Wifi Module
This module can be used instead of the raspberry controller or ESP07 Wifi Module. It can be connected to any of the sensor actor modules just like 
the Raspberry Controller or ESP Wifi Module.

### Arduino installation prerequsites
Install the athena bootloader in your Arduino IDE (https://github.com/embeddedartistry/athena-bootloader)
set board: "Arduino Uno"
set version: "Standard Wiznet w/ Wiznet 5500"
burn bootloader file athena_atmega328_w5500.hex

### flashing software
After flshing the tftp bootloader you can reach the bootloader at 192.168.1.128

### Attention
The athena bootloader uses the first 74 bytes of the eeprom. Take care if your application also needs specific eeprom access.
For details please read https://github.com/embeddedartistry/athena-bootloader.
 
