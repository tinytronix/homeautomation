#!/usr/bin/python
#---------------------------------------------------------------------------------------------------------------------------------------
#
# Dieses Python Script implementiert ein Software-UDP-Lora-Gateway.
# Daten werden per UDP entgegengenommen, dann per I2C an das Hardware-Lora-Gateway weitergegeben, welches die per I2C empfangenen 
# Daten (Request) per Funk an den entsprechenden Lora-Node sendet und auf eine Antwort (Response) wartet.
# Wenn eine Antwort vom Lora-Node im Gateway vorliegt, wird diese Antwort per I2C abgerufen und dann per UDP zurueckgegeben.
#
# Um eine zu hohe Sendehaeufigkeit best moeglich zu vermeiden, fuehrt dieses Programm eine Liste, in der jeder Request und die entsprechende
# Response mit Timestamp verzeichnet ist. Wenn ein Request erkannt wurde, der in genau dieser Form zuvor schon an einen 
# Node versendet wurde, wird ein erneutes Senden innerhalb einer bestimmten Zeit (SENDINTERVAL) unterbunden udn es wird
# stattdessen die zuvor empfangene Response per UDP zurueckgegeben. Somit wird kein I2C Traffic und auch kein Lora-Sendevorgang
# ausgeloest.
#
#---------------------------------------------------------------------------------------------------------------------------------------


 
#---------------------------------------------------------------------------------------------------------------------------------------
# imports
#---------------------------------------------------------------------------------------------------------------------------------------
from socket import *  
import RPi.GPIO as GPIO   
import time
import smbus


#---------------------------------------------------------------------------------------------------------------------------------------
# Gateway configuration
#---------------------------------------------------------------------------------------------------------------------------------------
HOST                                = "0.0.0.0"   
PORT                                = 49230     #UDP Server Port
SENDINTERVAL                        = 60        #Intervall in Sekunden, in dem Daten an einen Node gesendet werden. (Bei Aenderung - bspw. An->Aus wird sofort gesendet


#---------------------------------------------------------------------------------------------------------------------------------------
# I2C
#---------------------------------------------------------------------------------------------------------------------------------------
I2C_SLAVE_ADDR                      = 0x63      #I2C Adresse des Lora Gateways
I2C_REGADDR_SENDBUFFER              = 0x90      #I2C Register Adresse des Lora Sendepuffers
I2C_REGADDR_RESPONSESTATUS          = 0x81      #I2C Register Adresse zur Abfrage, ob bereits eine Response eingetroffen ist
GPIO_I2CSTATE 			                = 7  # I2C Zustand: 1 senden verboten 0: senden erlaubt


#---------------------------------------------------------------------------------------------------------------------------------------
# LoRa Protocol definitions
#---------------------------------------------------------------------------------------------------------------------------------------
LORA_ACTOR_REQ											=	0x01
LORA_ACTOR_RESP											=	0x02
LORA_SENSOR_REQ											=	0x03
LORA_SENSOR_RESP										=	0x04
LORA_EEPWRITE_REQ										=	0x05
LORA_EEPWRITE_RESP									=	0x06
LORA_EEPREAD_REQ										=	0x07
LORA_EEPREAD_RESP										=	0x08
LORA_PROPERTY_REQ										=	0x09
LORA_PROPERTY_RESP									=	0x0A


class Command:
  devId=0
  cmdId=0
  channelId=0
  action=0
  timestamp=0
  value=0
  def __init__(self, devId, cmdId, channelId, action):
    self.devId = devId
    self.cmdId = cmdId
    self.channelId = channelId
    self.action = action


#---------------------------------------------------------------------------------------------------------------------------------------
# global variables
#---------------------------------------------------------------------------------------------------------------------------------------
i2cBus = smbus.SMBus(1)
CommandList = []


#---------------------------------------------------------------------------------------------------------------------------------------
# init at start
#---------------------------------------------------------------------------------------------------------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_I2CSTATE, GPIO.IN)


