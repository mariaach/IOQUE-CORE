from rest_framework import viewsets, permissions

from .models import Category
from .serializers import CategoryListSerializer, CategoryDetailSerializer
from .filters import CategoryFilter
from .services import CategoryService


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    filterset_class = CategoryFilter
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryListSerializer
        return CategoryDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        language = self.request.query_params.get("language", "es")
        context["language"] = language
        return context

    def get_queryset(self):
        queryset = Category.objects.filter(active=True).prefetch_related("translations")
        language = self.request.query_params.get("language", "es")
        if language:
            queryset = queryset.filter(translations__language=language)
        return queryset.distinct()
