This is an interface pcb board which distributes power and I2C between all modules.

The I2C Bus Interface board can be used for Typ 2C, Typ 4C and Typ 6C
DIN rail housings by cutting as required.

Each DIN rail module needs to implement a module bus.

The module bus starting point is either the Controller module (Raspberry) or the LoRa Bridge,
because these modules initially provide the power and act as I2C master.


