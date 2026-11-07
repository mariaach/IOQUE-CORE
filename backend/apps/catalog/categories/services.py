from typing import Optional

from .models import Category, CategoryTranslation


class CategoryService:
    @staticmethod
    def get_active_categories(language: str = "es") -> list:
        return Category.objects.filter(active=True).prefetch_related("translations")

    @staticmethod
    def get_category_by_id(category_id: int) -> Optional[Category]:
        return Category.objects.filter(id=category_id).prefetch_related("translations").first()

    @staticmethod
    def get_or_create_mascotas_category() -> Category:
        category, created = Category.objects.get_or_create(
            id=1,
            defaults={"active": True},
        )
        if created:
            translations_data = [
                {"language": "es", "name": "Mascotas", "description": "Llaveros artesanales de razas de mascotas"},
                {"language": "en", "name": "Pets", "description": "Handmade keychains of pet breeds"},
                {"language": "pt", "name": "Animais de Estimação", "description": "Chaveiros artesanais de raças de animais de estimação"},
                {"language": "fr", "name": "Animaux", "description": "Porte-clés artisanaux de races d'animaux"},
            ]
            for data in translations_data:
                CategoryTranslation.objects.create(category=category, **data)
        return category

    @staticmethod
    def get_or_create_dogs_category() -> Category:
        return CategoryService.get_or_create_mascotas_category()

    @staticmethod
    def get_category_translation(
        category: Category, language: str
    ) -> Optional[CategoryTranslation]:
        for trans in category.translations.all():
            if trans.language == language:
                return trans
        return None
