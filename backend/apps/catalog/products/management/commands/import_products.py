import os
import re
import hashlib
import io
from typing import Dict, Optional

from django.core.management.base import BaseCommand
from PIL import Image
from django.db import transaction
from django.core.files import File

from apps.catalog.products.models import Product, ProductTranslation, ProductImage
from apps.catalog.categories.models import CategoryTranslation
from apps.catalog.categories.services import CategoryService


class Command(BaseCommand):
    help = "Importa productos desde los directorios img-breeds e img-keychain"

    PRODUCT_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
    BREEDS_DIR = "/Recursos/img-breeds"
    KEYCHAIN_DIR = "/Recursos/img-keychain"

    def handle(self, *args, **options):
        if not os.path.isdir(self.BREEDS_DIR):
            self.stderr.write(self.style.ERROR(
                f"Directorio no encontrado: {self.BREEDS_DIR}"
            ))
            return

        if not os.path.isdir(self.KEYCHAIN_DIR):
            self.stderr.write(self.style.ERROR(
                f"Directorio no encontrado: {self.KEYCHAIN_DIR}"
            ))
            return

        breed_files = self._get_files(self.BREEDS_DIR)
        keychain_files = self._get_files(self.KEYCHAIN_DIR)
        all_stems = sorted(set(breed_files.keys()) | set(keychain_files.keys()))

        if not all_stems:
            self.stdout.write(self.style.WARNING(
                "No se encontraron archivos de imagen válidos."
            ))
            return

        category = CategoryService.get_or_create_dogs_category()

        existing_slugs = set(
            ProductTranslation.objects
            .filter(language="es", slug__in=[self._slug(s) for s in all_stems])
            .values_list("slug", flat=True)
        )

        stems_to_import = [s for s in all_stems if self._slug(s) not in existing_slugs]

        if stems_to_import:
            last_product = Product.objects.order_by("id").last()
            start_index = (last_product.id + 1) if last_product else 1

            created = 0
            errors = []

            with transaction.atomic():
                for i, stem in enumerate(stems_to_import, start=start_index):
                    try:
                        self._create_product(
                            stem=stem,
                            breed_file=breed_files.get(stem),
                            keychain_file=keychain_files.get(stem),
                            category=category,
                            index=i,
                        )
                        created += 1
                    except Exception as e:
                        errors.append(f"{stem}: {e}")

            self.stdout.write(self.style.SUCCESS(
                f"Importación completada: {created} productos creados."
            ))
            if errors:
                for error in errors:
                    self.stderr.write(self.style.WARNING(f"  Error: {error}"))

        self._regenerate_thumbnails()

        self._fill_missing_translations()

    def _get_files(self, directory: str) -> Dict[str, str]:
        result = {}
        for f in os.listdir(directory):
            filepath = os.path.join(directory, f)
            if os.path.isfile(filepath):
                stem, ext = os.path.splitext(f)
                ext = ext.lower()
                if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif") and self.PRODUCT_NAME_PATTERN.match(stem):
                    result[stem] = f
        return result

    def _product_name(self, filename: str) -> str:
        stem = os.path.splitext(filename)[0]
        stem = re.sub(r"^\d+-", "", stem)
        return " ".join(word.capitalize() for word in re.split(r"[-_]", stem))

    def _slug(self, stem: str) -> str:
        stem = re.sub(r"^\d+-", "", stem)
        return stem.replace("_", "-").lower()

    def _generate_sku(self, index: int) -> str:
        return f"KEY-{index:06d}"

    def _translation_data(self, name: str, slug: str) -> dict:
        return {
            "es": {
                "name": name,
                "slug": slug,
                "short_description": f"Llavero personalizado de {name}",
                "story": f"Historia de {name}. Llavero artesanal personalizado.",
                "seo_title": name,
                "seo_description": f"Llavero personalizado de {name}. Producto artesanal único.",
            },
            "en": {
                "name": name,
                "slug": slug,
                "short_description": f"Custom keychain of {name}",
                "story": f"Story of {name}. Custom artisan keychain.",
                "seo_title": name,
                "seo_description": f"Custom keychain of {name}. Unique artisan product.",
            },
            "pt": {
                "name": name,
                "slug": slug,
                "short_description": f"Chaveiro personalizado de {name}",
                "story": f"História de {name}. Chaveiro artesanal personalizado.",
                "seo_title": name,
                "seo_description": f"Chaveiro personalizado de {name}. Produto artesanal único.",
            },
            "fr": {
                "name": name,
                "slug": slug,
                "short_description": f"Porte-clés personnalisé de {name}",
                "story": f"Histoire de {name}. Porte-clés artisanal personnalisé.",
                "seo_title": name,
                "seo_description": f"Porte-clés personnalisé de {name}. Produit artisanal unique.",
            },
        }

    def _regenerate_thumbnails(self):
        errors = 0
        for img in ProductImage.objects.iterator():
            for size_name, size_attr in [("thumbnail", "image_thumbnail"), ("medium", "image_medium")]:
                try:
                    getattr(img, size_attr).url
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Error generating {size_name} for image {img.id}: {e}"
                        )
                    )
        if errors:
            self.stdout.write(self.style.WARNING(
                f"Errores en generación de thumbnails: {errors}"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "Thumbnails verificados."
            ))

    def _fill_missing_translations(self):
        filled = 0
        products = Product.objects.filter(active=True).prefetch_related("translations")
        for product in products:
            existing_langs = set(
                product.translations.values_list("language", flat=True)
            )
            translation = product.translations.filter(language="es").first()
            if not translation:
                continue
            name = translation.name
            slug = translation.slug
            for lang in ("en", "pt", "fr"):
                if lang not in existing_langs:
                    data = self._translation_data(name, slug)
                    ProductTranslation.objects.create(
                        product=product,
                        language=lang,
                        **data[lang],
                    )
                    filled += 1
        if filled:
            self.stdout.write(self.style.SUCCESS(
                f"Traducciones completadas: {filled} creadas."
            ))

    def _open_and_resize(self, path: str, filename: str, max_dim: int = 1200) -> File:
        from PIL import Image as PilImage
        pil_img = PilImage.open(path)
        if pil_img.mode in ("RGBA", "P"):
            pil_img = pil_img.convert("RGB")
        if max(pil_img.size) > max_dim:
            pil_img.thumbnail((max_dim, max_dim), PilImage.LANCZOS)
        buf = io.BytesIO()
        ext = os.path.splitext(filename)[1].lower()
        fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
        pil_img.save(buf, fmt, quality=85)
        buf.seek(0)
        return File(buf, name=filename)

    def _generate_thumbnails(self, img):
        for size_name, size_attr in [("thumbnail", "image_thumbnail"), ("medium", "image_medium")]:
            try:
                getattr(img, size_attr).url
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Error generating {size_name} for image {img.id}: {e}"
                    )
                )

    def _create_product(
        self,
        stem: str,
        breed_file: Optional[str],
        keychain_file: Optional[str],
        category,
        index: int,
    ):
        filename = breed_file or keychain_file
        product_name = self._product_name(filename)
        slug = self._slug(stem)
        sku = self._generate_sku(index)

        price_points = [27000, 27500, 28000, 28500, 29000]
        price_idx = hashlib.md5(stem.encode()).digest()[0] % len(price_points)
        price = price_points[price_idx]

        product = Product.objects.create(
            category=category,
            sku=sku,
            price=price,
            stock=1,
            active=True,
        )

        for lang, name_translated in self._translation_data(product_name, slug).items():
            ProductTranslation.objects.create(
                product=product,
                language=lang,
                name=name_translated["name"],
                slug=name_translated["slug"],
                short_description=name_translated["short_description"],
                story=name_translated["story"],
                seo_title=name_translated["seo_title"],
                seo_description=name_translated["seo_description"],
            )

        if breed_file:
            path = os.path.join(self.BREEDS_DIR, breed_file)
            img_file = self._open_and_resize(path, breed_file)
            img = ProductImage.objects.create(
                product=product,
                type=ProductImage.ImageType.REAL,
                sort_order=0,
            )
            img.image.save(breed_file, img_file, save=True)
            img_file.close()
            self._generate_thumbnails(img)

        if keychain_file:
            path = os.path.join(self.KEYCHAIN_DIR, keychain_file)
            img_file = self._open_and_resize(path, keychain_file)
            img = ProductImage.objects.create(
                product=product,
                type=ProductImage.ImageType.KEYCHAIN,
                sort_order=1,
            )
            img.image.save(keychain_file, img_file, save=True)
            img_file.close()
            self._generate_thumbnails(img)
