from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.orders.models import Order
from apps.orders.serializers import (
    OrderCreateSerializer,
    OrderPaymentStatusSerializer,
    OrderSerializer,
    PaymentTransactionSerializer,
)
from apps.orders.services import (
    OrderNotFoundError,
    OrderService,
    OrderValidationError,
)
from apps.payments.providers import PaymentProviderError


class OrderViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()
    lookup_field = "order_number"

    def get_serializer_class(self):
        if self.action == "create_order":
            return OrderCreateSerializer
        if self.action == "payment_status":
            return OrderPaymentStatusSerializer
        if self.action == "create_nequi_qr":
            return PaymentTransactionSerializer
        return OrderSerializer

    @action(detail=False, methods=["post"], url_path="orders")
    def create_order(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            order = OrderService.create_order(
                items=data["items"],
                customer_name=data.get("customer_name", ""),
                customer_email=data.get("customer_email", ""),
                customer_phone=data.get("customer_phone", ""),
                idempotency_key=data.get("idempotency_key", ""),
            )
        except OrderValidationError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            OrderSerializer(order).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["get"], url_path="payment/status")
    def payment_status(self, request, order_number=None):
        order = get_object_or_404(Order, order_number=order_number)
        try:
            txn = OrderService.check_payment_status(order)
        except OrderNotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            OrderPaymentStatusSerializer({
                "order_status": order.status,
                "payment_status": txn.status,
                "order_number": order.order_number,
                "qr_code": txn.qr_code or "",
                "qr_payload": txn.qr_payload or "",
                "expires_at": txn.expires_at,
                "paid_at": txn.paid_at,
            }).data
        )

    @action(detail=True, methods=["post"], url_path="payment/nequi")
    def create_nequi_qr(self, request, order_number=None):
        order = get_object_or_404(Order, order_number=order_number)
        try:
            txn = OrderService.create_payment(order)
        except PaymentProviderError as exc:
            return Response(
                {"error": str(exc), "code": exc.code},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(
            PaymentTransactionSerializer(txn).data,
            status=status.HTTP_201_CREATED,
        )