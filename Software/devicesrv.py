#!/usr/bin/python

# Voraussetzungen
# sudo apt-get update
# sudo apt-get install i2c-tools
# sudo apt-get install python-smbus


#---------------------------------------------------------------------------------------------------------------------------------------
# imports
#---------------------------------------------------------------------------------------------------------------------------------------
from socket import *  
import RPi.GPIO as GPIO   
import time
import threading
from thread import start_new_thread
import subprocess
import smbus


#---------------------------------------------------------------------------------------------------------------------------------------
# TCP server configuration
#---------------------------------------------------------------------------------------------------------------------------------------
HOST = "0.0.0.0"   
PORT = 49220


#---------------------------------------------------------------------------------------------------------------------------------------
# supported devices 
#---------------------------------------------------------------------------------------------------------------------------------------
DEVICE_CLASS								= 0xFF000000
DEVICE_CLASS_CONTROLLER			= 0x01000000
DEVICE_CLASS_SCHALTMODUL		= 0x02000000
DEVICE_CLASS_ANALOGMODUL		= 0x03000000

DEVICE_SUBCLASS							= 0x00FF0000

DEVICE_TYPE									= 0x0000FF00
DEVICE_TYPE_A								= 0x00000100
DEVICE_TYPE_B								= 0x00000200

DEVICE_ADDRESS							= 0x000000FF
	
DEVICE_CONTROLLER_A_ID01		= DEVICE_CLASS_CONTROLLER  | DEVICE_TYPE_A | 0x01		# Hutschienencontroller_A
  
DEVICE_SCHALTMODUL_A_ID01		= DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_A | 0x01		# Schaltmodul
DEVICE_SCHALTMODUL_A_ID02		= DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_A | 0x02		# Schaltmodul
DEVICE_SCHALTMODUL_A_ID03		= DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_A | 0x03		# Schaltmodul

DEVICE_SCHALTMODUL_B_ID01		= DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_B | 0x05		# Schaltmodul
DEVICE_SCHALTMODUL_B_ID02		= DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_B | 0x06		# Schaltmodul
DEVICE_SCHALTMODUL_B_ID03		= DEVICE_CLASS_SCHALTMODUL | DEVICE_TYPE_B | 0x07		# Schaltmodul
  
DEVICE_ANALOGMODUL_A_ID01		= DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x01		# Analogmodul_A I2C Adresse 0x08 (U1), 0x18 (U5) (JP1=0, JP2=0, JP3=x, JP4=x)
DEVICE_ANALOGMODUL_A_ID02		= DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x02		# Analogmodul_A I2C Adresse 0x0A (U1), 0x1A (U5) (JP1=0, JP2=1, JP3=1, JP4=0)
DEVICE_ANALOGMODUL_A_ID03		= DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x03		# Analogmodul_A I2C Adresse 0x0B (U1), 0x1B (U5) (JP1=x, JP2=1, JP3=1, JP4=x)
DEVICE_ANALOGMODUL_A_ID04		= DEVICE_CLASS_ANALOGMODUL | DEVICE_TYPE_A | 0x04		# Analogmodul_A I2C Adresse 0x09 (U1), 0x19 (U5) (JP1=0, JP2=x, JP3=x, JP4=0)


#---------------------------------------------------------------------------------------------------------------------------------------
# hardware register defines MCP23017
#---------------------------------------------------------------------------------------------------------------------------------------
IODIRA = 0x00 # Pin Register fuer die Richtung
IODIRB = 0x01 # Pin Register fuer die Richtung
OLATA = 0x14  # Register fuer Ausgabe (GPB)
OLATB = 0x15  # Register fuer Ausgabe (GPB)


#---------------------------------------------------------------------------------------------------------------------------------------
# hardware register defines LTC2309
#---------------------------------------------------------------------------------------------------------------------------------------
LTC2309_SD_SINGLE	= 0x80
LTC2309_OS_ODD		= 0x40
LTC2309_S1				= 0x20
LTC2309_S0				= 0x10
LTC2309_UNI				= 0x08
LTC2309_SLEEP			= 0x04

