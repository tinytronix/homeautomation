# Home Automation Device Overview
An extensive and expandible home automation hardware and software system.
Contains ready to use gerber files for pcb production, part list and software examples.

Upper row: Module bus to connect I2C and Power to each module.<br>
Lower row left to right: Switching module, Analog module, Controller module:
![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/ModulesOpen.jpg)

The modules finally integrated in the fuse box:
![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/Schaltschrank2.JPG)

## Controller Module with watchdog:
- Raspberry B+ (read only file system)
- 2 Relais
- watchdog controller ATTiny85
- 1wire
- RS232
- RTC

The watchdog controller needs to be triggered by Raspi. If Raspi hangs or crashed, the watchdog controller
gains access to the I2C Bus. It then can read AD values and switch Relais in order to keep vital functions
alive and prevent damages to house installation.

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

## Switching Module Typ A:
- 11 Relais outputs 230VAC, 5A max.
- maximum of 8 switching modules per controller (I2C adressing constraint) 

## Switching Module Typ B:
- can control shutters and window blinds
- three channels each up/down
- software prevents switching up/down at the same time

## LoRa Gateway:
- A module to forwards commands (I2C or RS232 at 3,3V/5V) from the Raspberry Controller module via wireless spread spectrum radio data transmission to modules located somewhere in the house or garden.
- works on ISM Band at 433MHz or 868MHz
- LoRa is a highly reliable wireless spread spectrum radio data transmission technique. See https://en.wikipedia.org/wiki/LoRa
- This module creates a private LoRa home automation network. The software does not support LoRaWAN. 
- shares same hardware as LoRa Bridge, but different software
- for the Gateway version Jumper1 (JP1 - see schematic) needs to be open

## LoRa Bridge:
- shares same hardware as LoRa Gateway, but different software
- for the Bridge version Jumper1 (JP1 - see schematic) needs to be closed
- can be used to access switching modules or analog modules that are not directly coupled to the Controller module
- in this use case the switching or analog modules are coupled via I2C to the LoRa Bridge 
- The bridge implements a module bus starting point which provides 3,3V, 5V and I2C master to controll the connected modules

## LoRa inwall module
- can be placed behind inwall switches or inwall power outlets
- switches shutters, blinds, power outlets via LoRa
- requires a LoRa gateway connected to the Controller module

## LoRa switched power outlet ([here](https://github.com/tinytronix/homeautomation/tree/master/Hardware/LoraPowerswitch))
- switches 230V
- requires a LoRa gateway connected to the Controller module
