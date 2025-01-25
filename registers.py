from enum import IntEnum

class Reg(IntEnum):
    SECONDS = 0x00
    MINUTES = 0x01
    HOURS = 0x02
    WEEKDAY = 0x03
    DATE = 0x04
    MONTH = 0x05
    YEAR = 0x06
    ALARM_MINUTES = 0x07
    ALARM_HOURS = 0x08
    ALARM_WEEKDAY = ALARM_DATE = 0x09 # Depends on which one is enabled
    TIMER0 = 0x0A
    TIMER1 = 0x0B
    TIMER_STATUS0 = 0x0C     # readonly
    TIMER_STATUS1 = 0x0D     # readonly
    STATUS = 0x0E
    CONTROL1 = 0x0F
    CONTROL2 = 0x10
    GP_BITS = 0x11
    CLOCK_INT_MASK = 0x12
    EVENT_CONTROL = 0x13
    TIMESTAMP_COUNT = 0x14   # readonly
    TIMESTAMP_SECONDS = 0x15 # readonly
    TIMESTAMP_MINUTES = 0x16 # readonly
    TIMESTAMP_HOURS = 0x17   # readonly
    TIMESTAMP_DATE = 0x18    # readonly
    TIMESTAMP_MONTH = 0x19   # readonly
    TIMESTAMP_YEAR = 0x1A    # readonly
    UNIX_TIME0 = 0x1B
    UNIX_TIME1 = 0x1C
    UNIX_TIME2 = 0x1D
    UNIX_TIME3 = 0x1E
    RAM1 = 0x1F
    RAM2 = 0x20
    EEDATA = 0x26
    EECOMMAND = 0x27
    ID = 0x28               # readonly
    EEPROM_CLKOUT = 0x35
    EEPROM_OFFSET = 0x36
    EEPROM_BACKUP = 0x37



        

    



    

    