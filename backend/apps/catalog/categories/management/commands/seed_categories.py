import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from apps.catalog.categories.models import Category, CategoryTranslation


class Command(BaseCommand):
    help = "Crea/actualiza categorías desde docs/categories.json"

    def handle(self, *args, **options):
        fixture_path = os.path.join(settings.BASE_DIR, "docs", "categories.json")

        if not os.path.exists(fixture_path):
            self.stderr.write(self.style.ERROR(
                f"Archivo no encontrado: {fixture_path}"
            ))
            return

        with open(fixture_path, "r", encoding="utf-8") as f:
            categories = json.load(f)

        created = 0
        updated = 0

        for cat_data in categories:
            pk = cat_data["pk"]
            fields = cat_data["fields"]
            translations = cat_data.get("translations", [])

            category, was_created = Category.objects.update_or_create(
                id=pk,
                defaults={"active": fields.get("active", True)},
            )

            if was_created:
                created += 1
                self.stdout.write(f"  Categoría '{pk}' creada")
            else:
                updated += 1

            for trans in translations:
                CategoryTranslation.objects.update_or_create(
                    category=category,
                    language=trans["language"],
                    defaults={
                        "name": trans["name"],
                        "description": trans.get("description", ""),
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f"Seed completado: {created} creadas, {updated} actualizadas"
        ))