LTC2309_CHANNEL0	= (LTC2309_SD_SINGLE | LTC2309_UNI)	
LTC2309_CHANNEL1	= (LTC2309_SD_SINGLE | LTC2309_UNI | LTC2309_OS_ODD)
LTC2309_CHANNEL2  = (LTC2309_SD_SINGLE | LTC2309_UNI | LTC2309_S0)
LTC2309_CHANNEL3  = (LTC2309_SD_SINGLE | LTC2309_UNI | LTC2309_OS_ODD | LTC2309_S0)
LTC2309_CHANNEL4  = (LTC2309_SD_SINGLE | LTC2309_UNI | LTC2309_S1)
LTC2309_CHANNEL5  = (LTC2309_SD_SINGLE | LTC2309_UNI | LTC2309_OS_ODD | LTC2309_S1)
LTC2309_CHANNEL6  = (LTC2309_SD_SINGLE | LTC2309_UNI | LTC2309_S1 | LTC2309_S0)
LTC2309_CHANNEL7  = (LTC2309_SD_SINGLE | LTC2309_UNI | LTC2309_OS_ODD | LTC2309_S1 | LTC2309_S0)


#---------------------------------------------------------------------------------------------------------------------------------------
# software defines
#---------------------------------------------------------------------------------------------------------------------------------------
GPIO_WATCHDOG 			= 12 # Watchdog output
GPIO_I2CSTATE 			= 7  # I2C Zustand: 1 senden verboten 0: senden erlaubt
GPIO_RUN						= 5
GPIO_CTRL_K01 			= 19 # Relais K01 on Controllermodul_A
GPIO_CTRL_K02 			= 26 # Relais K02 on Controllermodul_A
GPIO_SENSOR_SUPPLY 	= 21


#---------------------------------------------------------------------------------------------------------------------------------------
# Helper classes
#---------------------------------------------------------------------------------------------------------------------------------------
class Average:
  buffer=[]
  idx=0
  lock = 0
  error = 0
  def __init__(self):
    self.buffer=[0,0,0,0,0]
    self.idx=0
    self.lock=threading.Lock()
    return
    
  def Init(self, val):
    if ( (val < 0) or (val>4095) ):
      self.error=1
      return
    else:
      self.error=0
      
    self.lock.acquire()
    self.buffer[0]=val
    self.buffer[1]=val
    self.buffer[2]=val
    self.buffer[3]=val
    self.buffer[4]=val
    self.lock.release()
    self.idx=0
    self.error=0
    
  def Push(self, val):
    if ( (val < 0) or (val>4095) ):
      self.error=1
      return
    else:
      self.error=0
      
    self.lock.acquire()
    self.buffer[self.idx]=val
    self.lock.release()
    self.idx=self.idx+1
    if (self.idx > 4):
      self.idx=0
    return
    
  def Get(self):
    self.lock.acquire()
    sum = self.buffer[0]+self.buffer[1]+self.buffer[2]+self.buffer[3]+self.buffer[4]
    self.lock.release()
    return (sum/5)

class Device:
  type=0;
  adcCh=[]
  i2cA=0
  i2cB=0
  shadowA=0
  shadowB=0
  isInitialized=0
  i2cInitReq=0
  lastCmd=0
  def __init__(self, type):
    self.type = type
    self.adcCh=[]
    self.i2cA=0
    self.i2cB=0
    self.shadowA=0
    self.shadowB=0
    self.isInitialized=0
    self.wtdCount=-1

class Watchdog:
  id=0
  wtdCount=0
  def __init__(self, id):
    self.wtdCount=10
    self.id=id
    
