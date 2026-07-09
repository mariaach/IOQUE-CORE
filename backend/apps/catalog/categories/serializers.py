from rest_framework import serializers

from .models import Category, CategoryTranslation


class CategoryTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryTranslation
        fields = ["id", "language", "name", "description"]


class CategoryListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "description", "active", "created_at"]

    def get_name(self, obj: Category) -> str:
        lang = self.context.get("language", "es")
        trans_map = {t.language: t for t in obj.translations.all()}
        translation = trans_map.get(lang)
        return translation.name if translation else str(obj)

    def get_description(self, obj: Category) -> str:
        lang = self.context.get("language", "es")
        trans_map = {t.language: t for t in obj.translations.all()}
        translation = trans_map.get(lang)
        return translation.description if translation else ""


class CategoryDetailSerializer(serializers.ModelSerializer):
    translations = CategoryTranslationSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "translations", "active", "created_at", "updated_at"]
