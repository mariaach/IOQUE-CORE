from django.contrib import admin

from .models import Category, CategoryTranslation


class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1
    max_num = 4


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name_display", "active", "product_count", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["translations__name"]
    inlines = [CategoryTranslationInline]
    actions = ["activate_categories", "deactivate_categories"]

    def name_display(self, obj: Category) -> str:
        return str(obj)

    name_display.short_description = "nombre"

    def product_count(self, obj: Category) -> int:
        return obj.products.count()

    product_count.short_description = "productos"

    @admin.action(description="Activar categorías seleccionadas")
    def activate_categories(self, request, queryset):
        queryset.update(active=True)

    @admin.action(description="Desactivar categorías seleccionadas")
    def deactivate_categories(self, request, queryset):
        queryset.update(active=False)
