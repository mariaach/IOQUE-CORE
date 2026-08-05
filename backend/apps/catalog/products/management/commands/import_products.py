import os
import re
import json
import hashlib
import io
from typing import Dict, Optional, List, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files import File

from apps.catalog.products.models import Product, ProductTranslation, ProductImage
from apps.catalog.categories.services import CategoryService


class Command(BaseCommand):
    help = "Importa productos desde directorios de imágenes de Recursos"

    PRODUCT_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")

    DEFAULT_DIRS = {
        "1": [("REAL", "/Recursos/img-breeds"), ("KEYCHAIN", "/Recursos/img-keychain")],
        "3": [("REAL", "/Recursos/img-religion")],
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--category-id",
            type=int,
            default=1,
            help="ID de la categoría (default: 1=Mascotas)",
        )
        parser.add_argument(
            "--dir",
            action="append",
            dest="image_dirs",
            metavar="TYPE:PATH",
            help=(
                "Directorio de imágenes como TYPE:PATH (ej: KEYCHAIN:/Recursos/img-religion). "
                "Puede repetirse. Si no se indica, usa los directorios por defecto de la categoría."
            ),
        )

    def handle(self, *args, **options):
        category_id = options["category_id"]
        image_dirs = self._parse_dirs(options.get("image_dirs"), category_id)

        if not image_dirs:
            self.stderr.write(self.style.ERROR(
                f"No hay directorios configurados para categoría {category_id}. "
                f"Usa --dir TYPE:PATH para especificar."
            ))
            return

        # Validar que todos los directorios existan
        for img_type, dir_path in image_dirs:
            if not os.path.isdir(dir_path):
                self.stderr.write(self.style.ERROR(
                    f"Directorio no encontrado: {dir_path} (tipo: {img_type})"
                ))
                return

        # Escanear archivos de todos los directorios
        files_by_type: Dict[str, Dict[str, str]] = {}
        list_by_dir: Dict[str, Dict[int, dict]] = {}
        all_stems = set()
        for img_type, dir_path in image_dirs:
            files = self._get_files(dir_path)
            files_by_type[img_type] = files
            list_by_dir[dir_path] = self._parse_list_file(dir_path)
            all_stems.update(files.keys())

        all_stems = sorted(all_stems)

        if not all_stems:
            self.stdout.write(self.style.WARNING(
                "No se encontraron archivos de imagen válidos."
            ))
            return

        category = self._get_category(category_id)
        sku_map = self._load_sku_map()

        existing_slugs = set(
            ProductTranslation.objects
            .filter(language="es", slug__in=[self._slug(s) for s in all_stems])
            .values_list("slug", flat=True)
        )

        stems_to_import = [s for s in all_stems if self._slug(s) not in existing_slugs]

        if stems_to_import:
            created = 0
            errors = []

            with transaction.atomic():
                for stem in stems_to_import:
                    try:
                        self._create_product(
                            stem=stem,
                            files_by_type=files_by_type,
                            image_dirs=image_dirs,
                            category=category,
                            sku_map=sku_map,
                            list_by_dir=list_by_dir,
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

    def _parse_dirs(
        self, raw_dirs: Optional[List[str]], category_id: int
    ) -> List[Tuple[str, str]]:
        if raw_dirs:
            result = []
            for entry in raw_dirs:
                if ":" not in entry:
                    self.stderr.write(self.style.ERROR(
                        f"Formato inválido: '{entry}'. Usa TYPE:PATH (ej: KEYCHAIN:/Recursos/img-religion)"
                    ))
                    return []
                img_type, path = entry.split(":", 1)
                result.append((img_type.upper(), path))
            return result
        return self.DEFAULT_DIRS.get(str(category_id), [])

    def _get_category(self, category_id: int):
        if category_id == 1:
            return CategoryService.get_or_create_mascotas_category()
        from apps.catalog.categories.models import Category
        category, _ = Category.objects.get_or_create(
            id=category_id,
            defaults={"active": True},
        )
        return category

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

    def _find_list_file(self, image_dir: str) -> Optional[str]:
        for f in os.listdir(image_dir):
            if os.path.isfile(os.path.join(image_dir, f)):
                if os.path.splitext(f)[0].lower().startswith("lista"):
                    return os.path.join(image_dir, f)
        return None

    def _parse_list_file(self, image_dir: str) -> Dict[int, dict]:
        entries: Dict[int, dict] = {}
        list_path = self._find_list_file(image_dir)
        if not list_path:
            return entries
        with open(list_path, encoding="utf-8") as fh:
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
                price = None
                price_match = re.search(r"(\d[\d.,]*)", price_part)
                if price_match:
                    parsed = re.sub(r"[^\d]", "", price_match.group(1))
                    if parsed:
                        price = int(parsed)
                name = re.split(r"\s*\(", desc, maxsplit=1)[0].strip().rstrip(".") or desc
                entries.setdefault(index if index != -1 else line_no, {
                    "price": price,
                    "name": name,
                    "description": desc,
                })
        return entries

    def _image_index(self, stem: str) -> int:
        match = re.match(r"^\s*(\d+)", stem)
        return int(match.group(1)) if match else -1

    def _generate_sku(self) -> str:
        last = (
            Product.objects
            .filter(sku__startswith="KEY-")
            .order_by("-sku")
            .values_list("sku", flat=True)
            .first()
        )
        if last:
            num = int(last.split("-")[1]) + 1
        else:
            num = 1
        return f"KEY-{num:06d}"

    def _load_sku_map(self) -> Dict[str, str]:
        products_json = os.path.join(settings.BASE_DIR, "docs", "products.json")
        if not os.path.exists(products_json):
            self.stdout.write(self.style.WARNING(
                f"products.json no encontrado: {products_json}, se generarán SKUs automáticos."
            ))
            return {}
        with open(products_json) as f:
            data = json.load(f)
        return {
            p["translations"]["es"]["slug"]: p["sku"]
            for p in data
            if "translations" in p and "es" in p["translations"]
        }

    def _translation_data(self, name: str, slug: str, description: Optional[str] = None) -> dict:
        if description:
            desc = {
                "name": name,
                "slug": slug,
                "short_description": description,
                "story": description,
                "seo_title": name,
                "seo_description": description,
            }
            return {lang: dict(desc) for lang in ("es", "en", "pt", "fr")}
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
        files_by_type: Dict[str, Dict[str, str]],
        image_dirs: List[Tuple[str, str]],
        category,
        sku_map: Dict[str, str],
        list_by_dir: Dict[str, Dict[int, dict]] = None,
    ):
        list_by_dir = list_by_dir or {}
        # Find first available file for naming
        first_file = None
        first_dir = None
        for img_type, dir_path in image_dirs:
            if stem in files_by_type.get(img_type, {}):
                first_file = files_by_type[img_type][stem]
                first_dir = dir_path
                break
        if not first_file:
            return

        entry = list_by_dir.get(first_dir, {}).get(self._image_index(stem))

        if entry:
            product_name = entry["name"]
            description = entry["description"]
            price = entry["price"]
        else:
            product_name = self._product_name(first_file)
            description = None
            price = None

        slug = self._slug(stem)
        sku = sku_map.get(slug, self._generate_sku())

        if not price:
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

        for lang, name_translated in self._translation_data(product_name, slug, description).items():
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

        sort_order = 0
        for img_type, dir_path in image_dirs:
            filename = files_by_type.get(img_type, {}).get(stem)
            if not filename:
                continue
            path = os.path.join(dir_path, filename)
            img_file = self._open_and_resize(path, filename)
            img = ProductImage.objects.create(
                product=product,
                type=img_type,
                sort_order=sort_order,
            )
            img.image.save(filename, img_file, save=True)
            img_file.close()
            self._generate_thumbnails(img)
            sort_order += 1
