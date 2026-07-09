from typing import Optional

from .models import Product


class ProductService:
    @staticmethod
    def get_active_products(language: str = "es"):
        return (
            Product.objects
            .filter(active=True)
            .select_related("category")
            .prefetch_related("translations", "images")
        )

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Product]:
        return (
            Product.objects
            .filter(id=product_id)
            .select_related("category")
            .prefetch_related("translations", "images")
            .first()
        )

    @staticmethod
    def search_products(query: str, language: str = "es"):
        return (
            Product.objects
            .filter(
                active=True,
                translations__language=language,
                translations__name__icontains=query,
            )
            .select_related("category")
            .prefetch_related("translations", "images")
            .distinct()
        )
