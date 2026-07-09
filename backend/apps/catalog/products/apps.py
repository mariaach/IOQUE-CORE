from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog.products"
    label = "catalog_products"
    verbose_name = "productos"
