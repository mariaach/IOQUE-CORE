#!/bin/bash
set -e

echo "=== IOQUE Catalog - Inicialización ==="

echo "1. Ejecutando migraciones..."
python manage.py migrate --noinput

echo "2. Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "3. Creando superusuario (si no existe)..."
python manage.py createsuperuser --noinput 2>/dev/null || echo "   Superusuario ya existe o saltado"

echo "4. Importando productos..."
python manage.py import_products

echo "=== Inicialización completada ==="
