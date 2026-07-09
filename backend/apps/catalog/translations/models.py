from django.db import models
from django.conf import settings


class BaseTranslation(models.Model):
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        verbose_name="idioma",
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.language}"
