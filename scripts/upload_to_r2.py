#!/usr/bin/env python3
"""
Script standalone para subir imágenes de productos a Cloudflare R2.

Uso:
  1. pip install boto3 Pillow python-dotenv psycopg2-binary
  2. Configurar variables en .env (ver .env.example)
  3. python scripts/upload_to_r2.py [--dry-run] [--force] [--extra-dir TYPE:PATH]

Ejemplo para subir imágenes de religión:
  python scripts/upload_to_r2.py --extra-dir REAL:/Recursos/img-religion

Este script NO depende de Django — opera directamente con boto3 y la DB vía psycopg2.
"""

import os
import sys
import re
import argparse
from pathlib import Path
from io import BytesIO

import boto3
from PIL import Image
from dotenv import load_dotenv

# Leer .env del directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── Config R2 ──
R2_ENDPOINT = os.getenv("AWS_S3_ENDPOINT_URL")
R2_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
R2_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("AWS_STORAGE_BUCKET_NAME")
R2_REGION = os.getenv("AWS_S3_REGION_NAME", "auto")

# ── Config DB ──
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "ioque_catalog")
DB_USER = os.getenv("POSTGRES_USER", "ioque")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")

# ── Config local ──
BREEDS_DIR = "/Recursos/img-breeds"
KEYCHAIN_DIR = "/Recursos/img-keychain"
MAX_DIM = 1200
THUMB_SIZE = (400, 400)
MEDIUM_MAX = 800

# ── Nomenclatura R2 ──
# products/{SKU}/real_0.jpg
# products/{SKU}/keychain_0.jpg
# products/{SKU}/detail_0.jpg


def get_r2_client():
    if not all([R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET]):
        print("ERROR: Faltan variables de R2 en .env")
        print("Necesitas: AWS_S3_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME")
        sys.exit(1)

    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name=R2_REGION,
    )


