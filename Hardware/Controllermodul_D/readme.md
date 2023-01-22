![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/ControllerC1.jpg)

# Purpose
This module can be used as a homeautomation "brain" for my [sensors and actors](https://github.com/tinytronix/homeautomation). The Controller is based upon a ATMega328 with a WIZnet W5500 ethernet controller. The ethernet controller implements TCP/IP/DHCP/UDP 
in hardware and ist connected to the ATMega328 via SPI. Arbitrary modules can be connected via I2C on the side of the housing. The I2C interface has
the same layout as all the other controller modules so it can interface to all sensor actor modules in a compatible way. The module may as well be used as a bridge: Receive I2C commands via ethernet from the raspberry controller module and forward to the sensor or actor modules.
</br>[Schematic](https://github.com/tinytronix/homeautomation/blob/master/Hardware/Controllermodul_D/Schematic.pdf)
</br>[Gerber files](https://github.com/tinytronix/homeautomation/blob/master/Hardware/Controllermodul_D/Gerber.zip)
</br>[Housing](https://github.com/tinytronix/homeautomation/blob/master/Hardware/HUT-C_DB-DE.pdf)
#### Information regarding schematic and gerber:
As of 21st January 2023 there is an error in the schematic: The SPI line from the WS5500 to the ATMega328 (MISO) does not reliably meet the voltage level specification. The ATmega328 sees 3.3V on the MISO line and minimum high level @5V is 0.6*Vcc=3V. It seems to work as it is now but I need to integrate a level shifter to set the MISO line from 3.3V to 5V to make it more reliable. 

### Features
- compatible to Arduino Uno 
- ATMega328 Microcontroller 5V/16MHz
- programming via ISP interface
- trace interface (serial uart)
- WIZnet W5500 Ethernet controller with hardwired TCP/IP/UDP/DHCP protocol support
- Software update via ethernet tftp
- I2C master or slave
- 1 Relais
- 1-wire
- 1 PWM output
- 1 digital input
- connector for two status LEDs

### Comparison to [Controllermodul_B (raspberry based)](https://github.com/tinytronix/homeautomation/tree/master/Hardware/Controllermodul_B) and [ESP07 Wifi Module](https://github.com/tinytronix/homeautomation/tree/master/Hardware/Controllermodul_C)
This module can be used instead of the raspberry controller or ESP07 Wifi Module. It can be connected to any of the sensor actor modules just like 
the Raspberry Controller or ESP Wifi Module.

### Arduino installation prerequsites
Install the athena bootloader in your Arduino IDE (https://github.com/embeddedartistry/athena-bootloader)
set board: "Arduino Uno"
set version: "Standard Wiznet w/ Wiznet 5500"
burn bootloader file athena_atmega328_w5500.hex

### flashing software
After flashing the tftp bootloader you can reach the bootloader at 192.168.1.128.
</br>The bootloader is [here](https://github.com/tinytronix/homeautomation/blob/master/Software/Controllermodul_D/athena_atmega328_w5500.hex)
</br>You may use this bash script for flashing: [tftpflash.sh](https://github.com/tinytronix/homeautomation/blob/master/Software/Controllermodul_D/tftpflash.sh)

### Attention
The athena bootloader uses the first 74 bytes of the eeprom. Take care if your application also needs specific eeprom access.
For details please read https://github.com/embeddedartistry/athena-bootloader.
 
### Picture with housing
Remark: The I2C connector breakout on the side of the housing was not finished when taking this picture. In the top of the housing is the same [bus interface](https://github.com/tinytronix/homeautomation/tree/master/Hardware/Modulbus) like any other of my modules. 
![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/ControllerC3.jpg)
