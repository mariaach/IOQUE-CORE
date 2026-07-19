from rest_framework import serializers

from .models import Product, ProductTranslation, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.ImageField(source="image", read_only=True)
    thumbnail = serializers.SerializerMethodField()
    medium = serializers.SerializerMethodField()
    alt = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ["id", "url", "thumbnail", "medium", "alt", "type", "sort_order"]

    def get_thumbnail(self, obj: ProductImage) -> str | None:
        try:
            return obj.image_thumbnail.url
        except Exception:
            pass
        try:
            return obj.image.url
        except Exception:
            return None

    def get_medium(self, obj: ProductImage) -> str | None:
        try:
            return obj.image_medium.url
        except Exception:
            pass
        try:
            return obj.image.url
        except Exception:
            return None

    def get_alt(self, obj: ProductImage) -> str:
        product_name = ""
        for trans in obj.product.translations.all():
            if trans.language == self.context.get("language", "es"):
                product_name = trans.name
                break
        if not product_name:
            product_name = obj.product.sku
        type_labels = {"REAL": "Real", "KEYCHAIN": "Llavero", "DETAIL": "Detalle", "PACKAGE": "Empaque"}
        return f"{product_name} - {type_labels.get(obj.type, obj.type)}"


class ProductTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTranslation
        fields = [
            "id", "language", "name", "slug",
            "short_description", "story",
            "seo_title", "seo_description",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    short_description = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    image_thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "sku", "name", "slug", "short_description",
            "category_name", "price", "stock", "featured",
            "images", "image_thumbnail", "created_at",
        ]

    def _translation(self, obj: Product, lang: str):
        if not hasattr(obj, '_trans_cache'):
            obj._trans_cache = {t.language: t for t in obj.translations.all()}
        return obj._trans_cache.get(lang)

    def get_name(self, obj: Product) -> str:
        lang = self.context.get("language", "es")
        translation = self._translation(obj, lang)
        return translation.name if translation else str(obj)

    def get_slug(self, obj: Product) -> str:
        lang = self.context.get("language", "es")
        translation = self._translation(obj, lang)
        return translation.slug if translation else ""

    def get_short_description(self, obj: Product) -> str:
        lang = self.context.get("language", "es")
        translation = self._translation(obj, lang)
        return translation.short_description if translation else ""

    def get_category_name(self, obj: Product) -> str:
        if not obj.category:
            return ""
        lang = self.context.get("language", "es")
        trans_map = {t.language: t for t in obj.category.translations.all()}
        trans = trans_map.get(lang)
        return trans.name if trans else str(obj.category)

    def get_image_thumbnail(self, obj: Product) -> str | None:
        first = None
        for img in obj.images.all():
            if img.type == ProductImage.ImageType.REAL:
                first = img
                break
        if not first:
            return None
        try:
            return first.image_thumbnail.url
        except Exception:
            pass
        try:
            return first.image.url
        except Exception:
            return None


class ProductDetailSerializer(serializers.ModelSerializer):
    translations = ProductTranslationSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "sku", "category", "category_name",
            "price", "stock", "featured", "active",
            "translations", "images",
            "created_at", "updated_at",
        ]

    def get_category_name(self, obj: Product) -> str:
        if not obj.category:
            return ""
        lang = self.context.get("language", "es")
        trans_map = {t.language: t for t in obj.category.translations.all()}
        trans = trans_map.get(lang)
        return trans.name if trans else str(obj.category)
