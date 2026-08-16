import os
import io

from django.core.management.base import BaseCommand
from django.core.files import File
from PIL import Image
import logging

from apps.catalog.products.models import Product, ProductImage


class Command(BaseCommand):
    help = "Crea 2 imágenes DETAIL por defecto para productos que no tengan"

    def handle(self, *args, **options):
        products = Product.objects.filter(active=True).prefetch_related("images")
        created_count = 0

        for product in products:
            detail_imgs = product.images.filter(type=ProductImage.ImageType.DETAIL)
            if detail_imgs.count() >= 2:
                continue

            source_img = (
                product.images.filter(type=ProductImage.ImageType.KEYCHAIN).first()
                or product.images.filter(type=ProductImage.ImageType.REAL).first()
            )
            if not source_img:
                self.stdout.write(self.style.WARNING(
                    f"  {product.sku}: sin imagen fuente, omitido"
                ))
                continue

            source_path = source_img.image.path
            if not os.path.exists(source_path):
                self.stdout.write(self.style.WARNING(
                    f"  {product.sku}: archivo no encontrado, omitido"
                ))
                continue

            existing_count = detail_imgs.count()
            for i in range(existing_count, 2):
                ext = os.path.splitext(source_img.image.name)[1].lower() or ".jpg"
                filename = f"detail_{i}{ext}"
                img_file = self._open_and_resize(source_path, filename)

                img = ProductImage.objects.create(
                    product=product,
                    type=ProductImage.ImageType.DETAIL,
                    sort_order=10 + i,
                )
                img.image.save(filename, img_file, save=True)
                img_file.close()

                try:
                    img.image_thumbnail.url
                except Exception as e:
                    logging.warning('URL retrieval failed')
                try:
                    img.image_medium.url
                except Exception as e:
                    logging.warning('URL retrieval failed')

                created_count += 1
                self.stdout.write(
                    f"  {product.sku}: DETAIL '{filename}' creado"
                )

        self.stdout.write(self.style.SUCCESS(
            f"Listo: {created_count} imágenes DETAIL creadas"
        ))

    def _open_and_resize(self, path, filename, max_dim=1200):
        pil_img = Image.open(path)
        if pil_img.mode in ("RGBA", "P"):
            pil_img = pil_img.convert("RGB")
        if max(pil_img.size) > max_dim:
            pil_img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        buf = io.BytesIO()
        ext = os.path.splitext(filename)[1].lower()
        fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
        pil_img.save(buf, fmt, quality=85)
        buf.seek(0)
        return File(buf, name=filename)