#---------------------------------------------------------------------------------------------------------------------------------------
# Check_LORA_ACTOR_REQ
#
# Diese Funktion prueft, ob genau der gleiche Request zuvor bereits abgeschickt wurde, um 
# zu vermeiden, dass unnoetig Daten per Lora gesendet werden 
# 
# Parameter:
# radioId: ID des Lora Nodes, fuer den die Daten gedacht sind
# channelId: Die ID des angesprochenen Sensors oder Aktors
# action: Nur bei Aktoren: Aktion, die ausgefuehrt werden soll, An, Aus etc...
#
# Rueckgabewert:
# array 
# arr[0]: index desObjektes in der CommandList
# arr[1]: True: kann gesendet werden   False: Wurde zuvor bereits gesendet
#---------------------------------------------------------------------------------------------------------------------------------------
def Check_LORA_ACTOR_REQ(radioId, channelId, action):
  global CommandList
  status = 0
  idx=-1
  rv = True
  for c in CommandList:
    if (c.devId == radioId):
      if (c.cmdId == LORA_ACTOR_REQ):
        if (c.channelId == channelId):
          if ( c.action == action):
            status=1
            rv = False
            break
          elif ( c.action != action):
            status=2  
            break
    idx=idx+1
  
  if ( status == 0 ):
    CommandList.append(Command(radioId, LORA_ACTOR_REQ, channelId, action))
    idx=idx+1
  
  
  return [idx,rv] 


#---------------------------------------------------------------------------------------------------------------------------------------
# WriteI2cBlockData
#
# Parameter:
# reg: I2C Registernummer (offset, an den geschrieben werden soll)
# data: die zu schreibenden Daten
#
# Rueckgabewert:
# True: Daten erfolgreich geschrieben
# False: Fehler beim Schreiben, I2C nicht erfolgreich
#
#---------------------------------------------------------------------------------------------------------------------------------------
def WriteI2cBlockData(reg, data):
  if(GPIO.input(GPIO_I2CSTATE) == GPIO.LOW):
    try:
      i2cBus.write_i2c_block_data(I2C_SLAVE_ADDR, reg, data)
      return True
    except IOError:
      return False
  else:
   return False
      


#---------------------------------------------------------------------------------------------------------------------------------------
# ReadI2cBlockData
#
# Parameter:
# reg: I2C Registernummer (offset, von dem gelesen werden soll)
# len: Anzahl der zu lesenden Bytes
#
# Rueckgabewert:
# array, welches die gelesenen Bytes enthaelt
#
#---------------------------------------------------------------------------------------------------------------------------------------
def ReadI2cBlockData(reg, len):
  if(GPIO.input(GPIO_I2CSTATE) == GPIO.LOW):
    try:
      return i2cBus.read_i2c_block_data(I2C_SLAVE_ADDR, reg, len)
    except IOError:
      return False
  else:
    return False
    

#---------------------------------------------------------------------------------------------------------------------------------------
# ReadI2cByteData
#
# Parameter:
# reg: I2C Registernummer (offset, von dem gelesen werden soll)
#
# Rueckgabewert:
# Byte, welches gelesen Bytes wurde
# None: falls es ein I2C Fehler erkannt wurde
#
#---------------------------------------------------------------------------------------------------------------------------------------
def ReadI2cByteData(reg):
  if(GPIO.input(GPIO_I2CSTATE) == GPIO.LOW):
    try:
      return i2cBus.read_byte_data(I2C_SLAVE_ADDR, reg)
    except IOError:
      return None
  else:
    return None
    


