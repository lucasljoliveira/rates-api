from datetime import date, timedelta

from django.conf import settings
from django.shortcuts import render
from django.utils import timezone
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError

from .external import get_rates_from_vatcomply
from .filters import RatesFilter
from .models import Currency, Rates
from .serializers import CurrencySerializer, RateSerializer, RatesViewSerializer


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer


class RateViewSet(viewsets.ModelViewSet):
    queryset = Rates.objects.select_related("base").all()
    serializer_class = RateSerializer
    filterset_class = RatesFilter


class RateView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Rates.objects.all()

    date__gte = None
    date__lte = None

    @property
    def iso_date__gte(self):
        if self.date__gte:
            return date.fromisoformat(self.date__gte)

    @property
    def iso_date__lte(self):
        if self.date__lte:
            return date.fromisoformat(self.date__lte)

    def set_class_dates(self, params):
        iso_current_date = timezone.now().date() - timedelta(days=1)
        current_date = iso_current_date.isoformat()

        self.date__gte = params.get("date__gte") or current_date
        self.date__lte = params.get("date__lte") or current_date

        if self.iso_date__gte > iso_current_date:
            self.date__gte = current_date
        if self.iso_date__lte > iso_current_date:
            self.date__lte = current_date

    def filter_queryset(self, queryset):
        base_symbol = settings.BASE_SYMBOL
        queryset = queryset.filter(
            date__gte=self.date__gte, date__lte=self.date__lte, base=base_symbol
        ).order_by("date")[: settings.MAX_WORKING_DAYS_RESULT]
        return queryset

    def get_queryset_date_as_string(self, queryset):
        days = []
        for item in queryset:
            days.append(item.date.isoformat())
        return days

    def save_external_data(self, external_data):
        for item in external_data:
            serializer = RateSerializer(data=item)
            if serializer.is_valid():
                serializer.save()

    def get_data_from_external_source(self, queryset):
        data = []
        data.extend(queryset.values())
        queryset_days = self.get_queryset_date_as_string(queryset)

        external_data = get_rates_from_vatcomply(
            self.iso_date__gte, self.iso_date__lte, queryset_days
        )
        self.save_external_data(external_data)

    def list(self, request, *args, **kwargs):
        params = request.query_params
        symbol = params.get("symbol", "BRL")

        self.set_class_dates(params)
        queryset_data = self.filter_queryset(self.get_queryset())

        unserialized_data = {
            "rates": queryset_data.values(),
            "date__gte": self.date__gte,
            "date__lte": self.date__lte,
            "symbol": symbol,
        }

        serializer = RatesViewSerializer(data=unserialized_data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError:
            self.get_data_from_external_source(queryset_data)
            queryset_data = self.filter_queryset(self.get_queryset())
            unserialized_data["rates"] = queryset_data.values()
            serializer = RatesViewSerializer(data=unserialized_data)
            serializer.is_valid(raise_exception=True)

        return render(request, "index.html", serializer.data)
