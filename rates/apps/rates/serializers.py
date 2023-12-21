from datetime import date, datetime

from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Currency, Rates
from .utils import working_days_between_dates


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rates
        fields = "__all__"


class RatesViewSerializer(serializers.Serializer):
    rates = serializers.ListField()
    date__gte = serializers.DateField()
    date__lte = serializers.DateField()
    symbol = serializers.CharField(max_length=5)

    class Meta:
        fields = ("data", "date__gte", "date__lte", "symbol")

    def to_internal_value(self, attrs):
        rates = attrs["rates"]
        symbol = attrs["symbol"]

        data = []
        for item in rates:
            item_date = item["date"]
            if isinstance(item_date, str):
                item_date = date.fromisoformat(item_date)
            item_date = datetime.combine(item_date, datetime.min.time())
            date_seconds = int(item_date.timestamp()) * 1000
            data.append([date_seconds, item["rates"][symbol]])

        attrs["rates"] = data
        return super().to_internal_value(attrs)

    def validate(self, attrs):
        max_working_days = settings.MAX_WORKING_DAYS_RESULT
        data = attrs["rates"]
        date__gte = attrs["date__gte"]
        date__lte = attrs["date__lte"]

        working_days = working_days_between_dates(date__gte, date__lte)
        if len(data) == working_days or (
            working_days > max_working_days and len(data) == max_working_days
        ):
            return attrs

        raise ValidationError("MissingRatesException")
