from django.contrib import admin

from .models import WhatsAppWidget, WhatsAppWidgetTranslation


class WhatsAppWidgetTranslationInline(admin.TabularInline):
    model = WhatsAppWidgetTranslation
    extra = 4
    max_num = 4
    fields = ["language", "welcome_message", "form_title", "submit_button_text", "privacy_policy_text"]


@admin.register(WhatsAppWidget)
class WhatsAppWidgetAdmin(admin.ModelAdmin):
    list_display = ["company_name", "whatsapp_number", "enabled", "position", "created_at"]
    list_filter = ["enabled", "position"]
    search_fields = ["company_name", "whatsapp_number"]
    inlines = [WhatsAppWidgetTranslationInline]
    fieldsets = [
        ("General", {"fields": ["enabled", "company_name", "whatsapp_number", "theme_color", "position", "logo"]}),
        ("Mensajes", {"fields": ["welcome_message", "form_title", "submit_button_text"]}),
        ("Privacidad", {"fields": ["privacy_policy_text", "privacy_policy_url"]}),
        ("Campos del formulario", {"fields": [
            ("show_company_field", "show_email_field", "show_phone_field"),
            ("require_company", "require_email", "require_phone"),
        ]}),
    ]