#---------------------------------------------------------------------------------------------------------------------------------------
# WaitForResponse
#
# Diese Funktion fragt beim Gateway per I2C maximal 8x ab, ob fuer die soeben verschickte Anfrage (Request)
# bereits eine Antwort (Response) empfangen wurde. 
#
# Parameter:
# nBytes: Anzahl der erwarteten Response-Bytes
#
# Rueckgabewert:
# True: Response wurde empfangen
# False: Response wurde nicht empfangen
# 
#---------------------------------------------------------------------------------------------------------------------------------------
def WaitForResponse(nBytes):
  time.sleep(0.06)
  
  for i in xrange(8):
    rv = ReadI2cByteData(I2C_REGADDR_RESPONSESTATUS)
    if ( rv == nBytes ):
      return True
    elif ( rv == None ):
      return False
    else:
      time.sleep(0.03)
    
  return False


#---------------------------------------------------------------------------------------------------------------------------------------
# ConvertAndCheckRequest		
#
# Konvertiert den von der UDP Schnittstelle kommenden Command String (Beispiel DINR,0x2020001,SET,K02,ON) 
# in einzelne Variablen, die dann per I2C an das Lora-Gateway geschickt werden.
#
# DINR,0x2020001,SET,K02,ON
#       |         |   |  |
#       |         |   |  +---  i2cCmd[4]
#       |         |   +------  i2cCmd[3]
#       |         +----------- i2cCmd[2]
#       +--------------------- i2cCmd[1]
# 
# i2cCmd[0]:
# True: Command is ok
# False: Command is not ok
#---------------------------------------------------------------------------------------------------------------------------------------
def ConvertAndCheckRequest(data):

  i2cCmd = [True,0,0,0,0,0]
  cmd = data.split(",")
  i2cCmd[1] = int(cmd[1], 16)
 
  if ( cmd[2] == 'SET' ):
    i2cCmd[2] = LORA_ACTOR_REQ
    if ( cmd[4] == 'ON' ):
      i2cCmd[4] = 1
    elif ( cmd[4] == 'OFF' ):
      i2cCmd[4] = 0
    else:
      i2cCmd[0] = False
    
    i2cCmd[3] = (int)(filter(str.isdigit, cmd[3]))

  elif ( cmd[2] == 'GET' ):
    i2cCmd[2] = LORA_SENSOR_REQ
    i2cCmd[3] = (int)(filter(str.isdigit, cmd[3]))
    i2cCmd[3] = i2cCmd[3] - 1

  else:
    i2cCmd[0] = False
   
  if ( (i2cCmd[3] > 255) or (i2cCmd[3] < 0) ):
    i2cCmd[0] = False
  
  return i2cCmd


#---------------------------------------------------------------------------------------------------------------------------------------
# Check_LORA_ACTOR_REQ
#
# Um zu vermeiden, dass unnoetig Daten per Funk gesendet werden, prueft 
# diese Funktion, ob genau der gleiche Request zuvor bereits abgeschickt wurde.
# Wenn ja, wird nicht gesendet und es wird nur der Status des letzten Sendevorganges
# zurueckgegeben.
#
# Parameter:
# radioId: ID des Lora Nodes, fuer den die Daten gedacht sind
# channelId: Die ID des angesprochenen Sensors oder Aktors
# action: Nur bei Aktoren: Aktion, die ausgefuehrt werden soll, An, Aus etc...
#
# Rueckgabewert:
# array 
# arr[0]: index desObjektes in der CommandList
# arr[1]: True: kann gesendet werden   False: Wurde zuvor bereits gesendet
#---------------------------------------------------------------------------------------------------------------------------------------
def Check_LORA_ACTOR_REQ(radioId, channelId, action):
  
  global CommandList
  status = 0
  idx=0
  rv = True

  for c in CommandList:
    if (c.devId == radioId):
      if (c.cmdId == LORA_ACTOR_REQ):
        if (c.channelId == channelId):
          if ( c.action == action):
            if ( (time.time() - c.timestamp) > SENDINTERVAL ):
              CommandList[idx].timestamp = time.time()
              status=1
              rv=True
            else:
              status=1
              rv = False
            break
          elif ( c.action != action):
            status=1 
            rv = True 
            break
    idx=idx+1
  
  if ( status == 0 ):
    CommandList.append(Command(radioId, LORA_ACTOR_REQ, channelId, action))
    CommandList[idx].timestamp = time.time()
  
  return [idx,rv] 


