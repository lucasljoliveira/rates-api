from django_filters import FilterSet

from .models import Rates


class RatesFilter(FilterSet):
    class Meta:
        model = Rates
        fields = {
            "base": ["exact"],
            "date": ["exact", "lte", "gte"],
        }
