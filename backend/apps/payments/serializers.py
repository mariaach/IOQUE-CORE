from rest_framework import serializers

from .models import Payment


class NequiPaymentSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3, default="COP")
    cart_items = serializers.JSONField(required=False, default=list)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero")
        return value

    def validate_phone_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("El número de teléfono es requerido")
        return value.strip()


class NequiPaymentResponseSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    transaction_id = serializers.CharField()
    message = serializers.CharField()


class NequiStatusSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "amount", "currency", "method", "status",
            "customer_name", "customer_email", "customer_phone",
            "created_at", "updated_at",
        ]
        read_only_fields = fields
