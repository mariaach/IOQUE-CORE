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
        CARD = "card", "Tarjeta"
        NEQUI = "nequi", "Nequi"

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="monto")
    currency = models.CharField(max_length=3, default="COP", verbose_name="moneda")
    method = models.CharField(
        max_length=10, choices=Method.choices, default=Method.CARD, verbose_name="método"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="estado",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255, unique=True, blank=True, null=True, verbose_name="ID de PaymentIntent"
    )
    stripe_client_secret = models.TextField(blank=True, verbose_name="client_secret")
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
            models.Index(fields=["stripe_payment_intent_id"]),
            models.Index(fields=["nequi_transaction_id"]),
        ]

    def __str__(self) -> str:
        return f"Pago {self.id} - {self.amount} {self.currency} ({self.method}, {self.status})"
