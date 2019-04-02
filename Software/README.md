All modules can be accessed using python.

For my use case I decided to write a driver in python which
can be accessed via UDP on Port 49220 on the Raspi controller module.

Usage:
Copy devicesrv.py to the Raspi
go to the directory where devicesrv.py was copied to
start the driver: python .\devicesrv.py

Then start the php test script test.php
