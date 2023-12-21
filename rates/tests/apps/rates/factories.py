import factory
from apps.rates.models import Currency, Rates


class CurrencyFactory(factory.django.DjangoModelFactory):
    id = factory.Faker("pystr", min_chars=3, max_chars=3)
    name = factory.Faker("name")

    class Meta:
        model = Currency


class RateFactory(factory.django.DjangoModelFactory):
    base = factory.SubFactory(CurrencyFactory)
    date = factory.Faker("date")
    rates = {
        "EUR": 0.9159186664224216,
        "USD": 1.0,
        "BRL": 2.0,
        "JPY": 142.83751602857663,
    }

    class Meta:
        model = Rates
