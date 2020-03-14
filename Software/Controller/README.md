Software example on how to control sensors, actors and send LoRa data. 

## How does it work:
The two python scripts devicesrv.py and loragateway.py are UDP-servers that interface on 127.0.0.1 localhost to the php modules and to the hardware. The python scripts listen to UDP commands sent from the php modules, translate them to I2C. After completion of the I2C command an UDP answer will be sent back to the php modules. The answer contains either:
- a value (in case of sensor)
- an ACK or NAK in case of actor
- lora data is handled exactly in the same manner

The python scripts have to run in background permanently.<br>
The php modules under php/class contain the sensor/actor control logic including error handling,
automatic reconnect and much more basic functionality.<br>

The php program test.php and temperature.php contain examples on how to use the php classes for switching actors and reading sensors.

![lt](https://github.com/tinytronix/homeautomation/blob/master/Software/Controller/Architektur.jpg)
## How to start:
1. Activate the I2C interface on the Raspberry
2. When using LoRa communication set I2C on Raspberry to 25kHz (RPi I2C stretching bug!!!)
3. Install I2C python modules<br>
  sudo apt-get update<br>
  sudo apt-get install i2c-tools<br>
  sudo apt-get install python-smbus<br>
4. Start the python scripts in background 
5. in test.php modify __PHP_BASE_DIR__ to where the php classes are located
6. run the test.php example

## Watchdog
The controller module needs a programmed watchdog controller (https://github.com/tinytronix/homeautomation/tree/master/Hardware/Controllermodul_A/WatchdogController). Else the Raspberry I2C interface is being disabled. The watchdog is toggled by Raspberry devicesrv.py (function def watchdog_thread). If this program does not run on the Raspi, the watchdog controller disables I2C from Raspberry and takes control over the I2C bus.
