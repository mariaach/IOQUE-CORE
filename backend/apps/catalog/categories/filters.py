import django_filters

from .models import Category


class CategoryFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method="filter_search",
        label="búsqueda",
    )

    class Meta:
        model = Category
        fields = ["active"]

    def filter_search(self, queryset, name: str, value: str) -> list:
        return queryset.filter(translations__name__icontains=value).distinct()
