from django.urls import path

from .views import PaymentViewSet

urlpatterns = [
    # Nequi
    path("payments/nequi-pay/", PaymentViewSet.as_view({"post": "create_nequi_payment"}), name="nequi-pay"),
    path("payments/nequi-webhook/", PaymentViewSet.as_view({"post": "nequi_webhook"}), name="nequi-webhook"),
    path("payments/nequi-status/", PaymentViewSet.as_view({"post": "check_nequi_status"}), name="nequi-status"),
]