#---------------------------------------------------------------------------------------------------------------------------------------
# global variables
#---------------------------------------------------------------------------------------------------------------------------------------
i2cBus = smbus.SMBus(1)
DeviceList = []
DeviceList.append(Device(DEVICE_CONTROLLER_A_ID01))
WatchdogList = []
AliveCount_Adc = 0
AliveCount_Lock=threading.Lock()

 
#---------------------------------------------------------------------------------------------------------------------------------------
# watchdog thread
#---------------------------------------------------------------------------------------------------------------------------------------
def watchdog_thread(v):
  global AliveCount_Adc
  global AliveCount_Lock
  global WatchdogList
  global i2cState
  global i2cStateLast
  
  wdt = 0
  
  while True:
    allowWtd=1
    AliveCount_Lock.acquire
    for w in WatchdogList:
      if ( w.wtdCount > 0 ):
        w.wtdCount=w.wtdCount-1
      if ( w.wtdCount == 0 ):
        allowWtd=0
    AliveCount_Lock.release
    if ( wdt == 0 ):
      wdt = 1
      if ( allowWtd == 1 ):
        GPIO.output(GPIO_WATCHDOG,0) 
      GPIO.output(GPIO_RUN,0) 
    else:
      wdt = 0
      if ( allowWtd == 1 ):
        GPIO.output(GPIO_WATCHDOG,1)
      GPIO.output(GPIO_RUN,1) 
   
    if ( allowWtd == 1 ):
      time.sleep(0.5)
    else:
      time.sleep(0.1)
    

#---------------------------------------------------------------------------------------------------------------------------------------
# Adc Conversion thread
#---------------------------------------------------------------------------------------------------------------------------------------
def AdcConversion_Thread(v):
  global DeviceList
  global AliveCount_Adc
  global AliveCount_Lock
  GPIO.output(GPIO_SENSOR_SUPPLY,0) 
  devIdx=0 
  while True:
    devIdx = 0
    AliveCount_Lock.acquire()
    if ( AliveCount_Adc < 10 ):
      AliveCount_Adc = AliveCount_Adc + 5
    if ( AliveCount_Adc > 10 ):
      AliveCount_Adc = 10
    AliveCount_Lock.release()
      
    if(GPIO.input(GPIO_I2CSTATE) == GPIO.HIGH):
      DeInitAllDevices()
      
    for dev in DeviceList:
      if ( ((DEVICE_CLASS & dev.type) == DEVICE_CLASS_ANALOGMODUL) and ((DEVICE_TYPE & dev.type) == DEVICE_TYPE_A) ):
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL0)
        #print 'CH0=',adc
        dev.adcCh[0].Push(adc)
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL1)
        #print 'CH1=',adc
        dev.adcCh[1].Push(adc)
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL2)
        #print 'CH2=',adc
        dev.adcCh[2].Push(adc)
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL3)
        #print 'CH3=',adc
        dev.adcCh[3].Push(adc)
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL4)
        #print 'CH4=',adc
        dev.adcCh[4].Push(adc)
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL5)
        #print 'CH5=',adc
        dev.adcCh[5].Push(adc)
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL6)
        #print 'CH6=',adc
        dev.adcCh[6].Push(adc)
        adc=ReadLTC2309(dev.i2cA, LTC2309_CHANNEL7)
        #print 'CH7=',adc
        dev.adcCh[7].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL0)
        #print 'CH8=',adc
        dev.adcCh[8].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL1)
        #print 'CH9=',adc
        dev.adcCh[9].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL2)
        #print 'CH10=',adc
        dev.adcCh[10].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL3)
        #print 'CH11=',adc
        dev.adcCh[11].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL4)
        #print 'CH12=',adc
        dev.adcCh[12].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL5)
        #print 'CH13=',adc
        dev.adcCh[13].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL6)
        #print 'CH14=',adc
        dev.adcCh[14].Push(adc)
        adc=ReadLTC2309(dev.i2cB, LTC2309_CHANNEL7)
        #print 'CH15=',adc
        dev.adcCh[15].Push(adc)
      devIdx=devIdx+1
    
    #sensor supply off ("1" inverted because of Transistor)
    GPIO.output(GPIO_SENSOR_SUPPLY,1)  
    time.sleep(0.9)
    #sensor supply on ("0")
    GPIO.output(GPIO_SENSOR_SUPPLY,0)
    time.sleep(0.1)

  
    
