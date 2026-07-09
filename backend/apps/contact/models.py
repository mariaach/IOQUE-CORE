from django.db import models


class WhatsAppWidget(models.Model):
    enabled = models.BooleanField(default=True, verbose_name="habilitado")
    company_name = models.CharField(max_length=255, blank=True, default="IOQUE", verbose_name="nombre de la empresa")
    whatsapp_number = models.CharField(max_length=20, default="573177695006", verbose_name="número de WhatsApp")
    welcome_message = models.TextField(blank=True, verbose_name="mensaje de bienvenida")
    form_title = models.CharField(max_length=255, blank=True, verbose_name="título del formulario")
    submit_button_text = models.CharField(max_length=100, blank=True, verbose_name="texto del botón")
    privacy_policy_text = models.CharField(max_length=255, blank=True, verbose_name="texto de políticas")
    privacy_policy_url = models.URLField(blank=True, verbose_name="URL de políticas")
    theme_color = models.CharField(max_length=7, default="#25D366", verbose_name="color del tema")
    logo = models.ImageField(upload_to="widget/", blank=True, null=True, verbose_name="logo")
    position = models.CharField(max_length=5, choices=[("left", "Izquierda"), ("right", "Derecha")], default="right", verbose_name="posición")
    show_company_field = models.BooleanField(default=True, verbose_name="mostrar campo empresa")
    show_email_field = models.BooleanField(default=True, verbose_name="mostrar campo correo")
    show_phone_field = models.BooleanField(default=True, verbose_name="mostrar campo teléfono")
    require_company = models.BooleanField(default=False, verbose_name="requerir empresa")
    require_email = models.BooleanField(default=False, verbose_name="requerir correo")
    require_phone = models.BooleanField(default=False, verbose_name="requerir teléfono")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="actualizado")

    class Meta:
        verbose_name = "widget de WhatsApp"
        verbose_name_plural = "widgets de WhatsApp"

    def __str__(self) -> str:
        return f"WhatsApp Widget ({self.company_name})"

    def save(self, *args, **kwargs) -> None:
        if self.enabled:
            WhatsAppWidget.objects.filter(enabled=True).exclude(pk=self.pk).update(enabled=False)
        super().save(*args, **kwargs)


class WhatsAppWidgetTranslation(models.Model):
    widget = models.ForeignKey(
        WhatsAppWidget,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="widget",
    )
    language = models.CharField(
        max_length=10,
        choices=[("es", "Español"), ("en", "English"), ("pt", "Português"), ("fr", "Français")],
        verbose_name="idioma",
    )
    welcome_message = models.TextField(blank=True, verbose_name="mensaje de bienvenida")
    form_title = models.CharField(max_length=255, blank=True, verbose_name="título del formulario")
    submit_button_text = models.CharField(max_length=100, blank=True, verbose_name="texto del botón")
    privacy_policy_text = models.CharField(max_length=255, blank=True, verbose_name="texto de políticas")

    class Meta:
        verbose_name = "traducción del widget"
        verbose_name_plural = "traducciones del widget"
        unique_together = ("widget", "language")
        indexes = [models.Index(fields=["language"])]

    def __str__(self) -> str:
        return f"{self.language}"
