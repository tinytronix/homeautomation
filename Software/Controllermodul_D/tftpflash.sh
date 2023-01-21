#!/bin/bash

ARDUINODIRECTORY=/set/your/arduino/directory/here
PROJECTNAME=nameOfYourProject

#jump to bootloader 
#Attention: This sequence is application specific. You need to implement it in your application if you want the flash procedure to start automatically.
#Otherwise you have to reboot manually before starting this script
echo -e "\xAA\x55\xAA\x55" | nc -w 0 -4u 192.168.1.128 46001

cd $ARDUINODIRECTORY
avr-objcopy -I ihex $ARDUINODIRECTORY/$PROJECTNAME.ino.arduino_standard.hex -O binary $ARDUINODIRECTORY/x.bin
sleep 0.6
tftp 192.168.1.128 <<'EOF'
mode octet
verbose
trace
put x.bin
EOF
