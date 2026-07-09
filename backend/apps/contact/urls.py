from django.urls import path

from .views import WhatsAppWidgetViewSet

urlpatterns = [
    path("contact/widget/", WhatsAppWidgetViewSet.as_view({"get": "list"}), name="contact-widget"),
]
