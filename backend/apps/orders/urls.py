from django.urls import path

from .views import OrderViewSet

urlpatterns = [
    path("orders/", OrderViewSet.as_view({"post": "create_order"}), name="order-create"),
    path(
        "orders/<str:order_number>/payment/status/",
        OrderViewSet.as_view({"get": "payment_status"}),
        name="order-payment-status",
    ),
    path(
        "orders/<str:order_number>/payment/nequi/",
        OrderViewSet.as_view({"post": "create_nequi_qr"}),
        name="order-nequi-qr",
    ),
]