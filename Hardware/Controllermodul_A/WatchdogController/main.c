
#include <avr/interrupt.h>
#include <util/delay.h>
#include "USI_TWI_Master.h"
#include "mcp23017.h"
#include "watchdog.h"
#include "board.h"

#ifdef __AVR_ATtiny2313__
#define BAUD 9600
#define MYUBBR (((1000000) / (BAUD * 16L)) - 1)
#define TRC(x) trace(x)
#else
#define TRC(x) void
#endif



#ifdef __AVR_ATtiny2313__
//***************************************************************************************
// functionname  :	initUart
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 :	Transmits 0-teriminated strings syncron
//
// description   :
//***************************************************************************************
void initUart()
{

	UCSRA |= (1 << U2X);
	UCSRB = (1 << RXEN) | (1 << TXEN) | (1 << RXCIE);// set frame format
	UCSRC = (1 << USBS) | (3 << UCSZ0); // asynchron 8n1

	UBRRH = 0;
	UBRRL = 12;
}


//***************************************************************************************
// functionname  :	trace
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 :	Transmits 0-teriminated strings syncron
//
// description   :
//***************************************************************************************
void trace(char* str)
{
	char *p = str;
	while ( *p != '\0' )
	{
		while (!(UCSRA & (1<<UDRE))
				);
		UDR = *p++;
	}
}
#endif


//***************************************************************************************
// functionname  :	Raspi_I2C_DefaultOn
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 : for debugging
//
// description   :
//***************************************************************************************
void Debug_Raspi_I2C_On(void)
{
	DDRB |= (1 << PB4);
	PORTB |= (1 << PB4);
}


//***************************************************************************************
// functionname  :	Debug_ATTiny_I2C_On
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 : for debugging
//
// description   :
//***************************************************************************************
void Debug_ATTiny_I2C_On(void)
{
	DDRB |= (1 << PB4);
	PORTB &= ~(1 << PB4);
}


//***************************************************************************************
// functionname  :	Debug_Send_I2C
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 : for debugging
//
// description   :
//***************************************************************************************
void Debug_Send_I2C(unsigned char c)
{
	unsigned char i[3];

	i[0] = (0x20 << 1) | TWI_WRITE_CMD; //i2c address
	i[1] = 0x14;
	i[2] = c;

	USI_TWI_Start_Transceiver_With_Data_Stop(i, (unsigned char)3, TRUE);
}


//***************************************************************************************
// functionname  :	main
//
// in parameters :
//
// out parameters:
//
// returnvalues  :
//
// short		 :
//
// description   :
//***************************************************************************************
int main(void) 
{
#ifdef __AVR_ATtiny2313__
	initUart();
	TRC("Testprogramm start\n");
#endif

	USI_TWI_Master_Initialise();

#if ( DEBUG_MODE == DBG_ATTINY_I2C )
	DDRB |= (1 << PB4);
	PORTB &= ~(1 << PB4);
	mcp23017_Init();
#endif

#if ( DEBUG_MODE == NORMAL_OPERATION )
	Watchdog_Init();

#elif ( DEBUG_MODE == DBG_ATTINY_I2C )
	unsigned char i[3];
#else
#endif

    while(1)
    {
#if ( DEBUG_MODE == NORMAL_OPERATION )
    	_delay_ms(100);
    	Watchdog_Main();

#elif ( DEBUG_MODE == DBG_ATTINY_LED )
		_delay_ms(2000);
		DDRB |= (1 << PB3);
		if ( !(PINB & (1 << PB3)) )
		{
			PORTB |= (1 << PB3);
		}
		else
		{
			PORTB &= ~(1 << PB3);
		}
#elif ( DEBUG_MODE == DBG_ATTINY_I2C )
    	DDRB |= (1 << PB4);
    	PORTB &= ~(1 << PB4);
    	i[0] = (0x20 << 1) | TWI_WRITE_CMD; //i2c address
		i[1] = 0x14;
		i[2] = 0x40;
		USI_TWI_Start_Transceiver_With_Data_Stop(i, (unsigned char)3, TRUE);
		_delay_ms(1000);
		i[0] = (0x20 << 1) | TWI_WRITE_CMD; //i2c address
		i[1] = 0x14;
		i[2] = 0x00;
		USI_TWI_Start_Transceiver_With_Data_Stop(i, (unsigned char)3, TRUE);
		_delay_ms(1000);
#elif ( DEBUG_MODE == RASPI_ON )
		DDRB |= (1 << PB4);
		PORTB |= (1 << PB4);
	#if (BOARD_REVISION == REV_V1)
		DDRB |= (1 << PB1);  	//PB1 output for Raspberry Reset
		PORTB &= ~(1 << PB1);	//disable reset for Raspberry (Raspberry can start)
	#endif
#else
		debug mode not defined
#endif
    }
}

