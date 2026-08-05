import os
import re
import io
import unicodedata
from typing import Dict, List

from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import transaction

from apps.catalog.products.models import Product, ProductTranslation, ProductImage
from apps.catalog.categories.models import Category, CategoryTranslation


RELIGION_CATEGORY_ID = 3
DEFAULT_PRICE = 15000

CATEGORY_TRANSLATIONS = [
    {"language": "es", "name": "Religión", "description": "Llaveros artesanales religiosos"},
    {"language": "en", "name": "Religion", "description": "Handmade religious keychains"},
    {"language": "pt", "name": "Religião", "description": "Chaveiros artesanais religiosos"},
    {"language": "fr", "name": "Religion", "description": "Porte-clés artisanaux religieux"},
]


def _normalize(value: str) -> str:
    value = value.lower()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"^\d+", "", value)
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"[^a-z0-9 ]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _make_slug(name: str, used_slugs: set) -> str:
    base = _normalize(name).replace(" ", "-") or "relicario"
    slug = base
    suffix = 2
    while slug in used_slugs:
        slug = f"{base}-{suffix}"
        suffix += 1
    used_slugs.add(slug)
    return slug


class Command(BaseCommand):
    help = "Importa productos religiosos desde img-religion con listaRelicarios.txt"

    def add_arguments(self, parser):
        parser.add_argument(
            "--image-dir",
            default="/Recursos/img-religion",
            help="Directorio con las imágenes PNG de religión",
        )
        parser.add_argument(
            "--list-file",
            default="/Recursos/img-religion/listaRelicarios.txt",
            help="Archivo con precio y descripción de cada relicario",
        )

    def handle(self, *args, **options):
        image_dir = options["image_dir"]
        list_file = options["list_file"]

        if not os.path.isdir(image_dir):
            self.stderr.write(self.style.ERROR(f"Directorio no encontrado: {image_dir}"))
            return
        if not os.path.isfile(list_file):
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {list_file}"))
            return

        images = self._get_images(image_dir)
        if not images:
            self.stderr.write(self.style.ERROR("No se encontraron imágenes válidas."))
            return

        entries = self._parse_list(list_file)
        if not entries:
            self.stderr.write(self.style.ERROR("No se pudieron leer descripciones del archivo."))
            return

        # El primer número del nombre de la imagen indica el orden y
        # corresponde al índice de la línea en listaRelicarios.txt
        entry_by_index = {
            entry["index"]: entry
            for entry in entries
        }

        category = self._get_category()
        used_slugs = set(
            ProductTranslation.objects.filter(language="es").values_list("slug", flat=True)
        )
        sku_number = self._next_sku_number()

        created = 0
        errors = []

        with transaction.atomic():
            for filename in images:
                stem = os.path.splitext(filename)[0]
                try:
                    index = self._image_index(stem)
                    entry = entry_by_index.get(index)
                    if entry is None:
                        errors.append(f"{filename}: sin descripción para índice {index}")
                        continue

                    already = ProductTranslation.objects.filter(
                        language="es",
                        name=entry["name"],
                        short_description=entry["description"],
                        product__category_id=RELIGION_CATEGORY_ID,
                    ).exists()
                    if already:
                        errors.append(f"{filename}: ya importado ({entry['name']})")
                        continue

                    sku = f"REL-{sku_number:06d}"
                    sku_number += 1
                    created += 1
                    self._create_product(
                        entry=entry,
                        filename=filename,
                        image_dir=image_dir,
                        category=category,
                        sku=sku,
                        used_slugs=used_slugs,
                    )
                except Exception as e:
                    errors.append(f"{stem}: {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Importación religión completada: {created} productos creados."
        ))
        if errors:
            for error in errors:
                self.stderr.write(self.style.WARNING(f"  {error}"))

        self._regenerate_thumbnails()

    def _get_images(self, image_dir: str) -> List[str]:
        result = []
        for f in sorted(os.listdir(image_dir)):
            filepath = os.path.join(image_dir, f)
            if os.path.isfile(filepath) and os.path.splitext(f)[1].lower() in (".jpg", ".jpeg", ".png", ".webp"):
                result.append(f)
        return result

    def _image_index(self, stem: str):
        match = re.match(r"^\s*(\d+)", stem)
        if not match:
            return -1
        return int(match.group(1))

    def _parse_list(self, list_file: str) -> List[dict]:
        entries = []
        with open(list_file, encoding="utf-8") as fh:
            for line_no, raw in enumerate(fh, start=1):
                line = raw.strip()
                if not line or ";" not in line:
                    continue
                parts = [part.strip() for part in line.split(";")]

                index = -1
                if parts and re.fullmatch(r"\d+", parts[0]):
                    index = int(parts[0])
                    parts = parts[1:]

                if not parts:
                    continue
                price_part = parts[0]
                desc = ";".join(parts[1:]).strip() if len(parts) > 1 else ""
                if not desc:
                    continue

                price = DEFAULT_PRICE
                price_match = re.search(r"(\d[\d.,]*)", price_part)
                if price_match:
                    parsed = re.sub(r"[^\d]", "", price_match.group(1))
                    if parsed:
                        price = int(parsed)
                        if price <= 0:
                            price = DEFAULT_PRICE

                name = re.split(r"\s*\(", desc, maxsplit=1)[0].strip().rstrip(".") or desc
                entries.append({
                    "index": index if index != -1 else line_no,
                    "price": price,
                    "name": name,
                    "description": desc,
                })
        return entries

    def _get_category(self) -> Category:
        category, _ = Category.objects.get_or_create(
            id=RELIGION_CATEGORY_ID,
            defaults={"active": True},
        )
        for data in CATEGORY_TRANSLATIONS:
            CategoryTranslation.objects.update_or_create(
                category=category,
                language=data["language"],
                defaults={"name": data["name"], "description": data["description"]},
            )
        return category

    def _next_sku_number(self) -> int:
        last = (
            Product.objects.filter(sku__startswith="REL-")
            .order_by("-sku")
            .values_list("sku", flat=True)
            .first()
        )
        if last:
            return int(last.split("-")[1]) + 1
        return 1

    def _translation_data(self, name: str, slug: str, description: str) -> dict:
        base = {
            "es": {
                "name": name,
                "slug": slug,
                "short_description": description,
                "story": description,
                "seo_title": name,
                "seo_description": description,
            },
            "en": {
                "name": name,
                "slug": slug,
                "short_description": description,
                "story": description,
                "seo_title": name,
                "seo_description": description,
            },
            "pt": {
                "name": name,
                "slug": slug,
                "short_description": description,
                "story": description,
                "seo_title": name,
                "seo_description": description,
            },
            "fr": {
                "name": name,
                "slug": slug,
                "short_description": description,
                "story": description,
                "seo_title": name,
                "seo_description": description,
            },
        }
        return base

    def _create_product(
        self,
        entry: dict,
        filename: str,
        image_dir: str,
        category: Category,
        sku: str,
        used_slugs: set,
    ):
        name = entry["name"]
        slug = _make_slug(name, used_slugs)
        description = entry["description"]
        price = entry["price"]

        product = Product.objects.create(
            category=category,
            sku=sku,
            price=price,
            stock=1,
            active=True,
        )

        for lang, data in self._translation_data(name, slug, description).items():
            ProductTranslation.objects.create(
                product=product,
                language=lang,
                name=data["name"],
                slug=data["slug"],
                short_description=data["short_description"],
                story=data["story"],
                seo_title=data["seo_title"],
                seo_description=data["seo_description"],
            )

        path = os.path.join(image_dir, filename)
        img_file = self._open_and_resize(path, filename)
        img = ProductImage.objects.create(
            product=product,
            type=ProductImage.ImageType.REAL,
            sort_order=0,
        )
        img.image.save(filename, img_file, save=True)
        img_file.close()
        self._generate_thumbnails(img)

    def _open_and_resize(self, path: str, filename: str, max_dim: int = 1000) -> File:
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
        for size_attr in ("image_thumbnail", "image_medium"):
            try:
                getattr(img, size_attr).url
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"  Error generando {size_attr} para imagen {img.id}: {e}")
                )

    def _regenerate_thumbnails(self):
        errors = 0
        for img in ProductImage.objects.filter(product__category_id=RELIGION_CATEGORY_ID).iterator():
            for size_attr in ("image_thumbnail", "image_medium"):
                try:
                    getattr(img, size_attr).url
                except Exception as e:
                    errors += 1
                    self.stdout.write(self.style.WARNING(
                        f"  Error generando {size_attr} para imagen {img.id}: {e}"
                    ))
        if errors:
            self.stdout.write(self.style.WARNING(f"Errores en generación de thumbnails: {errors}"))
        else:
            self.stdout.write(self.style.SUCCESS("Thumbnails verificados."))
