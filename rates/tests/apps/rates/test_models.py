import pytest
from apps.rates.models import Currency, Rates

pytestmark = pytest.mark.django_db


class TestRate:
    def test_create(self, rate_data):
        rate_data["base_id"] = rate_data.pop("base")
        rate = Rates.objects.create(**rate_data)

        assert Rates.objects.count() == 1
        assert rate.date == rate_data["date"]
        assert rate.base.id == rate_data["base_id"]
        assert rate.rates == rate_data["rates"]


class TestCurrency:
    def test_create(self, currency_data):
        currency = Currency.objects.create(**currency_data)

        assert Currency.objects.count() == 1
        assert currency.id == currency_data["id"]
        assert currency.name == currency_data["name"]
