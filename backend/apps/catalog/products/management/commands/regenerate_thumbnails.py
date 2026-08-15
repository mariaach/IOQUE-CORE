from django.core.management.base import BaseCommand

from apps.catalog.products.models import ProductImage


class Command(BaseCommand):
    help = (
        "Pre-genera (o verifica) los thumbnails y mediums de todas las "
        " imágenes de producto sobre el storage, evitando la generación "
        " perezosa dentro del request HTTP."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--category",
            type=int,
            default=None,
            help="Limitar a una categoría de producto (por defecto: todas).",
        )

    def handle(self, *args, **options):
        category_id = options.get("category")
        queryset = ProductImage.objects.all()
        if category_id is not None:
            queryset = queryset.filter(product__category_id=category_id)

        total = queryset.count()
        self.stdout.write(f"Verificando/{'generando'} thumbnails de {total} imágenes...")

        errors = 0
        generated_or_ok = 0
        for img in queryset.iterator():
            for size_attr in ("image_thumbnail", "image_medium"):
                try:
                    getattr(img, size_attr).generate()
                    generated_or_ok += 1
                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f"  Error generando {size_attr} para imagen {img.id}: {e}"
                        )
                    )

        if errors:
            self.stdout.write(
                self.style.WARNING(
                    f"Thumbnails listos (con {errors} errores). Variantes OK/verificadas: {generated_or_ok}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Thumbnails listos. Variantes OK/verificadas: {generated_or_ok}"
                )
            )