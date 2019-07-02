//controller board revision number
#define REV_V0				0	//31.10.2017
#define REV_V1				1	//xx.12.2017

#define BOARD_REVISION		REV_V1


//debug mode
#define NORMAL_OPERATION	0	//all functions enabled
#define RASPI_ON			1	//raspi always on, raspi i2c on, never reset raspi
#define DBG_ATTINY_I2C		2	//raspi always on but raspi i2c off, attiny blinks on MCP23017 Pin
#define DBG_ATTINY_LED		3

#define DEBUG_MODE			NORMAL_OPERATION
