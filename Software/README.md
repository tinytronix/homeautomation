Software example on how to control sensors, actors and send LoRa data. 

## How does it work:
The two python scripts are UDP-servers that interface to the php modules and to the hardware.
Therefore the python scripts have to run in background permanently.<br>
The php modules under php/class contain the sensor/actor control logic including error handling,
automatic reconnect and much more basic functionality.<br>

The php program test.php and temperature.php contain examples on how to use the php classes for switching actors and reading sensors.

## How to start:
1. Activate the I2C interface on the Raspberry:<br>
  sudo apt-get update<br>
  sudo apt-get install i2c-tools<br>
  sudo apt-get install python-smbus<br>
2. When using LoRa communication set I2C to 25kHz (RPi I2C stretching bug!!!)
3. Start the python scripts in background 
4. in test.php modify __PHP_BASE_DIR__ to where the php classes are located
5. run the test.php example

## Watchdog
The controller module needs a programmed watchdog controller. Else the Raspberry I2C interface is being disabled. The watchdog is toggled by Raspberry devicesrv.py. If this program does not run on the Raspi, the watchdog controller disables I2C from Raspberry and takes control over the I2C bus.
