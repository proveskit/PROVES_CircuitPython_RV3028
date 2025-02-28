"""
Basic date and time formatting library for RV-3028-C7 RTC module.

Author: Davit Babayan
"""

_MONTH_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def _is_leap_year(year: int) -> bool:
    "year -> True if leap year, else False."
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _validate_times(hour: int, minute: int, second: int) -> None:
    if not (0 <= hour <= 23):
        raise ValueError("Hour must be in 0..24")
    if not (0 <= minute <= 59):
        raise ValueError("Minute must be in 0..59")
    if not (0 <= second <= 59):
        raise ValueError("Second must be in 0..59")


def _validate_dates(year: int, month: int, day: int) -> None:
    if not (2000 <= year <= 2099):
        raise ValueError("Year must be in 2000..2099")
    if not (1 <= month <= 12):
        raise ValueError("Month must be in 1..12")
    if month == 2 and _is_leap_year(year):
        if not (1 <= day <= 29):
            raise ValueError("Day must be in 1..29")
        elif not (1 <= day <= _MONTH_DAYS[month - 1]):
            raise ValueError(f"Day must be in 1..{_MONTH_DAYS[month - 1]}")


class rtime:
    """
    Class that represents time in hours, minutes and seconds.

    Attributes:
        hour (int): The hour of the time.
        minute (int): The minute of the time.
        second (int): The second of the time.
    """

    def __new__(cls, hour: int, minute: int, second: int) -> "rtime":
        _validate_times(hour, minute, second)
        self = super().__new__(cls)
        self._hour = hour
        self._minute = minute
        self._second = second
        return self

    def __repr__(self) -> str:
        return f"{self.hour}:{self.minute}:{self.second}"

    __str__ = __repr__

    @property
    def hour(self) -> int:
        return self._hour

    @property
    def minute(self) -> int:
        return self._minute

    @property
    def second(self) -> int:
        return self._second


class rdate:
    """
    Class that represents date in year, month and day.

    Attributes:
        year (int): The year of the date.
        month (int): The month of the date.
        day (int): The day of the date.
    """

    def __new__(cls, year: int, month: int, day: int) -> "rdate":
        _validate_dates(year, month, day)
        self = super().__new__(cls)
        self._year = year
        self._month = month
        self._day = day
        return self

    def __repr__(self) -> str:
        return f"{self.year}-{self.month}-{self.day}"

    __str__ = __repr__

    @property
    def year(self) -> int:
        return self._year

    @property
    def month(self) -> int:
        return self._month

    @property
    def day(self) -> int:
        return self._day
