from rest_framework import serializers

from apps.orders.models import Order, OrderItem
from apps.payments.models import PaymentTransaction


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "product_name", "product_sku",
            "unit_price", "quantity", "subtotal",
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "customer_name", "customer_email",
            "customer_phone", "subtotal", "shipping_cost", "discount",
            "total", "currency", "status", "created_at", "updated_at", "items",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    items = serializers.ListField(child=serializers.DictField())
    customer_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    customer_email = serializers.EmailField(required=False, allow_blank=True, default="")
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")
    idempotency_key = serializers.CharField(
        max_length=128, required=False, allow_blank=True, default=""
    )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("El pedido no tiene artículos")
        for item in value:
            if "product_id" not in item or "quantity" not in item:
                raise serializers.ValidationError(
                    "Cada artículo requiere product_id y quantity"
                )
            if not isinstance(item.get("product_id"), int) or item.get("product_id") <= 0:
                raise serializers.ValidationError("product_id inválido")
            if not isinstance(item.get("quantity"), int) or item.get("quantity") <= 0:
                raise serializers.ValidationError("quantity inválido")
        return value


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            "id", "provider", "payment_method", "amount", "currency",
            "status", "provider_transaction_id", "provider_reference",
            "qr_code", "qr_payload", "expires_at", "paid_at",
            "failure_reason", "created_at", "updated_at",
        ]
        read_only_fields = fields


class OrderPaymentStatusSerializer(serializers.Serializer):
    order_status = serializers.CharField()
    payment_status = serializers.CharField()
    order_number = serializers.CharField()
    qr_code = serializers.CharField(allow_blank=True)
    qr_payload = serializers.CharField(allow_blank=True)
    expires_at = serializers.DateTimeField(allow_null=True)
    paid_at = serializers.DateTimeField(allow_null=True)