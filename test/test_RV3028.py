import pytest
import sys, os

# Override the I2CDevice class with a mock
sys.modules['adafruit_bus_device.i2c_device'] = sys.modules[__name__]

from types import ModuleType
from mocks.i2cMock import MockI2CDevice, MockI2C

# Fake adafruit_bus_device.i2c_device module
adafruit_bus_device = ModuleType('adafruit_bus_device')
adafruit_bus_device.i2c_device = ModuleType('adafruit_bus_device.i2c_device')
adafruit_bus_device.i2c_device.I2CDevice = MockI2CDevice
sys.modules['adafruit_bus_device'] = adafruit_bus_device

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rv3028 import RV3028
from registers import *

def test_set_time():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.set_time(12, 34, 56)
    assert i2c.registers[Reg.SECONDS] == ((56 // 10) << 4) | (56 % 10)
    assert i2c.registers[Reg.MINUTES] == ((34 // 10) << 4) | (34 % 10)
    assert i2c.registers[Reg.HOURS] == ((12 // 10) << 4) | (12 % 10)

def test_get_time():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    i2c.registers[Reg.SECONDS] = ((56 // 10) << 4) | (56 % 10)
    i2c.registers[Reg.MINUTES] = ((34 // 10) << 4) | (34 % 10)
    i2c.registers[Reg.HOURS] = ((12 // 10) << 4) | (12 % 10)

    hours, minutes, seconds = rtc.get_time()
    assert hours == 12
    assert minutes == 34
    assert seconds == 56

def test_set_date():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.set_date(21, 9, 30, 4)  # Year 21, September 30, Thursday
    assert i2c.registers[Reg.YEAR] == ((21 // 10) << 4) | (21 % 10)
    assert i2c.registers[Reg.MONTH] == ((9 // 10) << 4) | (9 % 10)
    assert i2c.registers[Reg.DATE] == ((30 // 10) << 4) | (30 % 10)
    assert i2c.registers[Reg.WEEKDAY] == ((4 // 10) << 4) | (4 % 10)

def test_get_date():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Set the registers directly
    i2c.registers[Reg.YEAR] = ((21 // 10) << 4) | (21 % 10)
    i2c.registers[Reg.MONTH] = ((9 // 10) << 4) | (9 % 10)
    i2c.registers[Reg.DATE] = ((30 // 10) << 4) | (30 % 10)
    i2c.registers[Reg.WEEKDAY] = ((4 // 10) << 4) | (4 % 10)

    year, month, date, weekday = rtc.get_date()
    assert year == 21
    assert month == 9
    assert date == 30
    assert weekday == 4

def test_set_alarm():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.set_alarm(minute=45, hour=6, weekday=1)
    assert i2c.registers[Reg.ALARM_MINUTES] == ((45 // 10) << 4) | (45 % 10)
    assert i2c.registers[Reg.ALARM_HOURS] == ((6 // 10) << 4) | (6 % 10)
    assert i2c.registers[Reg.ALARM_WEEKDAY] == ((1 // 10) << 4) | (1 % 10)

def test_set_alarm_invalid_minute():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    with pytest.raises(ValueError):
        rtc.set_alarm(minute=60)

def test_set_alarm_invalid_hour():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    with pytest.raises(ValueError):
        rtc.set_alarm(hour=24)

def test_set_alarm_invalid_weekday():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    with pytest.raises(ValueError):
        rtc.set_alarm(weekday=7)

def test_check_alarm():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Set the alarm flag
    i2c.registers[Reg.STATUS] |= 0x04

    result = rtc.check_alarm()
    assert result == True
    # Alarm flag should be cleared after check
    assert (i2c.registers[Reg.STATUS] & 0x04) == 0

def test_check_alarm():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Set the alarm flag
    i2c.registers[Reg.STATUS] |= 0x04

    result = rtc.check_alarm()
    assert result == True
    # Alarm flag should be cleared after check
    assert (i2c.registers[Reg.STATUS] & 0x04) == 0

def test_enable_trickle_charger_valid():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.enable_trickle_charger(resistance=3000)
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert backup_reg & 0x20  # TCE bit is set (bit 5)
    assert (backup_reg & 0x03) == 0x00  # TCR bits for 3000 ohms

    rtc.enable_trickle_charger(resistance=5000)
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert (backup_reg & 0x03) == 0x01  # TCR bits for 5000 ohms

    rtc.enable_trickle_charger(resistance=9000)
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert (backup_reg & 0x03) == 0x02  # TCR bits for 9000 ohms

    rtc.enable_trickle_charger(resistance=15000)
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert (backup_reg & 0x03) == 0x03  # TCR bits for 15000 ohms

def test_enable_trickle_charger_invalid():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    with pytest.raises(ValueError):
        rtc.enable_trickle_charger(resistance=2000)

def test_disable_trickle_charger():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # First enable it
    rtc.enable_trickle_charger(resistance=3000)
    # Now disable
    rtc.disable_trickle_charger()
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert (backup_reg & 0x20) == 0  # TCE bit is cleared

def test_configure_evi_enable():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.configure_evi(enable=True)
    event_control = i2c.registers[Reg.EVENT_CONTROL]
    assert event_control == 0x40  # EHL = 1, ET = 00

    control2 = i2c.registers[Reg.CONTROL2]
    assert control2 & 0x80  # TSE bit is set
    assert control2 & 0x04  # EIE bit is set

def test_configure_evi_disable():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.configure_evi(enable=False)
    control2 = i2c.registers[Reg.CONTROL2]
    assert (control2 & 0x80) == 0  # TSE bit is cleared
    assert (control2 & 0x04) == 0  # EIE bit is cleared

def test_get_event_timestamp():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Set the timestamp registers directly
    i2c.registers[Reg.TIMESTAMP_COUNT] = 1
    i2c.registers[Reg.TIMESTAMP_SECONDS] = ((50 // 10) << 4) | (50 % 10)
    i2c.registers[Reg.TIMESTAMP_MINUTES] = ((40 // 10) << 4) | (40 % 10)
    i2c.registers[Reg.TIMESTAMP_HOURS] = ((14 // 10) << 4) | (14 % 10)
    i2c.registers[Reg.TIMESTAMP_DATE] = ((15 // 10) << 4) | (15 % 10)
    i2c.registers[Reg.TIMESTAMP_MONTH] = ((8 // 10) << 4) | (8 % 10)
    i2c.registers[Reg.TIMESTAMP_YEAR] = ((22 // 10) << 4) | (22 % 10)

    timestamp = rtc.get_event_timestamp()
    assert timestamp == (22, 8, 15, 14, 40, 50, 1)

def test_clear_event_flag():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Set the event flag
    i2c.registers[Reg.STATUS] |= 0x02

    rtc.clear_event_flag()
    assert (i2c.registers[Reg.STATUS] & 0x02) == 0  # EVF bit is cleared

def test_is_event_flag_set():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Event flag not set
    assert rtc.is_event_flag_set() == False

    # Set the event flag
    i2c.registers[Reg.STATUS] |= 0x02
    assert rtc.is_event_flag_set() == True

def test_configure_backup_switchover_level():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.configure_backup_switchover(mode="level", interrupt=True)
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert backup_reg & 0x0C == 0x0C  # BSM = 11
    assert backup_reg & 0x40  # BSIE bit is set
    assert backup_reg & 0x10  # FEDE bit is set

def test_configure_backup_switchover_direct():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.configure_backup_switchover(mode="direct", interrupt=False)
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert backup_reg & 0x0C == 0x04  # BSM = 01
    assert (backup_reg & 0x40) == 0  # BSIE bit is cleared
    assert backup_reg & 0x10  # FEDE bit is set

def test_configure_backup_switchover_disabled():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    rtc.configure_backup_switchover(mode="disabled", interrupt=False)
    backup_reg = i2c.registers[Reg.EEPROM_BACKUP]
    assert backup_reg & 0x0C == 0x00  # BSM = 00
    assert (backup_reg & 0x40) == 0  # BSIE bit is cleared
    assert backup_reg & 0x10  # FEDE bit is set

def test_configure_backup_switchover_invalid():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    with pytest.raises(ValueError):
        rtc.configure_backup_switchover(mode="invalid")

def test_is_backup_switchover_occurred():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Switchover not occurred
    assert rtc.is_backup_switchover_occurred() == False

    # Set the BSF bit
    i2c.registers[Reg.STATUS] |= 0x20
    assert rtc.is_backup_switchover_occurred() == True

def test_clear_backup_switchover_flag():
    i2c = MockI2C()
    rtc = RV3028(i2c)

    # Set the BSF bit
    i2c.registers[Reg.STATUS] |= 0x20

    rtc.clear_backup_switchover_flag()
    assert (i2c.registers[Reg.STATUS] & 0x20) == 0  # BSF bit is cleared