from unittest import mock

import pytest
from apps.rates.serializers import CurrencySerializer, RateSerializer
from django.urls import reverse
from factories import CurrencyFactory, RateFactory
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db


class TestCurrencyView:
    def test_create(self, api_client, currency_data):
        url = reverse("api-currencies-list")
        response = api_client.post(url, currency_data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_list(self, api_client, currency):
        url = reverse("api-currencies-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_retrieve(self, api_client, currency):
        url = reverse("api-currencies-detail", args=[currency.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == currency.id

    def test_update(self, api_client, currency):
        new_name = currency.name + "NEW"
        currency_data = CurrencySerializer(currency).data
        currency_data["name"] = new_name
        url = reverse("api-currencies-detail", args=[currency.id])
        response = api_client.put(url, data=currency_data)
        assert response.status_code == status.HTTP_200_OK
        currency.refresh_from_db()
        assert currency.name == new_name

    def test_partial_update(self, api_client, currency):
        new_name = currency.name + " updated"
        data = {"name": new_name}
        url = reverse("api-currencies-detail", args=[currency.id])
        response = api_client.patch(url, data=data)
        assert response.status_code == status.HTTP_200_OK
        currency.refresh_from_db()
        assert currency.name == new_name


class TestRateView:
    def test_create(self, api_client, rate_data):
        url = reverse("api-rates-list")
        response = api_client.post(url, rate_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_list(self, api_client, rate):
        url = reverse("api-rates-list")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_retrieve(self, api_client, rate):
        url = reverse("api-rates-detail", args=[rate.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["date"] == rate.date
        assert response.data["base"] == rate.base.id
        assert response.data["rates"] == rate.rates

    def test_update(self, api_client, rate):
        new_rates = rate.rates
        new_rates.update({"NEW": 123})
        rate_data = RateSerializer(rate).data
        rate_data["rates"] = new_rates
        url = reverse("api-rates-detail", args=[rate.id])
        response = api_client.put(url, data=rate_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        rate.refresh_from_db()
        assert rate.rates == new_rates

    def test_partial_update(self, api_client, rate):
        new_rates = rate.rates
        new_rates.update({"NEW": 123})
        data = {"rates": new_rates}
        url = reverse("api-rates-detail", args=[rate.id])
        response = api_client.patch(url, data=data, format="json")
        assert response.status_code == status.HTTP_200_OK
        rate.refresh_from_db()
        assert rate.rates == new_rates


class TestRatesViewSerializer:
    @mock.patch("apps.rates.views.get_rates_from_vatcomply")
    def test_list_success_without_external_data(
        self, mocked_get_rates_from_vatcomply, api_client
    ):
        initial_date = "2023-10-18"
        final_date = "2023-10-19"
        currency = CurrencyFactory(id="USD")
        RateFactory(base=currency, date=initial_date)
        RateFactory(base=currency, date=final_date)

        url = reverse("rates")
        params = {"date__gte": initial_date, "date__lte": final_date, "symbol": "BRL"}
        response = api_client.get(url, params)

        expected_rates_var = [[1697598000000, 2.0], [1697684400000, 2.0]]
        assert response.status_code == status.HTTP_200_OK
        assert f"var rates = {str(expected_rates_var)}" in response.content.decode(
            "utf-8"
        )
        mocked_get_rates_from_vatcomply.assert_not_called()

    @mock.patch("apps.rates.views.get_rates_from_vatcomply")
    def test_list_success_with_external_data(
        self, mocked_get_rates_from_vatcomply, api_client, rate_data
    ):
        currency = CurrencyFactory(id="USD")
        rate_data["date"] = "2023-10-20"
        rate_data["base"] = currency.id
        mocked_get_rates_from_vatcomply.return_value = [rate_data]

        initial_date = "2023-10-18"
        middle_date = "2023-10-19"
        final_date = "2023-10-20"
        RateFactory(base=currency, date=initial_date)
        RateFactory(base=currency, date=middle_date)

        url = reverse("rates")
        params = {"date__gte": initial_date, "date__lte": final_date, "symbol": "BRL"}
        response = api_client.get(url, params)

        expected_rates_var = [
            [1697598000000, 2.0],
            [1697684400000, 2.0],
            [1697770800000, 2.0],
        ]
        assert response.status_code == status.HTTP_200_OK
        assert f"var rates = {str(expected_rates_var)}" in response.content.decode(
            "utf-8"
        )

    @freeze_time("2023-10-03")
    @mock.patch("apps.rates.views.get_rates_from_vatcomply")
    def test_list_success_with_dates_greater_than_today(
        self, mocked_get_rates_from_vatcomply, api_client
    ):
        initial_date = "2023-10-18"
        final_date = "2023-10-19"
        actual_date = "2023-10-02"
        currency = CurrencyFactory(id="USD")
        RateFactory(base=currency, date=actual_date)

        url = reverse("rates")
        params = {"date__gte": initial_date, "date__lte": final_date, "symbol": "BRL"}
        response = api_client.get(url, params)

        expected_rates_var = [[1696204800000, 2.0]]
        assert response.status_code == status.HTTP_200_OK
        assert f"var rates = {str(expected_rates_var)}" in response.content.decode(
            "utf-8"
        )
        mocked_get_rates_from_vatcomply.assert_not_called()

    @freeze_time("2023-10-03")
    @mock.patch("apps.rates.views.get_rates_from_vatcomply")
    def test_list_success_without_filters(
        self, mocked_get_rates_from_vatcomply, api_client
    ):
        actual_date = "2023-10-02"
        currency = CurrencyFactory(id="USD")
        RateFactory(base=currency, date=actual_date)

        url = reverse("rates")
        response = api_client.get(url)

        expected_rates_var = [[1696204800000, 2.0]]
        assert response.status_code == status.HTTP_200_OK
        assert f"var rates = {str(expected_rates_var)}" in response.content.decode(
            "utf-8"
        )
        mocked_get_rates_from_vatcomply.assert_not_called()
