#!/bin/bash
set -e

export PYTHONPATH=/app

echo "================================================"
echo "  IOQUE - Inicialización automática"
echo "================================================"

chown -R django:django /app/staticfiles /app/mediafiles 2>/dev/null || true

echo ""
echo "Waiting for PostgreSQL..."
python -c "
import time
import psycopg2
import os

for i in range(30):
    try:
        psycopg2.connect(
            dbname=os.environ['POSTGRES_DB'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'],
            port=os.environ.get('POSTGRES_PORT', '5432'),
        )
        print('PostgreSQL is ready.')
        break
    except psycopg2.OperationalError:
        if i == 29:
            print('ERROR: Could not connect to PostgreSQL after 30 attempts.')
            exit(1)
        time.sleep(1)
"

echo ""
echo "Creating migrations..."
python manage.py makemigrations catalog_categories catalog_products contact --noinput

echo ""
echo "Running migrations..."
python manage.py migrate --noinput

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "Creating default superuser..."
python scripts/create_superuser.py

echo ""
echo "Seeding categories..."
python manage.py seed_categories

echo ""
echo "Importing products..."
python manage.py import_products
python manage.py import_religion

echo ""
echo "Seeding WhatsApp widget..."
python manage.py seed_widget

echo ""
echo "================================================"
echo "  IOQUE está listo"
echo "================================================"
echo ""

exec gosu django gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --threads 4 \
  --worker-class gthread \
  --timeout 180 \
  --max-requests 200 \
  --max-requests-jitter 50 \
  --preload \
  --log-level info
