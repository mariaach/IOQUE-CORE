from typing import Optional

import os

import requests
from django.core.files.base import ContentFile

from .models import Product


def _storage_client():
    from django.core.files.storage import default_storage
    return default_storage.connection.meta.client


def _clear_imagekit_cache(sku: str) -> None:
    from django.conf import settings
    try:
        client = _storage_client()
        prefix = f"CACHE/images/products/{sku}/"
        token = None
        while True:
            kwargs = {"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Prefix": prefix, "MaxKeys": 500}
            if token:
                kwargs["ContinuationToken"] = token
            page = client.list_objects_v2(**kwargs)
            for obj in page.get("Contents", []):
                client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=obj["Key"])
            if not page.get("IsTruncated"):
                break
            token = page.get("NextContinuationToken")
    except Exception:
        pass


def _regenerate_thumbnails(img) -> None:
    for size_attr in ("image_thumbnail", "image_medium"):
        try:
            getattr(img, size_attr).url
        except Exception:
            pass


def sync_image_from_source(img, source: str) -> bool:
    """Copia el contenido de una fuente de texto (URL, ruta local del contenedor
    o storage name) al campo image del ProductImage con el nombre canónico
    (products/<sku>/<type>_<sort>.<ext>) e invalida/regenera los thumbnails.
    Devuelve True si se aplicó un cambio."""
    source = (source or "").strip()
    if not source:
        return False

    if source.startswith(("http://", "https://")):
        resp = requests.get(source, timeout=30)
        resp.raise_for_status()
        data = resp.content
        basename = os.path.basename(resp.url.split("?", 1)[0])
    elif source.startswith("/"):
        with open(source, "rb") as fh:
            data = fh.read()
        basename = os.path.basename(source)
    else:
        from django.core.files.storage import default_storage
        if not default_storage.exists(source):
            raise ValueError(f"No existe en el storage: {source}")
        img.image = source
        img.save(update_fields=["image"])
        _clear_imagekit_cache(img.product.sku)
        _regenerate_thumbnails(img)
        return True

    ext = os.path.splitext(basename)[1].lower() or ".png"
    filename = f"{img.type.lower()}_{img.sort_order}{ext}"
    img.image.save(filename, ContentFile(data), save=True)
    _clear_imagekit_cache(img.product.sku)
    _regenerate_thumbnails(img)
    return True


class ProductService:
    @staticmethod
    def get_active_products(language: str = "es"):
        return (
            Product.objects
            .filter(active=True)
            .select_related("category")
            .prefetch_related("translations", "images")
        )

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Product]:
        return (
            Product.objects
            .filter(id=product_id)
            .select_related("category")
            .prefetch_related("translations", "images")
            .first()
        )

    @staticmethod
    def search_products(query: str, language: str = "es"):
        return (
            Product.objects
            .filter(
                active=True,
                translations__language=language,
                translations__name__icontains=query,
            )
            .select_related("category")
            .prefetch_related("translations", "images")
            .distinct()
        )
