from django.db import models


class Currency(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=256)


class Rates(models.Model):
    date = models.DateField()
    base = models.ForeignKey(
        Currency, related_name="brates", on_delete=models.DO_NOTHING
    )
    rates = models.JSONField()

    class Meta:
        unique_together = ("date", "base")
