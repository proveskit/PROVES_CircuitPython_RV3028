import pytest
from mocks.i2cMock import MockI2C, MockI2CDevice

import rv3028.rtc_datetime as dt
from rv3028.registers import (
    BSM,
    Alarm,
    Control2,
    EEPROMBackup,
    EventControl,
    Flag,
    Reg,
    Resistance,
    Status,
)
from rv3028.rv3028 import RV3028


@pytest.fixture
def rtc():
    i2c_bus = MockI2C()
    i2c_device = MockI2CDevice(i2c_bus, 0x52)
    rtc = RV3028(i2c_device)
    return rtc


# Test functions
def test_set_and_get_time(rtc):
    rtc.time = dt.time(hour=23, minute=59, second=58)

    time_to_check = rtc.time
    assert time_to_check.hour == 23
    assert time_to_check.minute == 59
    assert time_to_check.second == 58


def test_set_and_get_date(rtc):
    rtc.date = dt.date(year=2021, month=12, day=31)

    date_to_check = rtc.date
    assert date_to_check.year == 2021
    assert date_to_check.month == 12
    assert date_to_check.day == 31


def test_year_bounds_on_set_date(rtc):
    # Test setting a date with a year below the lower bound (2000)
    with pytest.raises(ValueError):
        rtc.date = dt.date(year=1999, month=12, day=31)

    # Test setting a date with a year above the upper bound (2099)
    with pytest.raises(ValueError):
        rtc.date = dt.date(year=2100, month=1, day=1)


def test_set_and_get_datetime(rtc):
    datetime_to_set = dt.datetime(
        year=2028, month=11, day=30, hour=11, minute=11, second=12
    )
    rtc.datetime = datetime_to_set

    datetime_to_check = rtc.datetime
    assert datetime_to_check.year == 2028
    assert datetime_to_check.month == 11
    assert datetime_to_check.day == 30
    assert datetime_to_check.hour == 11
    assert datetime_to_check.minute == 11
    assert datetime_to_check.second == 12


def test_set_flag(rtc):
    # Check if _set_flag raises a ValueError
    with pytest.raises(ValueError):
        rtc._set_flag(0, 0, "funny string")


def test_set_alarm(rtc):
    rtc.set_alarm(minute=30, hour=14, weekday=3)
    alarm_minutes = rtc._read_register(Reg.ALARM_MINUTES)[0]
    alarm_hours = rtc._read_register(Reg.ALARM_HOURS)[0]
    alarm_weekday = rtc._read_register(Reg.ALARM_WEEKDAY)[0]
    assert (alarm_minutes & ~Alarm.DISABLED) == rtc._int_to_bcd(30)
    assert (alarm_hours & ~Alarm.DISABLED) == rtc._int_to_bcd(14)
    assert (alarm_weekday & ~Alarm.DISABLED) == rtc._int_to_bcd(3)


def test_check_alarm(rtc):
    rtc._set_flag(Reg.STATUS, Status.ALARM, Flag.SET)
    assert rtc.check_alarm()
    status = rtc._read_register(Reg.STATUS)[0]
    assert not (status & Status.ALARM)


def test_get_alarm(rtc):
    rtc.set_alarm(minute=4, hour=5, weekday=6)
    rtc._set_flag(Reg.ALARM_MINUTES, Alarm.DISABLED, Flag.SET)
    rtc._set_flag(Reg.ALARM_HOURS, Alarm.DISABLED, Flag.SET)
    rtc._set_flag(Reg.ALARM_WEEKDAY, Alarm.DISABLED, Flag.SET)
    assert rtc.get_alarm() == (None, None, None)

    rtc.set_alarm(minute=4)
    assert rtc.get_alarm() == (4, None, None)

    rtc.set_alarm(minute=4, hour=5)
    assert rtc.get_alarm() == (4, 5, None)

    rtc.set_alarm(minute=4, hour=5, weekday=6)
    assert rtc.get_alarm() == (4, 5, 6)


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
        rtc._int_to_bcd(0),  # count
        rtc._int_to_bcd(10),  # seconds
        rtc._int_to_bcd(20),  # minutes
        rtc._int_to_bcd(12),  # hours
        rtc._int_to_bcd(25),  # date
        rtc._int_to_bcd(9),  # month
        rtc._int_to_bcd(21),  # year
    ]
    rtc._write_register(Reg.TIMESTAMP_COUNT, bytes(timestamp))
    ts = rtc.get_event_timestamp()
    assert ts == (21, 9, 25, 12, 20, 10, 0)


def test_check_event_flag_set_and_clear(rtc):
    # Set the event flag
    rtc._set_flag(Reg.STATUS, Status.EVENT, Flag.SET)
    assert rtc.check_event_flag()  # Check and clear the flag
    status = rtc._read_register(Reg.STATUS)[0]
    assert not (status & Status.EVENT)  # Ensure the flag is cleared


def test_check_event_flag_set_without_clear(rtc):
    # Set the event flag
    rtc._set_flag(Reg.STATUS, Status.EVENT, Flag.SET)
    assert rtc.check_event_flag(clear=False)  # Check without clearing the flag
    status = rtc._read_register(Reg.STATUS)[0]
    assert status & Status.EVENT  # Ensure the flag is still set


def test_check_event_flag_not_set(rtc):
    # Ensure the event flag is not set
    assert not rtc.check_event_flag()  # Check the flag
    status = rtc._read_register(Reg.STATUS)[0]
    assert not (status & Status.EVENT)  # Ensure the flag is not set


def test_configure_backup_switchover(rtc):
    rtc.configure_backup_switchover(mode="direct", interrupt=True)
    backup_reg = rtc._read_register(Reg.EEPROM_BACKUP)[0]
    backup_mode = rtc._get_flag(
        Reg.EEPROM_BACKUP, EEPROMBackup.BACKUP_SWITCHOVER, size=BSM.SIZE
    )
    assert backup_mode == BSM.DIRECT
    assert backup_reg & EEPROMBackup.BACKUP_SWITCHOVER_INT_ENABLE


def test_check_backup_switchover_occurred(rtc):
    # Set the backup switchover flag
    rtc._set_flag(Reg.STATUS, Status.BACKUP_SWITCH, Flag.SET)
    assert rtc.check_backup_switchover()  # Check and clear the flag
    status = rtc._read_register(Reg.STATUS)[0]
    assert not (status & Status.BACKUP_SWITCH)  # Ensure the flag is cleared


def test_check_backup_switchover_occurred_without_clear(rtc):
    # Set the backup switchover flag
    rtc._set_flag(Reg.STATUS, Status.BACKUP_SWITCH, Flag.SET)
    assert rtc.check_backup_switchover(clear=False)  # Check without clearing the flag
    status = rtc._read_register(Reg.STATUS)[0]
    assert status & Status.BACKUP_SWITCH  # Ensure the flag is still set


def test_check_backup_switchover_not_occurred(rtc):
    # Ensure the backup switchover flag is not set
    assert not rtc.check_backup_switchover()  # Check the flag
    status = rtc._read_register(Reg.STATUS)[0]
    assert not (status & Status.BACKUP_SWITCH)  # Ensure the flag is not set
