from rest_framework import serializers

from .models import WhatsAppWidget, WhatsAppWidgetTranslation


class WhatsAppWidgetTranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppWidgetTranslation
        fields = [
            "language", "welcome_message", "form_title",
            "submit_button_text", "privacy_policy_text",
        ]


class WhatsAppWidgetSerializer(serializers.ModelSerializer):
    translations = WhatsAppWidgetTranslationSerializer(many=True, read_only=True)
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = WhatsAppWidget
        fields = [
            "enabled", "company_name", "whatsapp_number",
            "welcome_message", "form_title", "submit_button_text",
            "privacy_policy_text", "privacy_policy_url",
            "theme_color", "logo_url", "position",
            "show_company_field", "show_email_field", "show_phone_field",
            "require_company", "require_email", "require_phone",
            "translations",
        ]

    def get_logo_url(self, obj: WhatsAppWidget) -> str | None:
        if obj.logo:
            try:
                return obj.logo.url
            except Exception:
                return None
        return None
