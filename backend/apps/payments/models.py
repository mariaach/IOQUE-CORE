from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        PROCESSING = "processing", "Procesando"
        SUCCEEDED = "succeeded", "Pagado"
        FAILED = "failed", "Fallido"
        REFUNDED = "refunded", "Reembolsado"
        CANCELED = "canceled", "Cancelado"

    class Method(models.TextChoices):
        NEQUI = "nequi", "Nequi"

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="monto")
    currency = models.CharField(max_length=3, default="COP", verbose_name="moneda")
    method = models.CharField(
        max_length=10, choices=Method.choices, default=Method.NEQUI, verbose_name="método"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="estado",
    )
    nequi_transaction_id = models.CharField(
        max_length=255, unique=True, blank=True, null=True, verbose_name="ID transacción Nequi"
    )
    nequi_phone_number = models.CharField(
        max_length=20, blank=True, verbose_name="teléfono Nequi del cliente"
    )
    customer_name = models.CharField(max_length=255, blank=True, verbose_name="nombre del cliente")
    customer_email = models.EmailField(blank=True, verbose_name="email del cliente")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="teléfono del cliente")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="metadatos")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado")

    class Meta:
        verbose_name = "pago"
        verbose_name_plural = "pagos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["nequi_transaction_id"]),
        ]

    def __str__(self) -> str:
        return f"Pago {self.id} - {self.amount} {self.currency} ({self.method}, {self.status})"


class PaymentTransaction(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Creado"
        QR_GENERATED = "QR_GENERATED", "QR generado"
        PENDING = "PENDING", "Pendiente"
        APPROVED = "APPROVED", "Aprobado"
        REJECTED = "REJECTED", "Rechazado"
        EXPIRED = "EXPIRED", "Expirado"
        CANCELLED = "CANCELLED", "Cancelado"
        REVERSED = "REVERSED", "Reversado"
        ERROR = "ERROR", "Error"

    class Provider(models.TextChoices):
        NEQUI = "NEQUI", "Nequi"

    class Method(models.TextChoices):
        NEQUI_QR = "NEQUI_QR", "QR Nequi"

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payment_transactions",
        verbose_name="pedido",
    )
    provider = models.CharField(
        max_length=20, choices=Provider.choices, default=Provider.NEQUI, verbose_name="proveedor"
    )
    payment_method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.NEQUI_QR, verbose_name="método de pago"
    )
    amount = models.PositiveIntegerField(default=0, verbose_name="monto")
    currency = models.CharField(max_length=3, default="COP", verbose_name="moneda")
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.CREATED,
        verbose_name="estado",
    )
    provider_transaction_id = models.CharField(
        max_length=255, blank=True, verbose_name="ID transacción del proveedor"
    )
    provider_reference = models.CharField(
        max_length=255, blank=True, verbose_name="referencia del proveedor"
    )
    qr_code = models.URLField(blank=True, verbose_name="URL del QR")
    qr_payload = models.TextField(blank=True, verbose_name="payload del QR")
    expires_at = models.DateTimeField(blank=True, null=True, verbose_name="expira")
    failure_reason = models.TextField(blank=True, verbose_name="motivo de fallo")
    raw_response = models.JSONField(default=dict, blank=True, verbose_name="respuesta del proveedor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado")
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name="pagado")

    class Meta:
        verbose_name = "transacción de pago"
        verbose_name_plural = "transacciones de pago"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "provider_reference"],
                condition=models.Q(provider_reference__gt=""),
                name="uniq_order_provider_ref",
            ),
        ]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["provider_transaction_id"]),
            models.Index(fields=["provider_reference"]),
        ]

    def __str__(self) -> str:
        return f"{self.provider} {self.provider_reference} - {self.amount} {self.currency} ({self.status})"

    @property
    def is_terminal(self) -> bool:
        return self.status in {
            self.Status.APPROVED,
            self.Status.REJECTED,
            self.Status.EXPIRED,
            self.Status.CANCELLED,
            self.Status.REVERSED,
            self.Status.ERROR,
        }
