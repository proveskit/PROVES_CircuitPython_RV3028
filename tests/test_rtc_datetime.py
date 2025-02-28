import pytest
from mocks.i2cMock import MockI2C, MockI2CDevice

import rv3028.rtc_datetime as dt
from rv3028.rv3028 import RV3028


@pytest.fixture
def rtc():
    i2c_bus = MockI2C()
    i2c_device = MockI2CDevice(i2c_bus, 0x52)
    rtc = RV3028(i2c_device)
    return rtc


# Test functions
def test_leap_year():
    assert dt._is_leap_year(2000)
    assert not dt._is_leap_year(2001)
    assert not dt._is_leap_year(2100)
    assert dt._is_leap_year(2004)


def test_validate_times():
    with pytest.raises(ValueError):
        dt._validate_times(24, 0, 0)
    with pytest.raises(ValueError):
        dt._validate_times(0, 60, 0)
    with pytest.raises(ValueError):
        dt._validate_times(0, 0, 60)


def test_validate_dates():
    with pytest.raises(ValueError):
        dt._validate_dates(1999, 1, 1)  # year to small
    with pytest.raises(ValueError):
        dt._validate_dates(2100, 1, 1)  # year too big
    with pytest.raises(ValueError):
        dt._validate_dates(2000, 0, 1)  # month too small
    with pytest.raises(ValueError):
        dt._validate_dates(2000, 13, 1)  # month too large
    with pytest.raises(ValueError):
        dt._validate_dates(2000, 4, 31)  # day too big
    with pytest.raises(ValueError):
        dt._validate_dates(2001, 2, 29)  # Not a leap year
    try:
        dt._validate_dates(2000, 2, 29)  # Valid leap year date
    except ValueError:
        pytest.fail("Unexpected ValueError raised")


def test_time():
    t = dt.time(12, 20, 14)
    assert t.hour == 12
    assert t.minute == 20
    assert t.second == 14
    assert str(t) == "12:20:14"


def test_date():
    d = dt.date(2002, 11, 14)
    assert d.year == 2002
    assert d.month == 11
    assert d.day == 14
    assert str(d) == "2002-11-14"


def test_datetime():
    dt1 = dt.datetime(2002, 11, 14, 12, 20, 14)
    assert dt1.year == 2002
    assert dt1.month == 11
    assert dt1.day == 14
    assert dt1.hour == 12
    assert dt1.minute == 20
    assert dt1.second == 14
    assert str(dt1) == "2002-11-14 12:20:14"


def test_combine_and_split_datetime():
    t = dt.time(12, 20, 14)
    d = dt.date(2002, 11, 14)
    dt2 = dt.datetime.combine(d, t)
    assert str(dt2) == "2002-11-14 12:20:14"
    assert str(dt2.time()) == "12:20:14"
    assert str(dt2.date()) == "2002-11-14"
