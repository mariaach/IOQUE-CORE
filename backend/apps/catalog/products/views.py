from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer
from .filters import ProductFilter
from .services import ProductService


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    filterset_class = ProductFilter
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        language = self.request.query_params.get("language", "es")
        context["language"] = language
        return context

    def get_queryset(self):
        queryset = Product.objects.filter(active=True)\
            .select_related("category")\
            .prefetch_related("translations", "images", "category__translations")
        language = self.request.query_params.get("language", "es")
        if language:
            queryset = queryset.filter(translations__language=language)
        return queryset.distinct()

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        query = request.query_params.get("q", "")
        language = request.query_params.get("language", "es")
        if not query:
            return Response({"results": []})
        products = ProductService.search_products(query, language)
        serializer = ProductListSerializer(
            products, many=True, context={"language": language},
        )
        return Response({"results": serializer.data})