def get_db_connection(host=None):
    try:
        import psycopg2
        return psycopg2.connect(
            host=host or DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
    except ImportError:
        print("ERROR: psycopg2 no instalado. Ejecuta: pip install psycopg2-binary")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: No se pudo conectar a la DB: {e}")
        sys.exit(1)


def resize_image(path, max_dim=MAX_DIM):
    img = Image.open(path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    if max(img.size) > max_dim:
        img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    buf = BytesIO()
    ext = Path(path).suffix.lower()
    fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
    img.save(buf, fmt, quality=85)
    buf.seek(0)
    return buf, fmt


def generate_thumbnail(img_bytes, fmt):
    img = Image.open(img_bytes)
    img.thumbnail(THUMB_SIZE, Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, fmt, quality=85)
    buf.seek(0)
    return buf


def generate_medium(img_bytes, fmt):
    img = Image.open(img_bytes)
    if max(img.size) > MEDIUM_MAX:
        img.thumbnail((MEDIUM_MAX, MEDIUM_MAX), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, fmt, quality=90)
    buf.seek(0)
    return buf


def upload_to_r2(client, key, img_bytes, content_type="image/jpeg"):
    img_bytes.seek(0)
    client.put_object(
        Bucket=R2_BUCKET,
        Key=key,
        Body=img_bytes.read(),
        ContentType=content_type,
    )


def find_source_file(directory, name, slug):
    """Busca archivo original en Recursos por nombre o slug del producto."""
    if not os.path.isdir(directory):
        return None

    # Normalizar para comparación: quitar tildes, minúsculas
    import unicodedata
    def normalize(s):
        s = unicodedata.normalize("NFKD", s)
        s = "".join(c for c in s if not unicodedata.combining(c))
        return s.lower().replace(" ", "-").replace("_", "-")

    name_norm = normalize(name)
    slug_norm = normalize(slug)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            continue
        stem = Path(filename).stem
        stem_norm = normalize(stem)

        # Match exacto por slug o nombre
        if stem_norm == slug_norm or stem_norm == name_norm:
            return filepath

        # Match parcial: slug contenido en el filename
        if slug_norm and slug_norm in stem_norm:
            return filepath

        # Match por nombre sin número prefijo (ej: "pug" en "1-pug")
        stem_clean = re.sub(r"^\d+-", "", stem_norm)
        if stem_clean == slug_norm or stem_clean == name_norm:
            return filepath

    return None


def get_products_from_db(conn):
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.sku,
               pt_es.name as name_es,
               pt_es.slug as slug_es,
               pi.type as img_type,
               pi.sort_order,
               pi.image
        FROM catalog_products_product p
        JOIN catalog_products_producttranslation pt_es ON pt_es.product_id = p.id AND pt_es.language = 'es'
        LEFT JOIN catalog_products_productimage pi ON pi.product_id = p.id
        WHERE p.active = true
        ORDER BY p.id, pi.sort_order
    """)
    return cur.fetchall()


def main():
    parser = argparse.ArgumentParser(description="Subir imágenes de productos a R2")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar qué se subiría sin hacer cambios")
    parser.add_argument("--force", action="store_true", help="Re-subir aunque exista en R2")
    parser.add_argument("--breeds-dir", default=BREEDS_DIR, help="Directorio de imágenes de razas")
    parser.add_argument("--keychain-dir", default=KEYCHAIN_DIR, help="Directorio de imágenes de llaveros")
    parser.add_argument("--extra-dir", action="append", dest="extra_dirs", metavar="TYPE:PATH",
                        help="Directorio adicional como TYPE:PATH (ej: REAL:/Recursos/img-religion). Puede repetirse.")
    parser.add_argument("--db-host", default=DB_HOST, help="Host de PostgreSQL")
    args = parser.parse_args()

    # Construir mapa tipo→directorios
    type_dirs = {
        "REAL": args.breeds_dir,
        "KEYCHAIN": args.keychain_dir,
    }
    if args.extra_dirs:
        for entry in args.extra_dirs:
            if ":" not in entry:
                print(f"ERROR: Formato inválido: '{entry}'. Usa TYPE:PATH")
                sys.exit(1)
            img_type, path = entry.split(":", 1)
            type_dirs[img_type.upper()] = path

    print(f"Directorios: {type_dirs}")

    print("Conectando a R2...")
    s3 = get_r2_client()

    print("Conectando a la DB...")
    conn = get_db_connection(args.db_host)

    products = get_products_from_db(conn)
    print(f"Encontrados {len(products)} registros de imágenes en la DB")

    uploaded = 0
    skipped = 0
    errors = 0

    for row in products:
        product_id, sku, name_es, slug_es, img_type, sort_order, image_path = row

        if not img_type or not image_path:
            continue

        local_dir = type_dirs.get(img_type)
        if not local_dir:
            print(f"  WARN: {sku} - {name_es} [{img_type}] no hay directorio configurado para tipo '{img_type}'")
            errors += 1
            continue

        ext = Path(image_path).suffix.lower() or ".jpg"
        r2_key = f"products/{sku}/{img_type.lower()}_{sort_order}{ext}"

        # Buscar archivo original en Recursos por nombre del producto
        local_path = find_source_file(local_dir, name_es, slug_es)
        if not local_path:
            print(f"  WARN: {sku} - {name_es} [{img_type}] archivo no encontrado en {local_dir}")
            errors += 1
            continue

        # Verificar si ya existe en R2
        if not args.force:
            try:
                s3.head_object(Bucket=R2_BUCKET, Key=r2_key)
                skipped += 1
                continue
            except s3.exceptions.ClientError:
                pass

        if args.dry_run:
            print(f"  [DRY-RUN] {local_path} → r2://{R2_BUCKET}/{r2_key}")
            uploaded += 1
            continue

        try:
            # Redimensionar imagen original
            img_bytes, fmt = resize_image(local_path)
            content_type = "image/jpeg" if fmt == "JPEG" else "image/png"

            # Subir imagen original
            upload_to_r2(s3, r2_key, img_bytes, content_type)

            # Generar y subir thumbnail
            thumb_key = f"CACHE/images/{sku}/{img_type.lower()}_{sort_order}/thumb_{sort_order}.jpg"
            thumb_bytes = generate_thumbnail(img_bytes, "JPEG")
            upload_to_r2(s3, thumb_key, thumb_bytes, "image/jpeg")

            # Generar y subir medium
            medium_key = f"CACHE/images/{sku}/{img_type.lower()}_{sort_order}/medium_{sort_order}.jpg"
            medium_bytes = generate_medium(img_bytes, "JPEG")
            upload_to_r2(s3, medium_key, medium_bytes, "image/jpeg")

            uploaded += 1
            print(f"  OK: {sku} - {name_es} [{img_type}] → {r2_key}")

        except Exception as e:
            errors += 1
            print(f"  ERROR: {sku} - {name_es}: {e}")

    conn.close()

    print(f"\n{'Análisis' if args.dry_run else 'Subida'} completada:")
    print(f"  {uploaded} subidas")
    print(f"  {skipped} ya existían en R2")
    print(f"  {errors} errores")


if __name__ == "__main__":
    main()
