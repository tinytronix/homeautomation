#include <LoraGateway.h>
#include "build_defs.h"
#include <Wire.h>

//-------------------------------------------------------------------------------------
//
// Infos fuer die Arduino IDE und fuer das Flashen des Bootloaders
// Board: Arduino Pro or Pro Mini
// Processor: ATMega328P (8MHz, 3,3V)
//
//-------------------------------------------------------------------------------------

//-------------------------------------------------------------------------------------
//
// Defines
//
//-------------------------------------------------------------------------------------
#define PROGRAM_VERSION_STRING          "V1.0.3"

#define TASK_TIME_MS                    25
#define TIME_SECONDS(x)                 ((x) * (1000/TASK_TIME_MS))
#define TIME_MILLISECONDS(x)            ((x) / TASK_TIME_MS)


#define RF_FREQUENCY                    433000000 // Hz  center frequency
#define TX_OUTPUT_POWER                 22        // dBm tx output power
/* Langsame Datenrate
#define LORA_BANDWIDTH                  4         // bandwidth=125khz  0:250kHZ,1:125kHZ,2:62kHZ,3:20kHZ.... look for radio line 392                                                               
#define LORA_SPREADING_FACTOR           7         // spreading factor=11 [SF5..SF12]
#define LORA_CODINGRATE                 4         // [1: 4/5, 2: 4/6, 3: 4/7, 4: 4/8]
*/
#define LORA_BANDWIDTH                  6         // bandwidth=125khz  0:250kHZ,1:125kHZ,2:62kHZ,3:20kHZ.... look for radio line 392                                                               
#define LORA_SPREADING_FACTOR           5         // spreading factor=11 [SF5..SF12]
#define LORA_CODINGRATE                 4         // [1: 4/5,2: 4/6,3: 4/7, 4: 4/8]

#define LORA_PREAMBLE_LENGTH            8         // Same for Tx and Rx
#define LORA_SYMBOL_TIMEOUT             0         // Symbols
#define LORA_FIX_LENGTH_PAYLOAD_ON      false     // variable data payload
#define LORA_IQ_INVERSION_ON            false
#define LORA_PAYLOADLENGTH              0         // 0: variable receive length 
                                                // 1..255 payloadlength

#define  SENSOR_ELEMS                   3

//-------------------------------------------------------------------------------------
//
// globale Typdefinitionen
//
//-------------------------------------------------------------------------------------
typedef struct _tagI2CDATA
{
  uint32_t  radioId;         //LoRa Identifier des Geraetes, welches angesprochen werden soll
  uint8_t   cmdId;           //Lora CommandId
  uint8_t   data[32];        //data for CommandId
}I2CDATA;


//-------------------------------------------------------------------------------------
//
// globale Objekte
//
//-------------------------------------------------------------------------------------
unsigned long           lastWait;               //wenn die Funktion millis überläuft (ca. alle 1193 Stunden), kann die Wartezeit in 
                                                //diesem Zyklus nicht berechnet werden. Dann wird die letzte Wartezeit benutzt. 
                                                
LoraGateway             lora(PD5,               //Port-Pin Output: SPI select
                             PD6,               //Port-Pin Output: Reset 
                             PD7,               //Port-Pin Input:  Busy
                             PB0                //Port-Pin Input:  Interrupt DIO1 
                             );

CIPHERKEY               cipher;


//-------------------------------------------------------------------------------------
//
// setup
//
//-------------------------------------------------------------------------------------
void setup() 
{
  Serial.begin(9600);
  delay(500);
  
  Serial.println("\n");
  Serial.print("LoRa Gateway Version: ");
  Serial.print(PROGRAM_VERSION_STRING);
  Serial.print("  Build Number: ");
  Serial.print(TimestampedVersion);
  Serial.print("  Build date: ");
  Serial.println(__DATE__);

  lora.begin(TASK_TIME_MS,
             SX126X_PACKET_TYPE_LORA,
             RF_FREQUENCY,              //frequency in Hz
             TX_OUTPUT_POWER);          //tx power in dBm

  cipher = {0x00, 0x00, 0x00};    //add own cypher here if encryption is desired
  lora.EncryptDecryptKey(&cipher);
  
  lora.LoRaConfig(LORA_SPREADING_FACTOR, 
                  LORA_BANDWIDTH, 
                  LORA_CODINGRATE, 
                  LORA_PREAMBLE_LENGTH, 
                  LORA_PAYLOADLENGTH, 
                  true,                 //crcOn  
                  false                 //invertIrq
                  );
 
  I2C_Init();
}


//-------------------------------------------------------------------------------------
//
// onLORA_PROPERTY_REQ
//
//-------------------------------------------------------------------------------------
void onLORA_PROPERTY_REQ(uint16_t key, uint16_t value)
{
  if ( key == 1 )
  {
    lora.SetTxPower(value);
  }
}


//-------------------------------------------------------------------------------------
//
// main loop
//
//-------------------------------------------------------------------------------------
void loop() 
{
  I2CDATA data;
  unsigned long ts = millis();

  uint8_t len = I2C_GetData(&data);
  if ( len )
  {
/*    
    Serial.print("RadioID: 0x");
    Serial.println(data.radioId, HEX);
    Serial.print("Cmd: 0x");
    Serial.println(data.cmdId, DEC);
    Serial.print("DataLen: ");
    Serial.println(len, DEC);
*/  
    if ( data.radioId == DEVICE_LORA_GATEWAY )
    { 
      if ( data.cmdId == LORA_PROPERTY_REQ )
      {
        PROPERTY_REQ p;
        memcpy(&p, data.data, len);
        onLORA_PROPERTY_REQ(p.key, p.value);
      }    
    }
    else
    { 
      lora.Send(data.radioId, data.cmdId, data.data, len);
    }
  }
    
  lora.Service();
  WaitUntilNextTaskCycle(ts);
}
