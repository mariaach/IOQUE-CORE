from django import forms
from django.core.exceptions import ValidationError

from .models import ProductImage
from .security import (
    UnsafeSourceError,
    validate_local_path,
    validate_remote_url,
    validate_storage_name,
)


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

        try:
            if source.startswith(("http://", "https://")):
                return validate_remote_url(source)
            if source.startswith("/"):
                return validate_local_path(source)

            name = validate_storage_name(source)
            from django.core.files.storage import default_storage

            if not default_storage.exists(name):
                raise ValidationError(f"No existe en el storage: {name}")
            return name
        except UnsafeSourceError as exc:
            raise ValidationError(str(exc)) from exc
