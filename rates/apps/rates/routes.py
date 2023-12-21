from django.urls import path
from rest_framework import routers

from .views import CurrencyViewSet, RateView, RateViewSet

router = routers.DefaultRouter()
router.register(r"api/rates", RateViewSet, basename="api-rates")
router.register(r"api/currencies", CurrencyViewSet, basename="api-currencies")

urlpatterns = [
    path(
        r"rates",
        RateView.as_view(
            {
                "get": "list",
            }
        ),
        name="rates",
    )
]

urlpatterns += router.urls
