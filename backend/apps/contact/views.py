from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .models import WhatsAppWidget
from .serializers import WhatsAppWidgetSerializer


class WhatsAppWidgetViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = WhatsAppWidgetSerializer

    def get_queryset(self):
        return WhatsAppWidget.objects.filter(enabled=True).prefetch_related("translations")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        widget = queryset.first()
        if widget:
            serializer = self.get_serializer(widget)
            return Response(serializer.data)
        return Response({"enabled": False})
