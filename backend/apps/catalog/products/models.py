import os

from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, ResizeToFill

from apps.catalog.common.models import BaseModel
from apps.catalog.categories.models import Category


class Product(BaseModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="categoría",
    )
    sku = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="SKU",
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="precio",
    )
    stock = models.PositiveIntegerField(default=1, verbose_name="stock")
    featured = models.BooleanField(default=False, verbose_name="destacado")

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["featured"]),
            models.Index(fields=["active"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self) -> str:
        for trans in self.translations.all():
            if trans.language == "es":
                return trans.name
        return self.sku


class ProductTranslation(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="translations",
        verbose_name="producto",
    )
    language = models.CharField(
        max_length=10,
        choices=[("es", "Español"), ("en", "English"), ("pt", "Português"), ("fr", "Français")],
        verbose_name="idioma",
    )
    name = models.CharField(max_length=255, verbose_name="nombre")
    slug = models.SlugField(max_length=255, verbose_name="slug")
    short_description = models.TextField(blank=True, verbose_name="descripción corta")
    story = models.TextField(blank=True, verbose_name="historia")
    seo_title = models.CharField(max_length=255, blank=True, verbose_name="título SEO")
    seo_description = models.TextField(blank=True, verbose_name="descripción SEO")

    class Meta:
        verbose_name = "traducción de producto"
        verbose_name_plural = "traducciones de producto"
        unique_together = ("product", "language")
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["language"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.language})"


def product_image_upload_path(instance, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
    return f"products/{instance.product.sku}/{instance.type.lower()}_{instance.sort_order}.{ext}"


class ProductImage(models.Model):
    class ImageType(models.TextChoices):
        REAL = "REAL", "Real"
        KEYCHAIN = "KEYCHAIN", "Llavero"
        DETAIL = "DETAIL", "Detalle"
        PACKAGE = "PACKAGE", "Empaque"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="producto",
    )
    image = models.ImageField(
        upload_to=product_image_upload_path,
        verbose_name="imagen",
    )
    image_thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(400, 400)],
        format="JPEG",
        options={"quality": 85},
    )
    image_medium = ImageSpecField(
        source="image",
        processors=[ResizeToFit(800, 800)],
        format="JPEG",
        options={"quality": 90},
    )
    type = models.CharField(
        max_length=10,
        choices=ImageType.choices,
        verbose_name="tipo",
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name="orden")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creado")

    class Meta:
        verbose_name = "imagen de producto"
        verbose_name_plural = "imágenes de producto"
        ordering = ["sort_order"]
        indexes = [
            models.Index(fields=["product", "type"]),
        ]

    def __str__(self) -> str:
        return f"{self.product.sku} - {self.type}"

    @property
    def filename(self) -> str:
        return os.path.basename(self.image.name)