#---------------------------------------------------------------------------------------------------------------------------------------
# SendI2C
#---------------------------------------------------------------------------------------------------------------------------------------
def SendI2C(i2cAddr, reg, data):
  #print 'SendI2C', i2cAddr, reg, data
  if(GPIO.input(GPIO_I2CSTATE) == GPIO.LOW):
    try:
      i2cBus.write_byte_data(i2cAddr,reg, data)
    except IOError:
      return
  #else:
    #print 'SendI2C forbidden'
  return
    
 
#---------------------------------------------------------------------------------------------------------------------------------------
# ReadLTC2309
#---------------------------------------------------------------------------------------------------------------------------------------
def ReadLTC2309(addr, adCh):
  adcVal=0
  if(GPIO.input(GPIO_I2CSTATE) == GPIO.LOW):
    try:
      data_raw = i2cBus.read_word_data(addr,adCh)
      adcVal = ((data_raw&0xFF00)>>8)+((data_raw&0x00FF)<<8)
      adcVal=adcVal>>4
    except IOError:
      adcVal = -1
    
  return adcVal
  
  
#---------------------------------------------------------------------------------------------------------------------------------------
# GetFromDeviceList
#
# 
#---------------------------------------------------------------------------------------------------------------------------------------
def GetFromDeviceList(dev):
  global DeviceList
  found=0
  
  it=-1
  for d in DeviceList:
    it=it+1
    if (d.type == dev):
      found=1
      break
  
  if ( found == 0 ):
    DeviceList.append(Device(dev));
    #print 'GetFromDeviceList: new device added: ',it+1
    return it+1
  else:
    #print 'GetFromDeviceList: found requested device: ',it
    return it
   
    
#---------------------------------------------------------------------------------------------------------------------------------------
# DeInitAllDevices
#---------------------------------------------------------------------------------------------------------------------------------------
def DeInitAllDevices():
  global DeviceList
   
  for dev in DeviceList:
    dev.isInitialized = 0
  
  
#---------------------------------------------------------------------------------------------------------------------------------------
# init_Schaltmodul_A
#
# function supports all relevant I2C adresses (0x20...0x27)
#---------------------------------------------------------------------------------------------------------------------------------------
def init_Schaltmodul_A(idx):
  global DeviceList
  id = (DEVICE_ADDRESS & DeviceList[idx].type)
  
  if ( (id < 1) or (id > 8) ):
    return
  
  DeviceList[idx].i2cA = 32+id-1
  DeviceList[idx].shadowA = 0
  DeviceList[idx].shadowB = 0
  
  SendI2C(DeviceList[idx].i2cA,IODIRA,0x00)
  SendI2C(DeviceList[idx].i2cA,IODIRB,0x00)
  SendI2C(DeviceList[idx].i2cA, OLATA, DeviceList[idx].shadowA)
  SendI2C(DeviceList[idx].i2cA, OLATB, DeviceList[idx].shadowB)
  SendI2C(DeviceList[idx].i2cA, OLATA, 0)
  DeviceList[idx].isInitialized=1
  
  
#---------------------------------------------------------------------------------------------------------------------------------------
# handle_Schaltmodul_A
#
# 
#---------------------------------------------------------------------------------------------------------------------------------------
def handle_Schaltmodul_A(cmd, devIdx):
  global DeviceList
  rv = 'NAK' 
  i2cAddr = DeviceList[devIdx].i2cA
  
  if ( len(cmd) < 4 ):
    return rv

  command = cmd[2]
  switch = cmd[3]
  if ( command == 'SET' ):
    state = cmd[4]
  
  port = 0
  bitmask = 0
  
  if ( switch == "K01" ):
    bitmask = 0x01
  elif ( switch == "K02" ):
    bitmask = 0x2
  elif ( switch == "K03" ):
    bitmask = 0x4
  elif ( switch == "K04" ):
    bitmask = 0x1
    port = 1
  elif ( switch == "K06" ):
    bitmask = 0x10
  elif ( switch == "K07" ):
    bitmask = 0x20
  elif ( switch == "K08" ):
    bitmask = 0x40
  elif ( switch == "K09" ):
    bitmask = 0x8
  elif ( switch == "K10" ):
    bitmask = 0x2
    port = 1
  elif ( switch == "K11" ):
    bitmask = 0x4
    port = 1
  elif ( switch == "K05" ):
    bitmask = 0x8
    port = 1
  else:
    return rv
  	
  if ( command == "SET" ):
    if ( port == 0 ):  
  	  newVal = DeviceList[devIdx].shadowA
    else:
      newVal = DeviceList[devIdx].shadowB
  
    if ( state == "ON" ):
      newVal |= bitmask
    elif ( state == "OFF" ):
      newVal &= ~bitmask
    else:
      return rv
    
    if ( port == 0 ):  
  	  if ( newVal != DeviceList[devIdx].shadowA ):
  	    SendI2C(i2cAddr, OLATA, newVal)
  	    DeviceList[devIdx].shadowA = newVal
    else:
      if ( newVal != DeviceList[devIdx].shadowB ):
        SendI2C(i2cAddr, OLATB, newVal)
        DeviceList[devIdx].shadowB = newVal
    return 'ACK'
  elif ( command == "GET" ):
    if ( port == 0 ):
      if ( (DeviceList[devIdx].shadowA & bitmask) == bitmask ):
        return '1'
      else:
        return '0'
    else:
      if ( (DeviceList[devIdx].shadowB & bitmask) == bitmask ):
        return '1'
      else:
        return '0'
  else:
    return 'NAK'
  
  
