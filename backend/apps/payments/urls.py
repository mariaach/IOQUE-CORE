from django.urls import path

from .views import NequiWebhookView

urlpatterns = [
    path(
        "payments/nequi-webhook/",
        NequiWebhookView.as_view(),
        name="nequi-webhook",
    ),
]
