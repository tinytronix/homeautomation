This is a module that extends the home automation to speak LoRa (not LoRaWAN).
LoRa is a wireless spread spectrum radio data transmission technique for ISM band at 868MHz or 433MHz.
See https://en.wikipedia.org/wiki/LoRa

## Interfaces for sending and receiving LoRa data:
1. serial UART at 3,3V or 5V 
2. I2C

## Settings for Arduino IDE:
- The uC is an ATMega328, 8MHz, 3,3V. The board can be programmed with Arduino IDE.
- Board: Arduino Pro or Pro Mini
- Processor: ATMega328P (3,3V, 8MHz)

The bootloader can be directly programmed from the Arduino IDE when the above settings were made.

## Hardware options
This hardware can be used for a bridge module or a gateway module. For the Gateway version Jumper1 (JP1) needs to be open. Please see schematic for details.<br>
Hardware:
![lt](https://raw.githubusercontent.com/tinytronix/SX126x/master/pcb/LoRa2.JPG)
