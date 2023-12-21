from datetime import date
from unittest import mock

import pytest
from apps.rates.external import get_rates_from_vatcomply


@pytest.fixture
def rate_data_from_vatcomply(faker):
    return {
        "date": "2023-10-18",
        "base": "USD",
        "rates": {
            "EUR": 0.9159186664224216,
            "USD": 1.0,
            "BRL": 2.0,
            "JPY": 142.83751602857663,
        },
    }


@mock.patch("apps.rates.external.requests.request")
def test_get_rates_from_vatcomply(mocked_get, rate_data_from_vatcomply):
    rate_1 = rate_data_from_vatcomply.copy()
    rate_1["date"] = "2023-10-18"
    rate_2 = rate_data_from_vatcomply.copy()
    rate_2["date"] = "2023-10-19"
    mocked_get.side_effect = [
        mock.Mock(json=mock.Mock(return_value=rate_1)),
        mock.Mock(json=mock.Mock(return_value=rate_2)),
    ]
    initial_date = date.fromisoformat("2023-10-18")
    final_date = date.fromisoformat("2023-10-19")
    data = get_rates_from_vatcomply(initial_date, final_date, [])
    assert data[0] == rate_1
    assert data[1] == rate_2


@mock.patch("apps.rates.external.requests.request")
def test_get_rates_from_vatcomply_with_more_than_max_days(
    mocked_get, rate_data_from_vatcomply
):
    rate_1 = rate_data_from_vatcomply.copy()
    rate_1["date"] = "2023-10-18"
    rate_2 = rate_data_from_vatcomply.copy()
    rate_2["date"] = "2023-10-23"
    mocked_get.side_effect = [
        mock.Mock(json=mock.Mock(return_value=rate_1)),
        mock.Mock(json=mock.Mock(return_value=rate_2)),
    ]
    non_needed_dates = [
        "2023-10-20",
        "2023-10-19",
        "2023-10-24",
    ]
    initial_date = date.fromisoformat("2023-10-18")
    final_date = date.fromisoformat("2023-10-27")
    data = get_rates_from_vatcomply(initial_date, final_date, non_needed_dates)
    assert data == [rate_1, rate_2]
