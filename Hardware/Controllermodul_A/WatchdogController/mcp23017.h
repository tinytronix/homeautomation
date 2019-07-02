
#define MCP23017_GPA0		0x00
#define MCP23017_GPA1		0x01
#define MCP23017_GPA2		0x02
#define MCP23017_GPA3		0x03
#define MCP23017_GPA4		0x04
#define MCP23017_GPA5		0x05
#define MCP23017_GPA6		0x06
#define MCP23017_GPA7		0x07
#define MCP23017_GPB0		0x10
#define MCP23017_GPB1		0x11
#define MCP23017_GPB2		0x12
#define MCP23017_GPB3		0x13
#define MCP23017_GPB4		0x14
#define MCP23017_GPB5		0x15
#define MCP23017_GPB6		0x16
#define MCP23017_GPB7		0x17

#define MCP23017_GPXN_ON   	0x01
#define MCP23017_GPXN_OFF  	0x00

#define MCP23017_OK			0x00
#define MCP23017_ERR		0x01


void mcp23017_Init(void);
unsigned char mcp23017_SetOutput(unsigned char gpxn, unsigned char state);
