Software example on how to controll sensors, actors. 

The php modules contain the sensor/actor control logic.
The two python scripts are UDP-servers that interface to the 
php modules and to the hardware.

Therefore the python scripts have to run in background permanently.

## How to start:
1. Activate the I2C interface on the Raspberry
2. When using LoRa communication set I2C to 25kHz (RPi I2C stretching bug!!!)
3. Start the python scripts in background 
4. run the test.php example
