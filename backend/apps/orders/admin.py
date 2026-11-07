from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "product_name", "product_sku", "unit_price", "quantity", "subtotal"]
    can_delete = False
    ordering = ["id"]


_STATUS_COLORS = {
    Order.Status.PENDING_PAYMENT: "#d97706",
    Order.Status.PAYMENT_PROCESSING: "#2563eb",
    Order.Status.PAID: "#16a34a",
    Order.Status.PAYMENT_FAILED: "#dc2626",
    Order.Status.PAYMENT_EXPIRED: "#6b7280",
    Order.Status.CANCELLED: "#6b7280",
    Order.Status.REFUNDED: "#9333ea",
    Order.Status.COMPLETED: "#16a34a",
}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number", "status_badge", "total", "discount", "currency",
        "customer_name", "created_at",
    ]
    list_filter = ["status", "currency", "created_at"]
    search_fields = ["order_number", "customer_name", "customer_email", "customer_phone"]
    readonly_fields = [
        "order_number", "subtotal", "shipping_cost", "discount", "total", "currency",
        "created_at", "updated_at", "paid_at", "cancelled_at",
    ]
    inlines = [OrderItemInline]
    ordering = ["-created_at"]

    @admin.display(description="Estado")
    def status_badge(self, obj):
        color = _STATUS_COLORS.get(obj.status, "#6b7280")
        return format_html(
            '<span style="color:white;background:{};padding:2px 8px;border-radius:4px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    fieldsets = [
        ("Pedido", {"fields": ["order_number", "status"]}),
        ("Cliente", {"fields": ["customer_name", "customer_email", "customer_phone"]}),
        ("Totales", {"fields": ["subtotal", "shipping_cost", "discount", "total", "currency"]}),
        ("Trazabilidad", {"fields": ["created_at", "updated_at", "paid_at", "cancelled_at"]}),
    ]

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if obj and obj.status in {
            Order.Status.PAID, Order.Status.REFUNDED, Order.Status.COMPLETED,
            Order.Status.CANCELLED,
        }:
            return fields + ("status",)
        return fields

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product_name", "quantity", "unit_price", "subtotal"]
    search_fields = ["order__order_number", "product_name", "product_sku"]
    readonly_fields = ["order", "product", "product_name", "product_sku", "unit_price", "quantity", "subtotal"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False