#---------------------------------------------------------------------------------------------------------------------------------------
# init_Schaltmodul_B
#
# function supports all relevant I2C adresses (0x20...0x27)
#---------------------------------------------------------------------------------------------------------------------------------------
def init_Schaltmodul_B(idx):
  global DeviceList
  id = (DEVICE_ADDRESS & DeviceList[idx].type)

  if ( (id < 1) or (id > 8) ):
    return
  
  DeviceList[idx].i2cA = 32+id-1
  #print 'init_Schaltmodul_B: id=',DeviceList[idx].i2cA
  DeviceList[idx].shadowA = 0
  DeviceList[idx].shadowB = 0
  SendI2C(DeviceList[idx].i2cA,IODIRA,0x00)
  SendI2C(DeviceList[idx].i2cA,IODIRB,0x00)
  SendI2C(DeviceList[idx].i2cA, OLATA, DeviceList[idx].shadowA)
  SendI2C(DeviceList[idx].i2cA, OLATB, DeviceList[idx].shadowB)
  SendI2C(DeviceList[idx].i2cA, OLATA, 0)
  DeviceList[idx].isInitialized=1


#---------------------------------------------------------------------------------------------------------------------------------------
# handle_Schaltmodul_B
#
# 
#---------------------------------------------------------------------------------------------------------------------------------------
def handle_Schaltmodul_B(cmd, devIdx):
  global DeviceList
  
  rv = 'NAK' 
  
  if ( len(cmd) < 4 ):
    return rv

  command = cmd[4]
  switch = cmd[3]
  #print command
  #print switch
  bitmask = DeviceList[devIdx].shadowA
  
  if (switch == "SH1") and (command=="UP"):
    bitmask &= ~0x10																	#Befehl vorbereiten: Relais runter ausschalten
    bitmask |= 0x08																		#Befehl vorbereiten: Relais hoch einschalten							
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)	#Befehl senden
    time.sleep(0.4)																		#Puls 0.4s  (Relais hoch)
    bitmask &= ~0x08																	#Befehl vorbereiten: Relais hoch ausschalten
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)	#Befehl senden
    time.sleep(0.2)																		#warten, damit Befehlssequenzen von den Jalousieschaltern erkannt werden
    DeviceList[devIdx].shadowA = bitmask;
  elif (switch == "SH1") and (command=="DOWN"):
    bitmask &= ~0x08
    bitmask |= 0x10
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)
    time.sleep(0.4)
    bitmask &= ~0x10
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)
    time.sleep(0.2)
    DeviceList[devIdx].shadowA = bitmask;
  elif (switch == "SH2") and (command=="UP"):
    bitmask &= ~0x01
    bitmask |= 0x02
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)
    time.sleep(0.4)
    bitmask &= ~0x02
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)
    time.sleep(0.2)
    DeviceList[devIdx].shadowA = bitmask;
  elif (switch == "SH2") and (command=="DOWN"):
    bitmask &= ~0x02
    bitmask |= 0x01
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)
    time.sleep(0.4)
    bitmask &= ~0x01
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)
    time.sleep(0.2)
    DeviceList[devIdx].shadowA = bitmask;
  elif (switch == "K01") and (command=="ON"):
    bitmask |= 0x20
  elif (switch == "K01") and (command=="OFF"):
    bitmask &= ~0x20
  elif (switch == "K02") and (command=="ON"):
    bitmask |= 0x40
  elif (switch == "K02") and (command=="OFF"):
    bitmask &= ~0x40
  elif (switch == "K03") and (command=="ON"):
    bitmask |= 0x04
  elif (switch == "K03") and (command=="OFF"):
    bitmask &= ~0x04
  else:
    #print 'handle_Schaltmodul_B: error'
    return rv
  
  if ( bitmask != DeviceList[devIdx].shadowA ):	
    SendI2C(DeviceList[devIdx].i2cA, OLATA, bitmask)

  rv = 'ACK'
  DeviceList[devIdx].shadowA = bitmask;
  
  return rv


