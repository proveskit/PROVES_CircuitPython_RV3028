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

@pytest.fixture
def rtc():
    i2c_bus = MockI2C()
    rtc = RV3028(i2c_bus)
    return rtc

# Test functions
def test_set_and_get_time(rtc):
    rtc.set_time(23, 59, 58)
    hours, minutes, seconds = rtc.get_time()
    assert hours == 23
    assert minutes == 59
    assert seconds == 58

def test_set_and_get_date(rtc):
    rtc.set_date(21, 12, 31, 5)  # Year, month, date, weekday
    year, month, date, weekday = rtc.get_date()
    assert year == 21
    assert month == 12
    assert date == 31
    assert weekday == 5

def test_set_alarm(rtc):
    rtc.set_alarm(minute=30, hour=14, weekday=3)
    alarm_minutes = rtc._read_register(Reg.ALARM_MINUTES)[0]
    alarm_hours = rtc._read_register(Reg.ALARM_HOURS)[0]
    alarm_weekday = rtc._read_register(Reg.ALARM_WEEKDAY)[0]
    assert (alarm_minutes & ~Alarm.DISABLE) == rtc._int_to_bcd(30)
    assert (alarm_hours & ~Alarm.DISABLE) == rtc._int_to_bcd(14)
    assert (alarm_weekday & ~Alarm.DISABLE) == rtc._int_to_bcd(3)

def test_check_alarm(rtc):
    rtc._set_flag(Reg.STATUS, Status.ALARM, Flag.SET)
    assert rtc.check_alarm() == True
    status = rtc._read_register(Reg.STATUS)[0]
    assert not (status & Status.ALARM)

def test_enable_trickle_charger(rtc):
    rtc.enable_trickle_charger(resistance=9000)
    backup_reg = rtc._read_register(Reg.EEPROM_BACKUP)[0]
    assert backup_reg & EEPROMBackup.TRICKLE_CHARGE_ENABLE
    res_setting = backup_reg & EEPROMBackup.TRICKLE_CHARGE_RES
    assert res_setting == Resistance.RES_9000

def test_disable_trickle_charger(rtc):
    rtc.disable_trickle_charger()
    backup_reg = rtc._read_register(Reg.EEPROM_BACKUP)[0]
    assert not (backup_reg & EEPROMBackup.TRICKLE_CHARGE_ENABLE)

def test_configure_evi(rtc):
    rtc.configure_evi(enable=True)
    control2 = rtc._read_register(Reg.CONTROL2)[0]
    event_control = rtc._read_register(Reg.EVENT_CONTROL)[0]
    assert control2 & Control2.TIMESTAMP_ENABLE
    assert control2 & Control2.EVENT_INT_ENABLE
    assert event_control & EventControl.EVENT_HIGH_LOW_SELECT

def test_get_event_timestamp(rtc):
    timestamp = [
        rtc._int_to_bcd(0),   # count
        rtc._int_to_bcd(10),  # seconds
        rtc._int_to_bcd(20),  # minutes
        rtc._int_to_bcd(12),  # hours
        rtc._int_to_bcd(25),  # date
        rtc._int_to_bcd(9),   # month
        rtc._int_to_bcd(21)   # year
    ]
    rtc._write_register(Reg.TIMESTAMP_COUNT, bytes(timestamp))
    ts = rtc.get_event_timestamp()
    assert ts == (21, 9, 25, 12, 20, 10, 0)

def test_clear_event_flag(rtc):
    rtc._set_flag(Reg.STATUS, Status.EVENT, Flag.SET)
    rtc.clear_event_flag()
    status = rtc._read_register(Reg.STATUS)[0]
    assert not (status & Status.EVENT)

def test_is_event_flag_set(rtc):
    rtc._set_flag(Reg.STATUS, Status.EVENT, Flag.SET)
    assert rtc.is_event_flag_set() == True
    rtc.clear_event_flag()
    assert rtc.is_event_flag_set() == False

def test_configure_backup_switchover(rtc):
    rtc.configure_backup_switchover(mode="direct", interrupt=True)
    backup_reg = rtc._read_register(Reg.EEPROM_BACKUP)[0]
    backup_mode = rtc._get_flag(Reg.EEPROM_BACKUP, EEPROMBackup.BACKUP_SWITCHOVER, size=BSM.SIZE)
    assert backup_mode == BSM.DIRECT
    assert backup_reg & EEPROMBackup.BACKUP_SWITCHOVER_INT_ENABLE

def test_backup_switchover_flag(rtc):
    rtc._set_flag(Reg.STATUS, Status.BACKUP_SWITCH, Flag.SET)
    assert rtc.is_backup_switchover_occurred() == True
    rtc.clear_backup_switchover_flag()
    assert rtc.is_backup_switchover_occurred() == False