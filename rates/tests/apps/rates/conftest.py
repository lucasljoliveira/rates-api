from datetime import date, datetime

import pytest
from factories import CurrencyFactory, RateFactory
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def currency_data():
    return {"id": "USD", "name": "Dollar"}


@pytest.fixture
def rate_data(faker, currency):
    return {
        "date": "2023-10-18",
        "base": currency.id,
        "rates": {
            "EUR": 0.9159186664224216,
            "USD": 1.0,
            "BRL": 2.0,
            "JPY": 142.83751602857663,
        },
    }


@pytest.fixture
def rates_view_data(rate_data):
    return {
        "date__gte": "2023-10-18",
        "date__lte": "2023-10-19",
        "symbol": "EUR",
        "rates": [rate_data, rate_data],
    }


@pytest.fixture
def rates_view_data_internal_value(rates_view_data):
    new_rates_view_data = rates_view_data.copy()
    data = []
    symbol = rates_view_data["symbol"]
    for item in new_rates_view_data["rates"]:
        item_date = date.fromisoformat(item["date"])
        item_date = datetime.combine(item_date, datetime.min.time())
        date_seconds = int(item_date.timestamp()) * 1000
        data.append([date_seconds, item["rates"][symbol]])
    new_rates_view_data["rates"] = data
    return new_rates_view_data


@pytest.fixture
def currency():
    return CurrencyFactory()


@pytest.fixture
def rate():
    return RateFactory()
