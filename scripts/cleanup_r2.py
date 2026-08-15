#!/usr/bin/env python3
"""
Elimina del R2 las imágenes de productos de mascotas (SKU KEY-*) y su caché.

Uso:
  1. Configurar variables en .env (mismas que upload_to_r2.py)
  2. python scripts/cleanup_r2.py [--dry-run] [--prefix products/KEY-]
"""
import os
import sys
import argparse
from pathlib import Path

import boto3
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

R2_ENDPOINT = os.getenv("AWS_S3_ENDPOINT_URL")
R2_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
R2_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("AWS_STORAGE_BUCKET_NAME")
R2_REGION = os.getenv("AWS_S3_REGION_NAME", "auto")


def get_r2_client():
    if not all([R2_ENDPOINT, R2_ACCESS_KEY, R2_SECRET_KEY, R2_BUCKET]):
        print("ERROR: Faltan variables de R2 en .env")
        sys.exit(1)
    return boto3.client(
        "s3",
        endpoint_url=R2_ENDPOINT,
        aws_access_key_id=R2_ACCESS_KEY,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name=R2_REGION,
    )


def list_objects(client, prefix):
    keys = []
    token = None
    while True:
        kwargs = {"Bucket": R2_BUCKET, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        page = client.list_objects_v2(**kwargs)
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
        if not page.get("IsTruncated"):
            break
        token = page.get("NextContinuationToken")
    return keys


def main():
    parser = argparse.ArgumentParser(description="Eliminar imágenes de mascotas del R2")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar qué se borraría sin borrar")
    parser.add_argument("--prefix", action="append", dest="prefixes", default=None,
                        help="Prefijo a borrar (puede repetirse). Default: products/KEY-* y CACHE de KEY-*")
    parser.add_argument("--all", action="store_true", help="Borrar TODO el bucket (peligroso)")
    args = parser.parse_args()

    s3 = get_r2_client()

    if args.all:
        prefixes = [""]
    elif args.prefixes:
        prefixes = args.prefixes
    else:
        prefixes = ["products/KEY-", "CACHE/images/KEY-", "CACHE/images/products/KEY-"]

    all_keys = set()
    for prefix in prefixes:
        keys = list_objects(s3, prefix)
        all_keys.update(keys)
        print(f"  {len(keys)} objetos con prefijo '{prefix or '(todo)'}'")

    all_keys = sorted(all_keys)
    print(f"\nTotal a borrar: {len(all_keys)} objetos")

    if args.dry_run:
        for k in all_keys[:50]:
            print(f"  [DRY-RUN] {k}")
        if len(all_keys) > 50:
            print(f"  ... y {len(all_keys) - 50} más")
        return

    # Eliminar en lotes de 1000 (límite de delete_objects)
    for i in range(0, len(all_keys), 1000):
        batch = [{"Key": k} for k in all_keys[i:i + 1000]]
        resp = s3.delete_objects(Bucket=R2_BUCKET, Delete={"Objects": batch})
        deleted = resp.get("Deleted", [])
        errors = resp.get("Errors", [])
        print(f"  Borrados {len(deleted)} objetos (lote {i // 1000 + 1})")
        for err in errors:
            print(f"  ERROR: {err}")

    print(f"\nEliminación completada: {len(all_keys)} objetos.")


if __name__ == "__main__":
    main()