from datetime import datetime, timedelta

from apps.rates.utils import is_working_day, working_days_between_dates
from freezegun import freeze_time


@freeze_time("2023-10-02")
def test_is_working_day():
    now = datetime.today()
    assert is_working_day(now)


@freeze_time("2023-10-01")
def test_not_is_working_day():
    now = datetime.today()
    assert not is_working_day(now)


@freeze_time("2023-10-02")
def test_working_days_between_dates():
    now = datetime.today()
    now_plus_days = datetime.today() + timedelta(days=7)
    assert working_days_between_dates(now, now_plus_days) == 6
