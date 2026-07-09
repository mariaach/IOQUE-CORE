# Docker

## Servicios

### postgres
- Imagen: `postgres:16-alpine`
- Puerto: `5432`
- Volumen: `postgres_data` (persistente)
- Healthcheck cada 10s

### django
- Build: Dockerfile multicapa (builder + runtime)
- Puerto: `8000` (expuesto internamente)
- Volúmenes: `media_volume`, `static_volume`
- Depende de: postgres (healthcheck)
- Comando: migrate + collectstatic + gunicorn

### nginx
- Imagen: `nginx:alpine`
- Puerto: `80`
- Volúmenes: config nginx, static_volume (ro), media_volume (ro)
- Depende de: django

## Volúmenes

| Volumen | Propósito |
|---------|-----------|
| postgres_data | Datos persistentes de PostgreSQL |
| media_volume | Imágenes subidas por usuarios |
| static_volume | Archivos estáticos recolectados |

## Construcción

```bash
docker compose up --build
```

Para ejecutar en background:

```bash
docker compose up --build -d
```

## Comandos Útiles

```bash
# Ver logs
docker compose logs -f django

# Ejecutar comando en el contenedor django
docker compose exec django python manage.py <comando>

# Detener servicios
docker compose down

# Detener y eliminar volúmenes
docker compose down -v

# Reconstruir sin cache
docker compose build --no-cache django
```