#---------------------------------------------------------------------------------------------------------------------------------------
# bool Send_LORA_ACTOR_REQ			(uint32_t radioId, uint16_t id, uint8_t action);
#
# Parameter:
# radioId: ID des Lora Nodes, fuer den die Daten gedacht sind
# channelId: Die ID des angesprochenen Sensors oder Aktors
# action: Nur bei Aktoren: Aktion, die ausgefuehrt werden soll, An, Aus etc...
#
# typedef struct _tagACTOR_REQ
# {
#   uint16_t			id; 	
#   uint8_t			action; 	                            					                                                       
# }ACTOR_REQ;
#
#---------------------------------------------------------------------------------------------------------------------------------------
def Send_LORA_ACTOR_REQ(radioId, channelId, action):
  
  global CommandList

  #Pruefe, wann der Request zuletzt per Lora verschickt wurde. Wenn
  #seit dem letzten Schicken zu wenig Zeit vergangen ist, wird 
  #nicht gesendet sondern direkt 'ACK' zurueckgegeben
  #check: [idx,send,val]
  check = Check_LORA_ACTOR_REQ(radioId, channelId, action)
  if ( check[1] == False ):
    return 'ACK'

  data = [(radioId&0xFF),((radioId>>8)&0xFF),((radioId>>16)&0xFF),((radioId>>24)&0xFF),(LORA_ACTOR_REQ),(channelId>>0),(channelId>>8),(action)]
  rv = WriteI2cBlockData(I2C_REGADDR_SENDBUFFER, data)
  if ( rv == False ):
    return 'NAK' 
  else:
    CommandList[check[0]].action = action 

  await = 1
  rv = WaitForResponse(await)
  if ( rv == True ):
    #0x63:
    #I2C Adresse
    #erste 1: 
    #Anzahl der angeforderten Response Bytes - dieser Wert entspricht dem auszulesenden I2C Register, wird hier aber genutzt, 
    #um dem Lora Gateway mitzuteilen, wieviele Bytes es ausgeben soll. I2C Registeradressen < 127 werden vom Gateway als Laengeninformation 
    #interpretiert.
    #zweite 1:
    #Anzahl der angeforderten Bytes - diese Zahl ist fuer den I2C Treiber
    resp = ReadI2cByteData(1)
    if ( resp == None ):
      return 'NAK'
    elif ( resp == 0 ):
      return 'ACK'
    else:
      return 'NAK'

  else:
    return 'NAK'


#---------------------------------------------------------------------------------------------------------------------------------------
# Check_LORA_SENSOR_REQ
#
# Um zu vermeiden, dass unnoetig Daten per Funk gesendet werden, prueft 
# diese Funktion, ob genau der gleiche Request zuvor bereits abgeschickt wurde.
# Wenn ja, wird nicht gesendet und es wird der zuletzt empfangene Sensorwert zurueckgegeben.
#
# Parameter:
# radioId: ID des Lora Nodes, fuer den die Daten gedacht sind
# channelId: Die ID des angesprochenen Sensors oder Aktors
# 
# Rueckgabewert:
# Array 
# arr[0]: index des Objektes in der CommandList
# arr[1]: True: kann gesendet werden   False: Wurde zuvor bereits gesendet
# arr[2]: der zuletzt empfangene Sensorwert
#---------------------------------------------------------------------------------------------------------------------------------------
def Check_LORA_SENSOR_REQ(radioId, channelId):

  global CommandList
  status = 0
  idx=0
  send = True
  val = 0

  for c in CommandList:
    if (c.devId == radioId):
      if (c.cmdId == LORA_SENSOR_REQ):
        if (c.channelId == channelId):
          if ( (time.time()-c.timestamp) > SENDINTERVAL ):
            CommandList[idx].timestamp = time.time()
            send = True
          else:
            val = c.value
            send = False

          status=1          
          break;

        else:
          send = True

    idx=idx+1
  
  if ( status == 0 ):
    CommandList.append(Command(radioId, LORA_SENSOR_REQ, channelId, 0))
    CommandList[idx].timestamp = time.time()
    
  return [idx,send,val] 


