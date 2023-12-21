import pytest
from apps.rates.serializers import (
    CurrencySerializer,
    RateSerializer,
    RatesViewSerializer,
)
from rest_framework.exceptions import ValidationError

pytestmark = pytest.mark.django_db


class TestCurrencySerializer:
    def test_is_valid(self, currency_data):
        serializer = CurrencySerializer(data=currency_data)
        assert serializer.is_valid() is True
        serializer.save()

    def test_not_is_valid(self, currency_data):
        currency_data["id"] = "this-is-invalid-id.com"
        serializer = CurrencySerializer(data=currency_data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestRateSerializer:
    def test_is_valid(self, rate_data):
        serializer = RateSerializer(data=rate_data)
        assert serializer.is_valid() is True
        serializer.save()

    def test_not_is_valid(self, rate_data):
        rate_data["base"] = "this-is-invalid-base.com"
        serializer = RateSerializer(data=rate_data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestRatesViewSerializer:
    def test_is_valid(self, rates_view_data):
        serializer = RatesViewSerializer(data=rates_view_data)
        assert serializer.is_valid() is True

    def test_not_is_valid(self, rates_view_data):
        rates_view_data["rates"] = []
        serializer = RatesViewSerializer(data=rates_view_data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_to_internal_value(self, rates_view_data, rates_view_data_internal_value):
        serializer = RatesViewSerializer(data=rates_view_data)
        assert serializer.is_valid() is True
        assert serializer.data == rates_view_data_internal_value
