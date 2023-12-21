from unittest import mock

import pytest
from apps.rates.models import Currency
from django.core.management import call_command

pytestmark = pytest.mark.django_db


@pytest.fixture
def currencies():
    return {
        "USD": {"name": "US Dollar", "symbol": "$"},
        "EUR": {"name": "Euro", "symbol": "€"},
        "BRL": {"name": "Brazilian Real", "symbol": "R$"},
    }


@mock.patch("apps.rates.external.requests.request")
def test_from_vatcomply(mocked_get, currencies):
    mocked_get.return_value = mock.Mock(
        json=mock.Mock(return_value=currencies), status_code=200
    )
    actual_count = Currency.objects.count()
    assert actual_count == 0
    call_command("create_currencies")

    expected_count = Currency.objects.count()
    assert expected_count == 3


@mock.patch("apps.rates.external.requests.request")
def test_get_failure(mocked_get):
    mocked_get.return_value = mock.Mock(status_code=400)
    actual_count = Currency.objects.count()
    assert actual_count == 0
    call_command("create_currencies")

    expected_count = Currency.objects.count()
    assert expected_count == 1
