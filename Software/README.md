Software example on how to control sensors, actors and send LoRa data. 

## How does it work:
The php modules under php/class contain the sensor/actor control logic including error handling,
automatic reconnect and much more basic functionality.<br>
The two python scripts are UDP-servers that interface to the php modules and to the hardware.
Therefore the python scripts have to run in background permanently.<br>

The php program test.php contains the control logic examples for switching actors and reading sensors.

## How to start:
1. Activate the I2C interface on the Raspberry
2. When using LoRa communication set I2C to 25kHz (RPi I2C stretching bug!!!)
3. Start the python scripts in background 
4. in test.php modify __PHP_BASE_DIR__ to where the php classes are located
5. run the test.php example
