# Purpose
This is an extensive and expandible home automation hardware and software system.
It contains ready to use gerber files for pcb production, schematics, part list and software examples.

## Applications
- solar systems
- home heating
- home display to show temperatures, system states, warnings and many more
- alarm system
- presence simulation
- comfort functions
- window blinds and shutters
- garden irrigation
- consider weather forecast for any control as appropriate 
- ... and many more

## Maximum configuration
- up to 88 Relais
- up to 32 analog Temperature sensors
- up to 40 230V detection inputs
- up to 12 onewire sensors
- pulse counter
- 2^32 of wireless LoRa devices, 1000m distance through walls or 3 floors reliable
- development ongoing, max. configuration expandable as required

## System overview (more [here](https://github.com/tinytronix/homeautomation/tree/master/Software/Controller))
![lt](https://github.com/tinytronix/homeautomation/blob/master/Software/Controller/Architektur.jpg)

## Hardware Overview ([more photos here](https://github.com/tinytronix/homeautomation/blob/master/Photos/readme.md))
Upper row: Module bus to connect I2C and Power to each module.<br>
Lower row left to right: Switching module, Analog module, Controller module:
![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/ModulesOpen.jpg)

The modules finally integrated in the fuse box:
![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/Schaltschrank2.JPG)

## Raspberry Controller Module with watchdog ([here](https://github.com/tinytronix/homeautomation/tree/master/Hardware/Controllermodul_B)):
- Raspberry B+ with Ethernet 
- I2C master
- Atmel ATMega328 as a backup safety processor
- ATMega328 is in-circuit programmable
- Watchdog
- 2 Relais
- 1-wire
- UART interface 3.3V
- additional ISP interface at pcb edge

The watchdog controller needs to be triggered by Raspi. If Raspi hangs or crashed, the watchdog controller
gains access to the I2C Bus. It then can read AD values and switch Relais in order to keep vital functions
alive and prevent damages to house installation.

All modules can bei either controlled by Controller Module B (Raspberry) or Lora Bridge (ATMega328)
The interface to all modules is the same: I2C. Any module can easily be connected to Controller Module B or Lora Bridge without any modifications.

## ESP07 (ESP8266) Wifi Controller Module ([here](https://github.com/tinytronix/homeautomation/tree/master/Hardware/Controllermodul_C%20(ESP8266)))
- ESP07
- I2C master or slave
- 1 Relais
- 1-wire

This module can be used instead of the raspberry controller. It can be connected to any of the sensor actor modules listed below.
The ESP07 Wifi Module can also be used as a I2C slave.

## Module Bus
This is the common interface that every module needs. The module bus distributes 3,3V and 5V power supply and the
I2C connection. Each module needs to implement a module bus input and a module bus output.
So all DIN rail modules can be coupled and arbitrary extensions are possible.
The Controller module is the module bus starting point because it provides 3,3V, 5V and is the I2C master.
 
## Analog Module:
- 16 AD channels
- signal conditioning (Offset, Amplification) for each channel with Rail-2-Rail OP Amps
- channel 16 can be configured to read back sensor supply voltage
- maximum of 2 analog modules per controller (I2C adressing constraint)
- can easily be connected to Controller Module B or Lora Bridge without any modifications.
 
## Switching Module Typ A:
- 11 Relais outputs 230VAC, 5A max.
- maximum of 8 switching modules per controller (I2C adressing constraint) 
- can easily be connected to Controller Module B or Lora Bridge without any modifications.

## Switching Module Typ B:
- can control shutters and window blinds
- three channels each up/down
- software prevents switching up/down at the same time
- can easily be connected to Controller Module B or Lora Bridge without any modifications.

## Digital Input Module Typ A ([here](https://github.com/tinytronix/homeautomation/blob/master/Photos/Digitalmodul_A.JPG))
- 5x mains detection 230V
- 1x Counter Input 5V logic level (interrupt triggered)
- mains detection inputs can be changed to input 5V logic level as well
- can easily be connected to Controller Module B or Lora Bridge without any modifications.

## LoRa Gateway ([here](https://github.com/tinytronix/homeautomation/blob/master/Hardware/LoraGateway/readme.md)):
- A module to forwards commands (I2C or RS232 at 3,3V/5V) from the Raspberry Controller module via wireless spread spectrum radio data transmission to modules located somewhere in the house or garden.
- works on ISM Band at 433MHz or 868MHz
- LoRa is a highly reliable wireless spread spectrum radio data transmission technique. See https://en.wikipedia.org/wiki/LoRa
- This module creates a private LoRa home automation network. The software does not support LoRaWAN. 
- shares same hardware as LoRa Bridge, but different software
- for the Gateway version Jumper1 (JP1) needs to be open, see [schematic](https://github.com/tinytronix/homeautomation/blob/master/Hardware/LoraGateway/Schematic.pdf) 
- can easily be connected to Controller Module B

## LoRa Bridge ([here](https://github.com/tinytronix/homeautomation/blob/master/Hardware/LoraGateway/readme.md)):
- shares same hardware as LoRa Gateway, but different software
- for the Bridge version Jumper1 (JP1 - see schematic) needs to be closed
- can be used to access switching modules or analog modules that are not directly coupled to the Controller module
- in this use case the switching or analog modules are coupled via I2C to the LoRa Bridge 
- The bridge implements a module bus starting point which provides 3,3V, 5V and I2C master to controll the connected modules

## LoRa inwall module ([here](https://github.com/tinytronix/homeautomation/blob/master/Hardware/LoraInwallShutter/readme.md))
- can be placed behind inwall switches or inwall power outlets
- switches shutters, blinds, power outlets via LoRa
- requires a LoRa gateway connected to the Controller module

## LoRa switched power outlet ([here](https://github.com/tinytronix/homeautomation/blob/master/Hardware/LoraPowerswitch/readme.md))
- switches 230V
- requires a LoRa gateway connected to the Controller module
