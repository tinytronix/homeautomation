#include <avr/io.h>
#include <util/delay.h>
#include "mcp23017.h"
#include "board.h"

#define WATCHDOG_STATE_RPI_TOGGLE_OK		1
#define WATCHDOG_STATE_RPI_TOGGLE_ERR		2
#define WATCHDOG_STATE_RPI_TOGGLE_WAITERR	3

#define WATCHDOG_TOGGLE_TIMEOUT				40	//ca. 4s bei 100ms Zeitscheibe

static char wtdState;
static unsigned long wtdTimer1;
static unsigned long wtdTimer2;
static char wtdPinLast;

//***************************************************************************************
// functionname  :	Watchdog_Init
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
void Watchdog_Init(void)
{
#if (BOARD_REVISION == REV_V0)
	//no reset output available
	DDRB &= ~(1 << PB1);	//PB1 input for Raspberry watchdog signal
#elif (BOARD_REVISION == REV_V1)
	DDRB |= (1 << PB1);  	//PB1 output for Raspberry Reset
	DDRB &= ~(1 << PB5);	//PB5 input for ADC0 sampling Raspberry watchdog signal
	PORTB &= ~(1 << PB1);	//disable reset for Raspberry (Raspberry can start)
#else
	board revision not defined
#endif

	DDRB |= (1 << PB3);		//PB3 output for signalling I2C state to Raspberry
	DDRB |= (1 << PB4);		//PB4 output for enabling/disabling Raspberry I2C

	//init watchdog statemachine
	wtdState = WATCHDOG_STATE_RPI_TOGGLE_ERR;

	//init watchdog timers
	wtdTimer1 = 0;	//watchdog toggle timeout
	wtdTimer2 = 0;	//wait time between signalling and disabling I2C for Raspberry

	//initially Raspberry I2C is disabled
	PORTB |= (1 << PB3); 	//signal to Raspberry I2C disabled
	PORTB &= ~(1 << PB4); 	//Raspberry I2C is disabled in hardware

#ifdef __AVR_ATtiny45__
	#if (BOARD_REVISION == REV_V1)
		ADCSRA |= ((1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0));   //16Mhz/128 = 125Khz the ADC reference clock
		ADMUX |= (0<<REFS0);                			//Voltage reference VCC
		ADMUX &= 0xF0;									//use PB5 ADC0
		ADCSRA |= (1<<ADEN);                			//Turn on ADC
		ADCSRA |= (1<<ADSC);                			//Do an initial conversion because this one is the slowest and to ensure that everything is up and running
	#endif
#endif

#if (BOARD_REVISION == REV_V0)
	if ( PINB & (1 << PB1) )
	{
		wtdPinLast = 1;
	}
	else
	{
		wtdPinLast = 0;
	}
#elif  (BOARD_REVISION == REV_V1)
	#ifdef __AVR_ATtiny45__
		ADCSRA |= (1 << ADSC);         // start ADC measurement
		while (ADCSRA & (1 << ADSC) ); // wait till conversion complete

		if(ADCW > 900)
			wtdPinLast = 1;
		else
			wtdPinLast = 0;
	#endif
#else
	board revision not defined
#endif

	mcp23017_Init();

	mcp23017_SetOutput(MCP23017_GPA6, MCP23017_GPXN_ON);
}


//***************************************************************************************
// functionname  :	IsWatchdogServed
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
char IsWatchdogServed(void)
{
	char wtdPin;
	char rv = 1;

	if ( wtdTimer1 > 0 )
		wtdTimer1--;

#if (BOARD_REVISION == REV_V0)
	if ( PINB & (1 << PB1) )
	{
		wtdPin = 1;
	}
	else
	{
		wtdPin = 0;
	}
#elif  (BOARD_REVISION == REV_V1)
	#ifdef __AVR_ATtiny45__
		ADCSRA |= (1 << ADSC);         // start ADC measurement
		while (ADCSRA & (1 << ADSC) ); // wait till conversion complete

		if(ADCW > 900)
			wtdPin = 1;
		else
			wtdPin = 0;
	#endif
#else
	board revision not defined
#endif
	if ( wtdPin != wtdPinLast )
	{
		wtdTimer1 = WATCHDOG_TOGGLE_TIMEOUT;
		wtdPinLast = wtdPin;
	}

	if ( wtdTimer1 == 0 )
	{
		rv = 0;
	}

	return rv;
}


//***************************************************************************************
// functionname  :	Watchdog_Main
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
void Watchdog_Main(void)
{
	switch ( wtdState )
	{
		case WATCHDOG_STATE_RPI_TOGGLE_ERR:
			#if(BOARD_REVISION == REV_V1)
				PORTB &= ~(1 << PB1); 	//no reset for Raspberry
			#endif
			PORTB |= (1 << PB3); 	//signal to Raspberry I2C disabled
			PORTB &= ~(1 << PB4); 	//Raspberry I2C is disabled in hardware
			if ( 1 == IsWatchdogServed() )
			{
				mcp23017_Init();
				mcp23017_SetOutput(MCP23017_GPA6, MCP23017_GPXN_OFF);
				wtdState = WATCHDOG_STATE_RPI_TOGGLE_OK;
			}
			break;

		case WATCHDOG_STATE_RPI_TOGGLE_WAITERR:
			#if (BOARD_REVISION == REV_V1)
				PORTB &= ~(1 << PB1); 	//no reset for Raspberry
			#endif
			PORTB |= (1 << PB3); 	//signal to Raspberry I2C disabled
			if ( 1 == IsWatchdogServed() )
			{
				wtdState = WATCHDOG_STATE_RPI_TOGGLE_OK;
			}
			else if ( wtdTimer2 > 0 )
			{
				wtdTimer2--;
			}
			else
			{
			}

			if ( wtdTimer2 == 0 )
			{
				PORTB &= ~(1 << PB4); 	//Raspberry I2C is disabled in hardware
				_delay_ms(10);
				mcp23017_Init();
				mcp23017_SetOutput(MCP23017_GPA6, MCP23017_GPXN_ON);
				#if (BOARD_REVISION == REV_V1)
					//reset Raspberry for 500ms
					PORTB |= (1 << PB1);
					_delay_ms(500);
					PORTB &= ~(1 << PB1);
				#endif
				wtdState = WATCHDOG_STATE_RPI_TOGGLE_ERR;
			}
			break;

		case WATCHDOG_STATE_RPI_TOGGLE_OK:
			#if (BOARD_REVISION == REV_V1)
				PORTB &= ~(1 << PB1); 	//no reset for Raspberry
			#endif
			PORTB &= ~(1 << PB3); 	//signal to Raspberry I2C enabled
			PORTB |= (1 << PB4); 	//Raspberry I2C is enabled in hardware
			if ( 0 == IsWatchdogServed() )
			{
				wtdState = WATCHDOG_STATE_RPI_TOGGLE_WAITERR;
				wtdTimer2 = 40;
			}
			break;

		default:
			break;
	}
}
