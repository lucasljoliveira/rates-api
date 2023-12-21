from datetime import timedelta


def is_working_day(day):
    if day.weekday() >= 5:
        return False
    return True


def working_days_between_dates(initial_date: str, final_date: str):
    working_days = 0
    current_day = initial_date

    while current_day <= final_date:
        if is_working_day(current_day):
            working_days += 1
        current_day += timedelta(days=1)

    return working_days
