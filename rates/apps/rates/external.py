from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone

from .utils import is_working_day, working_days_between_dates


def get_current_date(iso_initial_date, day):
    current_date = iso_initial_date + timedelta(days=day)
    is_weekend_day = not is_working_day(current_date)
    if is_weekend_day:
        current_date = current_date + timedelta(days=2)
    return current_date


def is_valid_date(current_date, non_needed_dates):
    already_got_this_date = current_date.isoformat() in non_needed_dates
    is_day_after_today = current_date > timezone.now().date()
    if already_got_this_date or is_day_after_today:
        return False
    return True


def request_data(params):
    url = settings.VATCOMPLY_URL + "/rates"
    response = requests.request("GET", url, params=params)
    return response.json()


def get_rates_from_vatcomply(iso_initial_date, iso_final_date, non_needed_dates):
    days = working_days_between_dates(iso_initial_date, iso_final_date)
    data = []

    params = {"base": settings.BASE_SYMBOL}

    for day in range(days):
        got_all_required_data = (
            len(data) + len(non_needed_dates)
        ) == settings.MAX_WORKING_DAYS_RESULT
        if got_all_required_data:
            break

        current_date = get_current_date(iso_initial_date, day)
        if not is_valid_date(current_date, non_needed_dates):
            continue

        params["date"] = current_date.isoformat()
        result = request_data(params)

        result_has_correct_date = result["date"] == params["date"]
        if result_has_correct_date:
            data.append(result)

    return data


def get_currencies_from_vatcomply():
    url = settings.VATCOMPLY_URL + "/currencies"
    response = requests.request("GET", url)

    result = (
        response.status_code == 200,
        None if response.status_code != 200 else response.json(),
    )
    return result
