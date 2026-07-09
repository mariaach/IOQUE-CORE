import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category_id")
    category_slug = django_filters.CharFilter(
        method="filter_category_slug",
        label="categoría por slug",
    )
    min_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="gte", label="precio mínimo",
    )
    max_price = django_filters.NumberFilter(
        field_name="price", lookup_expr="lte", label="precio máximo",
    )
    in_stock = django_filters.BooleanFilter(
        field_name="stock", method="filter_in_stock", label="en stock",
    )

    class Meta:
        model = Product
        fields = ["featured", "active", "category"]

    def filter_category_slug(self, queryset, name: str, value: str) -> list:
        return queryset.filter(
            category__translations__slug=value,
        ).distinct()

    def filter_in_stock(self, queryset, name: str, value: bool) -> list:
        if value:
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0)
