import hashlib
import os
import re

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.catalog.products.models import Product, ProductImage


SOURCE_DIRS = {
    1: [
        (ProductImage.ImageType.REAL, "/Recursos/img-breeds"),
        (ProductImage.ImageType.KEYCHAIN, "/Recursos/img-keychain"),
    ],
    3: [
        (ProductImage.ImageType.REAL, "/Recursos/img-religion"),
    ],
}


def _slug_from_filename(filename: str) -> str:
    import unicodedata

    stem = os.path.splitext(filename)[0]
    stem = stem.replace("_", "-").lower()
    stem = re.sub(r"^\d+-", "", stem)
    stem = unicodedata.normalize("NFKD", stem)
    stem = "".join(c for c in stem if not unicodedata.combining(c))
    return stem


def _md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


class Command(BaseCommand):
    help = (
        "Re-sube las imágenes de productos existentes desde /Recursos a R2 "
        "cuando el contenido difiere del objeto en storage, y regenera los "
        "thumbnails. Corrige imágenes desactualizadas respecto a los fuentes."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--product",
            type=int,
            default=None,
            help="Limitar a un id de producto (por defecto: todos).",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Solo reportar qué se actualizaría, sin subir.",
        )
        parser.add_argument(
            "--type",
            type=str,
            choices=[t.value for t in ProductImage.ImageType],
            default=None,
            help="Limitar a un tipo de imagen (REAL/KEYCHAIN/...).",
        )

    def handle(self, *args, **options):
        product_id = options.get("product")
        check_only = options.get("check")
        only_type = options.get("type")

        source_files: dict = {}
        for cat_id, dirs in SOURCE_DIRS.items():
            for img_type, dir_path in dirs:
                if not os.path.isdir(dir_path):
                    continue
                for fname in os.listdir(dir_path):
                    full = os.path.join(dir_path, fname)
                    if not os.path.isfile(full):
                        continue
                    source_files.setdefault(_slug_from_filename(fname), []).append(
                        {"type": img_type, "path": full}
                    )

        client = None
        bucket = settings.AWS_STORAGE_BUCKET_NAME

        def storage_etag(key: str):
            nonlocal client
            if client is None:
                from django.core.files.storage import default_storage
                client = default_storage.connection.meta.client
            try:
                resp = client.head_object(Bucket=bucket, Key=key)
                return resp["ETag"].strip('"')
            except Exception:
                return None

        def delete_cache_prefix(sku: str):
            if client is None:
                return
            prefix = f"CACHE/images/products/{sku}/"
            token = None
            while True:
                kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 500}
                if token:
                    kwargs["ContinuationToken"] = token
                page = client.list_objects_v2(**kwargs)
                for obj in page.get("Contents", []):
                    client.delete_object(Bucket=bucket, Key=obj["Key"])
                if not page.get("IsTruncated"):
                    break
                token = page.get("NextContinuationToken")

        queryset = Product.objects.filter(category_id__in=SOURCE_DIRS).order_by("id")
        if product_id is not None:
            queryset = queryset.filter(id=product_id)

        total = 0
        updated = 0
        skipped = 0
        errors = []

        for product in queryset.iterator():
            es = product.translations.filter(language="es").first()
            slug = es.slug if es else None
            candidates = source_files.get(slug, []) if slug else []

            for img in product.images.all():
                if only_type and img.type != only_type:
                    continue
                match = next((c for c in candidates if c["type"] == img.type), None)
                if not match:
                    errors.append(f"{product.sku} img {img.id}: sin fuente para {img.type}")
                    continue
                total += 1
                with open(match["path"], "rb") as fh:
                    data = fh.read()
                local_md5 = _md5(data)
                remote_md5 = storage_etag(img.image.name)
                if remote_md5 == local_md5:
                    skipped += 1
                    continue

                if check_only:
                    self.stdout.write(
                        f"  [diff] {product.sku} {img.type} {img.image.name} "
                        f"(remoto {remote_md5} -> local {local_md5})"
                    )
                    updated += 1
                    continue

                basename = os.path.basename(img.image.name)
                img.image.save(basename, ContentFile(data), save=True)
                updated += 1
                self.stdout.write(f"  OK {product.sku} {img.type} -> {img.image.name}")
                if client is not None:
                    delete_cache_prefix(product.sku)

        if check_only:
            self.stdout.write(
                f"Check: {updated} imágenes difieren del fuente ({skipped} iguales)."
            )
        else:
            self.stdout.write(
                f"Sync: {updated} imágenes re-subidas, {skipped} sin cambios, "
                f"{total} revisadas."
            )
            if errors:
                self.stderr.write(self.style.WARNING(
                    f"{len(errors)} imágenes sin fuente: {errors[:10]}"
                ))

        if updated and not check_only:
            self.stdout.write("Regenerando thumbnails...")
            call_command("regenerate_thumbnails")
            self.stdout.write(self.style.SUCCESS("Thumbnails regenerados."))