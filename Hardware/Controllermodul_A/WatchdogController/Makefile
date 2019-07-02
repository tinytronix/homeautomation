# Makefile for this AVR project

# make code       Compiles the source code
# make fuses      Program fuses
# make program    Program flash and eeprom

# make list       Create generated code listing
# make clean      Delete all generated files

# Programmer hardware settings for avrdude
# AVRDUDE_HW = -c avr910 -P /dev/ttyUSB0 -b 115200
# AVRDUDE_HW = -c arduino -P COM3 -b 57600
AVRDUDE_HW = -c avrispmkII

# Name of the program without extension
#PRG = ctrl_atiny2313
PRG = ctrl_atiny45

# Microcontroller type and clock frequency
#MCU = attiny2313
MCU = attiny45
F_CPU = 1000000
#F_CPU = 1200000

# Optional fuse settings, for example
# LFUSE = 0x64
# HFUSE = 0xDF
# EFUSE = 0xFF

# Objects to compile (*.c and *.cpp files, but with suffix .o)
OBJ = main.o USI_TWI_Master.o mcp23017.o watchdog.o


###################################################################
# You possibly do not need to change settings below this marker
###################################################################

# Binaries to be used
# You may add the path to them if they are not in the PATH variable.
CC       = avr-gcc
OBJCOPY  = avr-objcopy
OBJDUMP  = avr-objdump
AVRDUDE  = avrdude
AVR_SIZE = avr-size

# Do we need to write Eeprom? (yes/no)
EEPROM = no

# Extra Libraries
#LIBS = -L path/to/libraries -llibrary1 -llibrary2

# Extra Includes
#INCLUDES = -I path/to/include_files

# Compiler flags for C and C++
FLAGS = -Wall -O1 -fshort-enums -mmcu=$(MCU) -DF_CPU=$(F_CPU)

# Additional compiler flags for C only
CFLAGS = -std=c99

# Additional compiler flags for C++ only
CPPFLAGS = -fno-exceptions

# Linker flags
LDFLAGS = -lm

# Enable creation of a map file
# LDFLAGS += -Wl,-Map,$(PRG).map

# Enable floating-point support in printf
#LDFLAGS += -Wl,-u,vfprintf -lprintf_flt

# Enable floating-point support in scanf
#LDFLAGS += -Wl,-u,vscanf -lscanf_flt

# Enable automatic removal of unused code
FLAGS += -ffunction-sections -fdata-sections
LDFLAGS += -Wl,--gc-sections

# Collect fuse operations for avrdude
ifdef FUSE
  FUSES += -U fuse:w:$(FUSE):m
endif
ifdef LFUSE
  FUSES += -U lfuse:w:$(LFUSE):m
endif
ifdef HFUSE
  FUSES += -U hfuse:w:$(HFUSE):m
endif
ifdef EFUSE
  FUSES += -U efuse:w:$(EFUSE):m
endif
ifdef FUSE0
  FUSES += -U fuse0:w:$(FUSE0):m
endif
ifdef FUSE1
  FUSES += -U fuse1:w:$(FUSE1):m
endif
ifdef FUSE2
  FUSES += -U fuse2:w:$(FUSE2):m
endif
ifdef FUSE3
  FUSES += -U fuse3:w:$(FUSE3):m
endif
ifdef FUSE4
  FUSES += -U fuse4:w:$(FUSE4):m
endif
ifdef FUSE5
  FUSES += -U fuse5:w:$(FUSE5):m
endif
ifdef FUSE6
  FUSES += -U fuse6:w:$(FUSE6):m
endif
ifdef FUSE7
  FUSES += -U fuse7:w:$(FUSE7):m
endif

# Workaround: avrdude does not support attiny13a
ifeq ($(MCU),attiny13a)
  AVRDUDE_MCU = attiny13
else
  AVRDUDE_MCU = $(MCU)
endif

# Default sections
ifeq ($(EEPROM),yes)
all: code eeprom
else
all: code
endif

# Program code
code: $(PRG).hex

# Eeprom content
eeprom: $(PRG)_eeprom.hex

# Generated code listing
list: $(PRG).lst

# Remove all generated files
clean:
	rm -f $(OBJ) $(PRG).hex $(PRG).elf $(PRG).lst $(PRG).map $(PRG)_eeprom.hex

# Program flash memory with or without eeprom
flash: 
	$(AVRDUDE) -p $(AVRDUDE_MCU) $(AVRDUDE_HW) -U flash:w:$(PRG).hex:i


# Program fuses
#fuses:
#	$(AVRDUDE) -p $(AVRDUDE_MCU) $(AVRDUDE_HW) $(FUSES)

%.o : %.c
	$(CC) -c $(FLAGS) $(CFLAGS) $(INCLUDES) $(LIBS) -o $@ $< 

%.o : %.cpp
	$(CC) -c $(FLAGS) $(CPPFLAGS) $(INCLUDES) $(LIBS) -o $@ $< 

$(PRG).elf: $(OBJ)
	$(CC) $(FLAGS) $(LDFLAGS) -o $@ $^
	$(AVR_SIZE) $(PRG).elf

$(PRG).lst: $(PRG).elf
	$(OBJDUMP) -h -S $< > $@

$(PRG).hex: $(PRG).elf
	$(OBJCOPY) -j .text -j .data -O ihex $< $@

$(PRG)_eeprom.hex: $(PRG).elf
	$(OBJCOPY) -j .eeprom --change-section-lma .eeprom=0 -O ihex $< $@ 

