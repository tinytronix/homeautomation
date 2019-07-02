#include <avr/io.h>
#include "USI_TWI_Master.h"
#include "mcp23017.h"

//all register definitions apply to default register mapping (IOCON.BANK = 0)
#define MCP23017_IODIRA		0x00
#define MCP23017_IODIRB		0x01
#define MCP23017_OLATA		0x14
#define MCP23017_OLATB		0x15

//other definitions
#define MCP23017_I2C_BUF_SIZE	3
#define MCP23017_I2C_ADDRESS	0x20


//module locale variable declarations
static unsigned char i2c_Buffer[MCP23017_I2C_BUF_SIZE];
static unsigned char portA;
static unsigned char portB;

//***************************************************************************************
// functionname  :	mcp23017_Init
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 :	initializes the MCP23017 to output for all Port pins.
//
// description   :
//***************************************************************************************
void mcp23017_Init(void)
{
	portA = 0;
	portB = 0;

	//set PortA to output direction
	i2c_Buffer[0] = (MCP23017_I2C_ADDRESS << 1) | TWI_WRITE_CMD;
	i2c_Buffer[1] = MCP23017_IODIRA;
	i2c_Buffer[2] = 0x00;
	USI_TWI_Start_Transceiver_With_Data_Stop(i2c_Buffer, (unsigned char)3, TRUE);

	//set PortB to output direction
	i2c_Buffer[0] = (MCP23017_I2C_ADDRESS << 1) | TWI_WRITE_CMD;
	i2c_Buffer[1] = MCP23017_IODIRB;
	i2c_Buffer[2] = 0x00;
	USI_TWI_Start_Transceiver_With_Data_Stop(i2c_Buffer, (unsigned char)3, TRUE);

	//init PortA to default
	portA = 0x00;
	i2c_Buffer[0] = (MCP23017_I2C_ADDRESS << 1) | TWI_WRITE_CMD;
	i2c_Buffer[1] = MCP23017_OLATA;
	i2c_Buffer[2] = 0;
	USI_TWI_Start_Transceiver_With_Data_Stop(i2c_Buffer, (unsigned char)3, TRUE);

	//init PortB to default
	portB = 0x00;
	i2c_Buffer[0] = (MCP23017_I2C_ADDRESS << 1) | TWI_WRITE_CMD;
	i2c_Buffer[1] = MCP23017_OLATB;
	i2c_Buffer[2] = 0;
	USI_TWI_Start_Transceiver_With_Data_Stop(i2c_Buffer, (unsigned char)3, TRUE);
}


//***************************************************************************************
// functionname  :	mcp23017_SetOutput
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 :	sets one of the output pins GPA0...GPB7 on or off
//
// description   :
//***************************************************************************************
unsigned char mcp23017_SetOutput(unsigned char gpxn, unsigned char state)
{
	unsigned char rv = MCP23017_OK;
	unsigned char io = (1 << (gpxn & 0x07));

	if ( (gpxn & 0x10) == 0x00 )
	{
		//PortA
		if ( state == MCP23017_GPXN_ON )
		{
			//set bit
			portA |= io;
		}
		else
		{
			//reset bit
			portA &= ~io;
		}
		i2c_Buffer[0] = (MCP23017_I2C_ADDRESS << 1) | TWI_WRITE_CMD;
		i2c_Buffer[1] = MCP23017_OLATA;
		i2c_Buffer[2] = portA;
		if ( FALSE == USI_TWI_Start_Transceiver_With_Data_Stop(i2c_Buffer, (unsigned char)3, TRUE) )
		{
			rv = MCP23017_ERR;
		}
	}
	else
	{
		//PortB
		if ( state == MCP23017_GPXN_ON )
		{
			//set bit
			portB |= io;
		}
		else
		{
			//reset bit
			portB &= ~io;
		}
		i2c_Buffer[0] = (MCP23017_I2C_ADDRESS << 1) | TWI_WRITE_CMD;
		i2c_Buffer[1] = MCP23017_OLATB;
		i2c_Buffer[2] = portB;
		if ( FALSE == USI_TWI_Start_Transceiver_With_Data_Stop(i2c_Buffer, (unsigned char)3, TRUE) )
		{
			rv = MCP23017_ERR;
		}
	}

	return rv;
}
