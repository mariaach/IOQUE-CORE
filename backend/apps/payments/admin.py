from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "amount", "currency", "status", "customer_name", "customer_email", "created_at"]
    list_filter = ["status", "currency", "created_at"]
    search_fields = ["customer_name", "customer_email", "stripe_payment_intent_id"]
    readonly_fields = ["stripe_payment_intent_id", "stripe_client_secret", "created_at", "updated_at"]
    fieldsets = [
        ("Información del pago", {"fields": ["amount", "currency", "status", "stripe_payment_intent_id"]}),
        ("Cliente", {"fields": ["customer_name", "customer_email", "customer_phone"]}),
        ("Metadatos", {"fields": ["metadata"]}),
        ("Fechas", {"fields": ["created_at", "updated_at"]}),
    ]
