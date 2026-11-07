from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html

from .forms import ProductImageForm
from .models import Product, ProductTranslation, ProductImage
from .services import sync_image_from_source


class ProductTranslationInline(admin.TabularInline):
    model = ProductTranslation
    extra = 1
    max_num = 4
    fields = ["language", "name", "slug", "short_description", "story", "seo_title", "seo_description"]


class ProductImageFormSet(BaseInlineFormSet):
    def _apply_source(self, form, obj):
        source = (form.cleaned_data.get("image") or "").strip()
        if not source:
            return
        previous = obj.image.name
        try:
            sync_image_from_source(obj, source)
        except Exception as exc:
            form.add_error("image", str(exc))
            obj.image = previous
            if obj.pk:
                obj.save(update_fields=["image"])

    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        self._apply_source(form, obj)
        if commit:
            obj.save()
        return obj

    def save_existing(self, form, obj, commit=True):
        if self.can_delete and self._should_delete_form(form):
            return super().save_existing(form, obj, commit)
        original = obj.image.name
        result = super().save_existing(form, obj, commit)
        source = (form.cleaned_data.get("image") or "").strip()
        if source:
            self._apply_source(form, obj)
        elif not source and original:
            obj.image = original
            obj.save(update_fields=["image"])
        return result


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    form = ProductImageForm
    formset = ProductImageFormSet
    extra = 1
    fields = ["image", "type", "sort_order", "image_preview"]
    readonly_fields = ["image_preview"]

    def image_preview(self, obj: ProductImage) -> str:
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 100px;" />',
                obj.image.url,
            )
        return ""

    image_preview.short_description = "vista previa"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "sku",
        "name_display",
        "category_display",
        "price",
        "stock",
        "featured",
        "active",
        "image_real_thumb",
        "image_keychain_thumb",
        "created_at",
    ]
    list_filter = [
        "active",
        "featured",
        "category",
        "created_at",
        "translations__language",
    ]
    search_fields = [
        "sku",
        "translations__name",
        "translations__short_description",
    ]
    inlines = [ProductTranslationInline, ProductImageInline]
    actions = [
        "activate_products",
        "deactivate_products",
        "mark_featured",
        "unmark_featured",
    ]
    list_editable = ["price", "stock", "featured", "active"]
    list_per_page = 25

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("translations", "images", "category__translations")
        )

    def name_display(self, obj: Product) -> str:
        return str(obj)

    name_display.short_description = "nombre"

    def category_display(self, obj: Product) -> str:
        if obj.category:
            return str(obj.category)
        return "-"

    category_display.short_description = "categoría"
    category_display.admin_order_field = "category"

    def _first_image_by_type(self, obj: Product, image_type: str):
        for img in obj.images.all():
            if img.type == image_type:
                return img
        return None

    def image_real_thumb(self, obj: Product) -> str:
        image = self._first_image_by_type(obj, ProductImage.ImageType.REAL)
        if image and image.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />',
                image.image.url,
            )
        return "-"

    image_real_thumb.short_description = "Real"

    def image_keychain_thumb(self, obj: Product) -> str:
        image = self._first_image_by_type(obj, ProductImage.ImageType.KEYCHAIN)
        if image and image.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />',
                image.image.url,
            )
        return "-"

    image_keychain_thumb.short_description = "Llavero"

    @admin.action(description="Activar productos seleccionados")
    def activate_products(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description="Desactivar productos seleccionados")
    def deactivate_products(self, request, queryset):
        queryset.update(active=False)

    @admin.action(description="Marcar como destacados")
    def mark_featured(self, request, queryset):
        queryset.update(featured=True)

    @admin.action(description="Quitar destacado")
    def unmark_featured(self, request, queryset):
        queryset.update(featured=False)
