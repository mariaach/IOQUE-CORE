from django.contrib import admin

from .models import Payment


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