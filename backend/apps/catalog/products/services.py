import logging
from typing import Optional

from django.core.files.base import ContentFile

from .models import Product, ProductImage
from .security import (
    download_remote_image,
    validate_image_bytes,
    validate_local_path,
    validate_storage_name,
)

logger = logging.getLogger(__name__)


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
        logger.exception("No se pudo limpiar la caché de ImageKit para el SKU %s", sku)


def _regenerate_thumbnails(img, *, force: bool = True) -> None:
    """Genera las variantes de ImageKit sobre el storage.

    Con la estrategia ``Optimistic`` acceder a ``.url`` NO genera el archivo:
    solo asume que ya existe. Por eso aquí se llama a ``generate()`` de forma
    explícita (y con ``force=True`` cuando la caché se acaba de borrar) para
    evitar URLs que devuelven 404.
    """
    for size_attr in ("image_thumbnail", "image_medium"):
        try:
            getattr(img, size_attr).generate(force=force)
        except Exception:
            logger.exception(
                "No se pudo regenerar %s de la imagen %s", size_attr, img.pk
            )


def _regenerate_product_thumbnails(product_id: int) -> None:
    """Regenera las variantes de TODAS las imágenes del producto.

    La caché se invalida por SKU completo, así que regenerar solo la imagen
    editada dejaría al resto de imágenes del producto con URLs 404.
    """
    for product_img in ProductImage.objects.filter(product_id=product_id):
        _regenerate_thumbnails(product_img)


def sync_image_from_source(img, source: str) -> bool:
    """Copia el contenido de una fuente de texto (URL, ruta local del contenedor
    o storage name) al campo image del ProductImage con el nombre canónico
    (products/<sku>/<type>_<sort>.<ext>) e invalida/regenera los thumbnails.
    Devuelve True si se aplicó un cambio."""
    source = (source or "").strip()
    if not source:
        return False

    if source.startswith(("http://", "https://")):
        data, _final_url = download_remote_image(source)
    elif source.startswith("/"):
        local_path = validate_local_path(source)
        with open(local_path, "rb") as fh:
            data = fh.read()
    else:
        name = validate_storage_name(source)
        from django.core.files.storage import default_storage
        if not default_storage.exists(name):
            raise ValueError(f"No existe en el storage: {name}")
        img.image = name
        img.save(update_fields=["image"])
        _clear_imagekit_cache(img.product.sku)
        _regenerate_product_thumbnails(img.product_id)
        return True

    ext = validate_image_bytes(data)
    filename = f"{img.type.lower()}_{img.sort_order}{ext}"
    img.image.save(filename, ContentFile(data), save=True)
    _clear_imagekit_cache(img.product.sku)
    _regenerate_product_thumbnails(img.product_id)
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
