from django.contrib import admin

from .models import Payment, PaymentTransaction


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "amount", "currency", "status", "nequi_phone_number", "created_at"]
    list_filter = ["status", "currency", "created_at"]
    search_fields = ["customer_name", "customer_email", "nequi_phone_number", "nequi_transaction_id"]
    readonly_fields = ["nequi_transaction_id", "created_at", "updated_at"]
    fieldsets = [
        ("Información del pago", {"fields": ["amount", "currency", "status", "nequi_transaction_id"]}),
        ("Cliente", {"fields": ["customer_name", "customer_email", "customer_phone", "nequi_phone_number"]}),
        ("Metadatos", {"fields": ["metadata"]}),
        ("Fechas", {"fields": ["created_at", "updated_at"]}),
    ]


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id", "order", "provider", "amount", "currency",
        "status", "provider_reference", "expires_at", "paid_at",
    ]
    list_filter = ["provider", "status", "currency", "created_at"]
    search_fields = [
        "order__order_number",
        "provider_transaction_id",
        "provider_reference",
    ]
    readonly_fields = [
        "order", "provider", "payment_method", "amount", "currency",
        "provider_transaction_id", "provider_reference", "qr_code",
        "qr_payload", "expires_at", "paid_at", "failure_reason",
        "raw_response", "created_at", "updated_at",
    ]
    list_select_related = ["order"]
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        return False

    fieldsets = [
        ("Transacción", {"fields": ["order", "provider", "payment_method", "status"]}),
        ("Monto", {"fields": ["amount", "currency"]}),
        ("Proveedor", {"fields": ["provider_transaction_id", "provider_reference"]}),
        ("QR", {"fields": ["qr_code", "qr_payload"]}),
        ("Tiempos", {"fields": ["expires_at", "paid_at", "created_at", "updated_at"]}),
        ("Diagnóstico", {"fields": ["failure_reason", "raw_response"]}),
    ]