# IOQUE - Catálogo de Productos Artesanales

Backend para administrar el catálogo de productos artesanales (llaveros personalizados) de IOQUE.

## Stack Tecnológico

- Python 3.13 / Django 5
- Django REST Framework
- PostgreSQL 16
- Docker / Docker Compose
- Nginx
- Swagger (drf-spectacular)

## Requisitos

- Docker y Docker Compose v2

## Instalación y Ejecución

### 1. Clonar y configurar

```bash
cp .env.example .env
# Editar .env si es necesario
```

### 2. Construir y levantar

```bash
docker compose up --build
```

Esto inicia los servicios:
- **PostgreSQL** en `localhost:5432`
- **Django + Gunicorn** en `localhost:8000`
- **Nginx** en `localhost:80`

### 3. Migraciones (se ejecutan automáticamente)

```bash
docker compose exec django python manage.py migrate
```

### 4. Crear superusuario

```bash
docker compose exec django python manage.py createsuperuser
```

### 5. Importar productos

```bash
docker compose exec django python manage.py import_products
```

## Acceso

| Servicio | URL |
|----------|-----|
| Admin Django | http://localhost/admin/ |
| API REST | http://localhost/api/ |
| Swagger | http://localhost/api/docs/ |
| Schema OpenAPI | http://localhost/api/schema/ |

## API REST

### Autenticación

```bash
# Obtener token
curl -X POST http://localhost/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Refrescar token
curl -X POST http://localhost/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "..."}'
```

### Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/categories/` | Listar categorías |
| GET | `/api/categories/{id}/` | Detalle de categoría |
| GET | `/api/products/` | Listar productos |
| GET | `/api/products/{id}/` | Detalle de producto |
| GET | `/api/products/search/?q=...` | Buscar productos |
| GET | `/api/products/?language=en` | Filtrar por idioma |
| GET | `/api/products/?featured=true` | Productos destacados |
| GET | `/api/products/?category=1` | Filtrar por categoría |
| GET | `/api/products/?min_price=10&max_price=50` | Filtrar por precio |
| GET | `/api/products/?in_stock=true` | Solo en stock |

### Paginación

```
/api/products/?page=2&page_size=10
```

### Ordenamiento

```
/api/products/?ordering=price
/api/products/?ordering=-created_at
/api/products/?ordering=price,-created_at
```

## Estructura del Proyecto

```
core/
├── backend/
│   ├── config/              # Configuración Django
│   ├── apps/
│   │   ├── api/             # API REST (urls, pagination)
│   │   └── catalog/
│   │       ├── categories/  # Modelo Categoría
│   │       ├── products/    # Modelo Producto
│   │       ├── translations/# Utilidades de traducción
│   │       └── common/      # Modelos base compartidos
│   ├── mediafiles/          # Imágenes subidas
│   ├── requirements/        # Dependencias
│   └── manage.py
├── docker/
│   ├── Dockerfile
│   └── nginx/
│       └── default.conf
├── docs/                    # Documentación
├── docker-compose.yml
├── .env.example
└── README.md
```

## Comandos Útiles

```bash
# Ver logs
docker compose logs -f django

# Ejecutar shell de Django
docker compose exec django python manage.py shell

# Crear migraciones
docker compose exec django python manage.py makemigrations

# Ejecutar migraciones
docker compose exec django python manage.py migrate

# Importar productos
docker compose exec django python manage.py import_products

# Recolectar estáticos
docker compose exec django python manage.py collectstatic --noinput
```



## Configurar DNS Temporal:
ESte comando se ejecuta en el Raspberry PI 3
```
curl -fsSL https://tailscale.com/install.sh | sh

sudo tailscale funnel 80

```
Arroja esta respuesta 
 Available on the internet:

https://raspberrypi.tail8dbae4.ts.net/
|-- proxy http://127.0.0.1:80