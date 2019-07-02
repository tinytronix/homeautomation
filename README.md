# Home Automation Device Overview
An extensive and expandible home automation hardware and software system.
Contains gerber files for allmodules, part list and software examples.

From left to right: Switching module, Analog module,controller module:
![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/ModulesOpen.jpg)

The modules finally integrated in the fuse box:
![lt](https://github.com/tinytronix/homeautomation/blob/master/Photos/Schaltschrank.JPG)

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

## Analog Module:
- 16 AD channels
- channel 16 can be configured to read back sensor supply voltage
- signal conditioning for each channel with 16 Rail-2-Rail OP Amps
- maximum of 2 analog modules per controller (I2C adressing constraint)

## Switching Module Typ A:
- 11 Relais outputs 230VAC, 5A max.
- maximum of 8 switching modules per controller (I2C adressing constraint) 

## Switching Module Typ B:
- can control shutters and window blinds (3x UP/DOWN)
- two channels each up/down
- software prevents switching up/down at the same time

## LoRa Gateway:
- The LoRa (https://en.wikipedia.org/wiki/LoRa) module forwards I2C commands via spread spectrum radio to modules located somewhere in the house or garden.