#---------------------------------------------------------------------------------------------------------------------------------------
# init_Analogmodul_A
#---------------------------------------------------------------------------------------------------------------------------------------
def init_Analogmodul_A(devIdx):
  global DeviceList
  id = (DEVICE_ADDRESS & DeviceList[devIdx].type)
  if ( id == 1 ):
    DeviceList[devIdx].i2cA = 0x18
    DeviceList[devIdx].i2cB = 0x08
  elif ( id == 2 ):
    DeviceList[devIdx].i2cA = 0x0A
    DeviceList[devIdx].i2cB = 0x1A
  elif ( id == 3 ):
    DeviceList[devIdx].i2cA = 0x0B
    DeviceList[devIdx].i2cB = 0x1B  
  elif ( id == 4 ):
    DeviceList[devIdx].i2cA = 0x09
    DeviceList[devIdx].i2cB = 0x19
  else:
    return
    
  DeviceList[devIdx].adcCh=[Average(),Average(),Average(),Average(),
                            Average(),Average(),Average(),Average(),
                            Average(),Average(),Average(),Average(),
                            Average(),Average(),Average(),Average()] 
  
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL0)
  DeviceList[devIdx].adcCh[0].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL1)
  DeviceList[devIdx].adcCh[1].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL2)
  DeviceList[devIdx].adcCh[2].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL3)
  DeviceList[devIdx].adcCh[3].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL4)
  DeviceList[devIdx].adcCh[4].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL5)
  DeviceList[devIdx].adcCh[5].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL6)
  DeviceList[devIdx].adcCh[6].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cA, LTC2309_CHANNEL7)
  DeviceList[devIdx].adcCh[7].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL0)
  DeviceList[devIdx].adcCh[8].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL1)
  DeviceList[devIdx].adcCh[9].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL2)
  DeviceList[devIdx].adcCh[10].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL3)
  DeviceList[devIdx].adcCh[11].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL4)
  DeviceList[devIdx].adcCh[12].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL5)
  DeviceList[devIdx].adcCh[13].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL6)
  DeviceList[devIdx].adcCh[14].Init(adc)
  adc=ReadLTC2309(DeviceList[devIdx].i2cB, LTC2309_CHANNEL7)
  DeviceList[devIdx].adcCh[15].Init(adc)
  DeviceList[devIdx].isInitialized=1
 	
