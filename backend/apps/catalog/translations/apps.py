from django.apps import AppConfig


class TranslationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.catalog.translations"
    label = "catalog_translations"
