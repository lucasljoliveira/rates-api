from apps.rates.external import get_currencies_from_vatcomply
from apps.rates.models import Currency
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create currencies"

    def handle(self, *args, **kwargs):
        success, data = get_currencies_from_vatcomply()

        if not success:
            self.stdout.write(
                self.style.NOTICE("Could not request currencies at VATCOMPLY.")
            )
            currency = {"name": "Dollar"}
            Currency.objects.update_or_create(pk="USD", defaults=currency)
            self.stdout.write(
                self.style.SUCCESS("Currency with ID USD created successfully.")
            )
            return
        else:
            for key, value in data.items():
                currency = {"name": value.get("name")}
                Currency.objects.update_or_create(pk=key, defaults=currency)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Currency  {key} - {value.get('name')} created successfully."
                    )
                )

        self.stdout.write(self.style.SUCCESS("Currencies created successfully."))