#---------------------------------------------------------------------------------------------------------------------------------------
# handle_Analogmodul_A
#---------------------------------------------------------------------------------------------------------------------------------------
def handle_Analogmodul_A(cmd, devIdx):
  global DeviceList
  adc = 'NAK'
    
  channel = cmd[3]
  
  if ( channel == "T16" ):
    if ( DeviceList[devIdx].adcCh[0].error == 0 ):
      adc=DeviceList[devIdx].adcCh[0].Get()
  elif ( channel == "T05" ):
    if ( DeviceList[devIdx].adcCh[1].error == 0 ):
      adc=DeviceList[devIdx].adcCh[1].Get()
  elif ( channel == "T06" ):
    if ( DeviceList[devIdx].adcCh[2].error == 0 ):
      adc=DeviceList[devIdx].adcCh[2].Get()
  elif ( channel == "T07" ):
    if ( DeviceList[devIdx].adcCh[3].error == 0 ):
      adc=DeviceList[devIdx].adcCh[3].Get()
  elif ( channel == "T08" ):
    if ( DeviceList[devIdx].adcCh[4].error == 0 ):
      adc=DeviceList[devIdx].adcCh[4].Get()
  elif ( channel == "T13" ):
    if ( DeviceList[devIdx].adcCh[5].error == 0 ):
      adc=DeviceList[devIdx].adcCh[5].Get()
  elif ( channel == "T14" ):
    if ( DeviceList[devIdx].adcCh[6].error == 0 ):
      adc=DeviceList[devIdx].adcCh[6].Get()
  elif ( channel == "T15" ):
    if ( DeviceList[devIdx].adcCh[7].error == 0 ):
      adc=DeviceList[devIdx].adcCh[7].Get()
  elif ( channel == "T12" ):
    if ( DeviceList[devIdx].adcCh[8].error == 0 ):
      adc=DeviceList[devIdx].adcCh[8].Get()
  elif ( channel == "T01" ):
    if ( DeviceList[devIdx].adcCh[9].error == 0 ):
      adc=DeviceList[devIdx].adcCh[9].Get()
  elif ( channel == "T02" ):
    if ( DeviceList[devIdx].adcCh[10].error == 0 ):
      adc=DeviceList[devIdx].adcCh[10].Get()
  elif ( channel == "T03" ):
    if ( DeviceList[devIdx].adcCh[11].error == 0 ):
      adc=DeviceList[devIdx].adcCh[11].Get()
  elif ( channel == "T04" ):
    if ( DeviceList[devIdx].adcCh[12].error == 0 ):
      adc=DeviceList[devIdx].adcCh[12].Get()
  elif ( channel == "T09" ):
    if ( DeviceList[devIdx].adcCh[13].error == 0 ):
      adc=DeviceList[devIdx].adcCh[13].Get()
  elif ( channel == "T10" ):
    if ( DeviceList[devIdx].adcCh[14].error == 0 ):
      adc=DeviceList[devIdx].adcCh[14].Get()
  elif ( channel == "T11" ):
    if ( DeviceList[devIdx].adcCh[15].error == 0 ):
      adc=DeviceList[devIdx].adcCh[15].Get()
  else:
    adc = 'NAK'
  
  return adc


#---------------------------------------------------------------------------------------------------------------------------------------
# handle_Watchdog
#---------------------------------------------------------------------------------------------------------------------------------------
def handle_Watchdog(id):
  global WatchdogList
  global AliveCount_Lock
  found = 0
  
  for w in WatchdogList:
    if ( w.id == id ):
      found = 1
      AliveCount_Lock.acquire
      w.wtdCount = 10
      AliveCount_Lock.release
     
  if ( found == 0 ):
   AliveCount_Lock.acquire
   WatchdogList.append(Watchdog(id))
   AliveCount_Lock.release
  
#---------------------------------------------------------------------------------------------------------------------------------------
# handle_Controllermodul_A
#---------------------------------------------------------------------------------------------------------------------------------------
def handle_Controllermodul_A(cmd):
  rv = 'ACK'
  
  if ( cmd[2] == "WTD" ):
    handle_Watchdog(cmd[3]) 
  elif ( cmd[3] == "K01"):
    if ( cmd[4] == "ON" ):
      GPIO.output(GPIO_CTRL_K01, 1) 
    elif ( cmd[4] == "OFF" ):
      GPIO.output(GPIO_CTRL_K01, 0)
    else:
      rv = 'NAK' 
  elif ( cmd[3] == "K02" ):
    if ( cmd[4] == "ON" ):
      GPIO.output(GPIO_CTRL_K02, 1) 
    elif ( cmd[4] == "OFF" ):
      GPIO.output(GPIO_CTRL_K02, 0)
    else:
      rv = 'NAK'
  else:
    rv = 'NAK'
    
  return rv
  
   
