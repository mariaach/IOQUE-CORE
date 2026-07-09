# Despliegue

## Producción

### Requisitos

- Servidor Linux (Ubuntu 22.04+ / Debian 12+)
- Docker y Docker Compose
- Dominio configurado (opcional)
- SSL/TLS (Certbot / Let's Encrypt)

### Pasos

1. Clonar el repositorio en el servidor
2. Copiar `.env.example` a `.env` y configurar:
   - `DJANGO_SECRET_KEY`: Generar clave segura
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=midominio.com,www.midominio.com`
   - Configurar credenciales de base de datos
3. Configurar Nginx con SSL
4. Construir y levantar:

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

### Seguridad

- Cambiar `DJANGO_SECRET_KEY` por una clave segura
- `DJANGO_DEBUG=False` en producción
- Configurar HTTPS con Certbot
- Limitar accesos por IP (firewall)
- Actualizar dependencias regularmente

### SSL con Let's Encrypt

```nginx
server {
    listen 443 ssl;
    server_name midominio.com;

    ssl_certificate /etc/letsencrypt/live/midominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/midominio.com/privkey.pem;

    location / {
        proxy_pass http://django:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/staticfiles/;
    }

    location /media/ {
        alias /app/mediafiles/;
    }
}
```

## Preparación para S3

Para migrar a Amazon S3:

1. Agregar `django-storages` a requirements
2. Configurar en settings.py:

```python
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
```

3. Agregar variables de entorno al docker-compose

## Escalado Futuro

Para agregar Celery + Redis:

```yaml
# docker-compose.yml
redis:
  image: redis:7-alpine
  restart: unless-stopped

celery:
  build: .
  command: celery -A config worker -l info
  depends_on:
    - redis
    - postgres
```

Para ElasticSearch:

```yaml
elasticsearch:
  image: elasticsearch:8
  environment:
    - discovery.type=single-node
```
