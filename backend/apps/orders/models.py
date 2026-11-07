from django.db import models


def generate_order_number() -> str:
    from datetime import datetime

    from django.utils import timezone

    now = timezone.localtime()
    prefix = now.strftime("IOQUE-%Y%m%d-")
    day_prefix = prefix
    last = Order.objects.filter(order_number__startswith=day_prefix).order_by("-order_number").first()
    if last:
        try:
            seq = int(last.order_number.rsplit("-", 1)[-1]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pendiente de pago"
        PAYMENT_PROCESSING = "PAYMENT_PROCESSING", "Procesando pago"
        PAID = "PAID", "Pagado"
        PAYMENT_FAILED = "PAYMENT_FAILED", "Pago fallido"
        PAYMENT_EXPIRED = "PAYMENT_EXPIRED", "Pago expirado"
        CANCELLED = "CANCELLED", "Cancelado"
        REFUNDED = "REFUNDED", "Reembolsado"
        COMPLETED = "COMPLETED", "Completado"

    order_number = models.CharField(
        max_length=32, unique=True, verbose_name="número de pedido", editable=False
    )
    customer_name = models.CharField(max_length=255, blank=True, verbose_name="nombre del cliente")
    customer_email = models.EmailField(blank=True, verbose_name="email del cliente")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="teléfono del cliente")
    subtotal = models.PositiveIntegerField(default=0, verbose_name="subtotal")
    shipping_cost = models.PositiveIntegerField(default=0, verbose_name="costo de envío")
    discount = models.PositiveIntegerField(default=0, verbose_name="descuento por envío")
    total = models.PositiveIntegerField(default=0, verbose_name="total")
    currency = models.CharField(max_length=3, default="COP", verbose_name="moneda")
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        verbose_name="estado",
    )
    idempotency_key = models.CharField(
        max_length=128, blank=True, null=True, unique=True, db_index=True,
        verbose_name="clave de idempotencia",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="pagado")
    cancelled_at = models.DateTimeField(blank=True, null=True, verbose_name="cancelado")

    class Meta:
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["idempotency_key"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.order_number} - {self.total} {self.currency} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_order_number()
        super().save(*args, **kwargs)

    def recalc_totals(self) -> None:
        subtotal = sum(item.subtotal for item in self.items.all())
        self.subtotal = subtotal
        self.total = subtotal + self.shipping_cost - self.discount
        if self.total < 0:
            self.total = 0
        self.save(update_fields=["subtotal", "total", "updated_at"])

    @property
    def display_number(self) -> str:
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name="pedido"
    )
    product = models.ForeignKey(
        "catalog_products.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="producto",
    )
    product_name = models.CharField(max_length=255, verbose_name="nombre del producto")
    product_sku = models.CharField(max_length=20, blank=True, verbose_name="SKU")
    unit_price = models.PositiveIntegerField(default=0, verbose_name="precio unitario")
    quantity = models.PositiveIntegerField(default=1, verbose_name="cantidad")
    subtotal = models.PositiveIntegerField(default=0, verbose_name="subtotal")

    class Meta:
        verbose_name = "detalle de pedido"
        verbose_name_plural = "detalles de pedido"
        indexes = [
            models.Index(fields=["order"]),
        ]

    def __str__(self) -> str:
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)