#---------------------------------------------------------------------------------------------------------------------------------------
# handle_Request
#---------------------------------------------------------------------------------------------------------------------------------------
def handle_Request(data):  
  global DeviceList
 
  cmd = data.split(",")
  dev = int(cmd[1], 16)

  if ( ((DEVICE_CLASS & dev) == DEVICE_CLASS_CONTROLLER) and ((DEVICE_TYPE & dev) == DEVICE_TYPE_A) ):
    rv = handle_Controllermodul_A(cmd)
    
  elif ( GPIO.input(GPIO_I2CSTATE) == GPIO.HIGH ):
    rv = 'NAK'
      
  elif ( ((DEVICE_CLASS & dev) == DEVICE_CLASS_SCHALTMODUL) and ((DEVICE_TYPE & dev) == DEVICE_TYPE_A) ):
    devIdx = GetFromDeviceList(dev)
    if ( DeviceList[devIdx].isInitialized == 0 ):
      init_Schaltmodul_A(devIdx)
    if ( DeviceList[devIdx].isInitialized == 1 ):
      rv = handle_Schaltmodul_A(cmd, (DEVICE_ADDRESS&dev))
    else:
      rv = 'NAK'

  elif ( ((DEVICE_CLASS & dev) == DEVICE_CLASS_ANALOGMODUL) and ((DEVICE_TYPE & dev) == DEVICE_TYPE_A) ):
    devIdx = GetFromDeviceList(dev)
    if ( DeviceList[devIdx].isInitialized == 0 ):
      init_Analogmodul_A(devIdx)
    if ( DeviceList[devIdx].isInitialized == 1 ):
      rv = handle_Analogmodul_A(cmd, devIdx)
    else:
      rv = 'NAK'

  elif ( ((DEVICE_CLASS & dev) == DEVICE_CLASS_SCHALTMODUL) and ((DEVICE_TYPE & dev) == DEVICE_TYPE_B) ):
    devIdx = GetFromDeviceList(dev)
    if ( DeviceList[devIdx].isInitialized == 0 ):
      init_Schaltmodul_B(devIdx)
    if ( DeviceList[devIdx].isInitialized == 1 ):
      rv = handle_Schaltmodul_B(cmd, devIdx)
    else:
      rv = 'NAK'

  else:
    rv = 'NAK'

  return (str(rv))


#---------------------------------------------------------------------------------------------------------------------------------------
# init after start
#---------------------------------------------------------------------------------------------------------------------------------------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_CTRL_K01, GPIO.OUT)
GPIO.setup(GPIO_CTRL_K02, GPIO.OUT)
GPIO.setup(GPIO_WATCHDOG, GPIO.OUT)
GPIO.setup(GPIO_RUN, GPIO.OUT)       			# watchdog output to avr microcontroller
GPIO.setup(GPIO_I2CSTATE, GPIO.IN)   			# i2c state from avr microcontroller 1: Raspberry must not send I2C data
GPIO.setup(GPIO_SENSOR_SUPPLY, GPIO.OUT)  # adc sensor power supply
GPIO.output(GPIO_SENSOR_SUPPLY,0)         # disable adc sensor power supply
GPIO.output(GPIO_RUN, 0)
GPIO.output(GPIO_CTRL_K01, 0)                    
GPIO.output(GPIO_CTRL_K02, 0)

start_new_thread(watchdog_thread, (0,))
start_new_thread(AdcConversion_Thread, (0,))	# start continuous ADC data aqusition


#---------------------------------------------------------------------------------------------------------------------------------------
# main loop
#---------------------------------------------------------------------------------------------------------------------------------------
serversock = socket(AF_INET, SOCK_DGRAM)
ADDR = (HOST, PORT)
serversock.bind(ADDR)
print 'waiting for UDP connection on port', PORT

while 1:
  data, sender_addr = serversock.recvfrom(128)
  #print 'Req: ',data
  
  try:
    resp = handle_Request(data)
  except:
    resp = 'NAK'
  
  resp += "\n"
  serversock.sendto(resp, sender_addr)
