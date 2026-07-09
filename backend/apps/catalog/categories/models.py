from django.db import models

from apps.catalog.common.models import BaseModel


class Category(BaseModel):
    class Meta:
        verbose_name = "categoría"
        verbose_name_plural = "categorías"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["active"]),
        ]

    def __str__(self) -> str:
        for trans in self.translations.all():
            if trans.language == "es":
                return trans.name
        return f"Categoría {self.pk}"


class CategoryTranslation(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="categoría",
    )
    language = models.CharField(
        max_length=10,
        choices=[("es", "Español"), ("en", "English"), ("pt", "Português"), ("fr", "Français")],
        verbose_name="idioma",
    )
    name = models.CharField(max_length=255, verbose_name="nombre")
    description = models.TextField(blank=True, verbose_name="descripción")

    class Meta:
        verbose_name = "traducción de categoría"
        verbose_name_plural = "traducciones de categorías"
        unique_together = ("category", "language")
        indexes = [
            models.Index(fields=["language"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.language})"
