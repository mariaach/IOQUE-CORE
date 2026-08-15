import os

import requests
from django import forms
from django.core.exceptions import ValidationError

from .models import ProductImage


class ProductImageForm(forms.ModelForm):
    image = forms.CharField(
        required=False,
        label="URL / ruta de la imagen",
        widget=forms.TextInput(attrs={"class": "vLargeTextField"}),
    )

    class Meta:
        model = ProductImage
        fields = ["image", "type", "sort_order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.image:
            self.fields["image"].help_text = (
                f"Actual: {self.instance.image.name} · Puedes pegar una URL "
                "(https://...), una ruta del contenedor (p. ej. /Recursos/img-breeds/...)"
                " o un storage name (products/<sku>/...). Déjalo vacío para no cambiar."
            )

    def clean_image(self):
        source = (self.cleaned_data.get("image") or "").strip()
        if not source:
            return source
        if source.startswith(("http://", "https://")):
            try:
                resp = requests.head(source, timeout=15, allow_redirects=True)
                if resp.status_code >= 400:
                    raise ValidationError(f"La URL responde {resp.status_code}.")
            except requests.RequestException as exc:
                raise ValidationError(f"No se pudo acceder a la URL: {exc}") from exc
        elif source.startswith("/"):
            if not os.path.isfile(source):
                raise ValidationError(f"No existe la ruta en el contenedor: {source}")
        else:
            from django.core.files.storage import default_storage
            if not default_storage.exists(source):
                raise ValidationError(f"No existe en el storage: {source}")
        return source