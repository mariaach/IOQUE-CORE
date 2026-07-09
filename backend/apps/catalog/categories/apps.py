from django.apps import AppConfig


class CategoriesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog.categories"
    label = "catalog_categories"
    verbose_name = "categorías"
