from django.core.management.base import BaseCommand

from apps.contact.models import WhatsAppWidget, WhatsAppWidgetTranslation


class Command(BaseCommand):
    help = "Crea la configuración inicial del widget de WhatsApp"

    def handle(self, *args, **options):
        if WhatsAppWidget.objects.exists():
            self.stdout.write("El widget ya existe. Usa el admin para modificarlo.")
            return

        widget = WhatsAppWidget.objects.create(
            enabled=True,
            company_name="IOQUE",
            whatsapp_number="573177695006",
            theme_color="#25D366",
            show_company_field=True,
            show_email_field=True,
            show_phone_field=True,
            require_company=False,
            require_email=False,
            require_phone=False,
        )

        translations = {
            "es": {
                "welcome_message": "Estamos para ayudarte",
                "form_title": "Cont\u00e1ctanos",
                "submit_button_text": "Enviar",
                "privacy_policy_text": "Acepto las pol\u00edticas de privacidad",
            },
            "en": {
                "welcome_message": "We are here to help",
                "form_title": "Contact us",
                "submit_button_text": "Send",
                "privacy_policy_text": "I accept the privacy policy",
            },
            "pt": {
                "welcome_message": "Estamos aqui para ajudar",
                "form_title": "Fale conosco",
                "submit_button_text": "Enviar",
                "privacy_policy_text": "Aceito as pol\u00edticas de privacidade",
            },
            "fr": {
                "welcome_message": "Nous sommes l\u00e0 pour vous aider",
                "form_title": "Contactez-nous",
                "submit_button_text": "Envoyer",
                "privacy_policy_text": "J'accepte la politique de confidentialit\u00e9",
            },
        }

        for lang, data in translations.items():
            WhatsAppWidgetTranslation.objects.create(
                widget=widget,
                language=lang,
                **data,
            )

        self.stdout.write(self.style.SUCCESS("Widget de WhatsApp creado correctamente."))