#---------------------------------------------------------------------------------------------------------------------------------------
# Send_LORA_SENSOR_REQ
#
# Parameter:
# radioId: ID des Lora Nodes, fuer den die Daten gedacht sind
# startId: ID des ersten Sensors, der ausgelesen werden soll
# nSensors: Anzahl der Sensoren, die beginnend ab startId gelesen werden sollen
# 
# typedef struct _tagSENSOR_ELEM
# {
#   int8_t        id;
#  int16_t       value;
#}SENSOR_ELEM;
#
#typedef struct _tagSENSOR_RESP
#{
#	uint8_t				nSensors;
#  SENSOR_ELEM   sensor[6];      //1..6 Sensorwerte					                                                       
#}SENSOR_RESP;
#
#---------------------------------------------------------------------------------------------------------------------------------------
def Send_LORA_SENSOR_REQ(radioId, startId, nSensors):
  
  global CommandList

  #Pruefe, wann der Request zuletzt per Lora verschickt wurde. Wenn
  #seit dem letzten Schicken zu wenig Zeit vergangen ist, wird der
  #zuletzt ermittelte, gespeicherte Wert zurueckgegeben
  #check: [idx,send,val]
  check = Check_LORA_SENSOR_REQ(radioId, startId)
  if ( check[1] == False ):
    rv = CommandList[check[0]].value

  else:
    #Wert in der Liste erstmal auf ungueltig setzen
    CommandList[check[0]].value = int(0xFFFF)
    data = [(radioId&0xFF),((radioId>>8)&0xFF),((radioId>>16)&0xFF),((radioId>>24)&0xFF),(LORA_SENSOR_REQ),(startId),(nSensors)]
    rv = WriteI2cBlockData(I2C_REGADDR_SENDBUFFER, data)
    if ( rv == False ):
      return 'NAK'  

    await = 1 + (nSensors*3)
    rv = WaitForResponse(await)
    if ( rv == True ):
      resp = ReadI2cBlockData(await, await)
      if ( resp != False ):
        rv = resp[3] << 8
        rv |= resp[2]
        CommandList[check[0]].value = int(rv)
      else:
        rv = 0xFFFF
    else:
      rv = 0xFFFF

  if ( rv == 0xFFFF ):
    return 'NAK'
  else:
    return str(rv)


#---------------------------------------------------------------------------------------------------------------------------------------
# handle_Request
#--------------------------------------------------------------------------------------------------------------------------------------- 
def handle_Request(data):
  
  global CommandList
  
  rv = 'NAK'

  #Falls der Request ungueltige Daten enthaelt, wird NAK
  #zurueckgegeben
  i2cCmd = ConvertAndCheckRequest(data)
  if ( i2cCmd[0] == False ):
    return rv

  radioId   = i2cCmd[1]
  channelId = i2cCmd[3]
  action    = i2cCmd[4]

  if ( i2cCmd[2] == LORA_ACTOR_REQ ):   
    rv = Send_LORA_ACTOR_REQ(radioId, channelId, action)
  
  elif ( i2cCmd[2] == LORA_SENSOR_REQ ): 
    rv = Send_LORA_SENSOR_REQ(radioId, channelId, 1)    
  
  else:
    #aktuell noch nicht unterstuetzt
    print 'handle_Request: Request nicht unterstuetzt'
    rv = 'NAK'

  return rv


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
    #print 'Resp: ',resp
  except:
    resp = 'NAK'
  
  resp += "\n"
  serversock.sendto(resp, sender_addr)
