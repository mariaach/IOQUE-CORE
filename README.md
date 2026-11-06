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

La API de catálogo es **pública y de solo lectura**: no requiere token.
La gestión de datos se hace desde el panel de administración (`/admin/`).

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

## Pedidos y Pagos con QR Nequi

Flujo completo de compra: el cliente agrega productos al carrito, crea un pedido y paga escaneando un QR con Nequi.

### Endpoints de pedidos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/orders/` | Crear pedido. Body: `{"items": [{"product_id": 1, "quantity": 2}], "idempotency_key": "..."}` |
| GET | `/api/orders/{order_number}/payment/status/` | Consultar estado del pago (requiere token) |
| POST | `/api/orders/{order_number}/payment/nequi/` | Generar QR de pago para el pedido (requiere token) |

La creación del pedido devuelve `access_token`, un token firmado y con caducidad (30 días por defecto). Los endpoints de estado y QR lo exigen en la cabecera `X-Order-Token` (o `?token=`); sin él responden `403`. Así el número de pedido, que es corto y predecible, no permite consultar pedidos ajenos.

Seguridad de precios: el backend calcula siempre el subtotal, envío y total desde la base de datos (`Product.price`). El frontend solo envía `product_id` y `quantity`; nunca confía en el precio del navegador. El stock se descuenta al crear el pedido dentro de la misma transacción que valida la disponibilidad.

Envío incluido: no se cobra envío adicional (`DEFAULT_SHIPPING_COST=0`). Si la cantidad total de productos supera `SHIPPING_DISCOUNT_THRESHOLD` (2), se descuenta `SHIPPING_DISCOUNT_PER_EXTRA` (15000 COP) del total por cada producto adicional.

### Estados del pedido y del pago

- **Order**: `PENDING_PAYMENT` → `PAYMENT_PROCESSING` → `PAID` · `PAYMENT_FAILED` · `PAYMENT_EXPIRED` · `CANCELLED` · `REFUNDED` · `COMPLETED`
- **PaymentTransaction**: `CREATED` → `QR_GENERATED` → `PENDING` → `APPROVED` · `REJECTED` · `EXPIRED` · `CANCELLED` · `REVERSED` · `ERROR`

El pedido y la transacción se crean en una única transacción de base de datos con validación de stock. Un doble clic en "pagar" devuelve la misma transacción (idempotencia).

### Modos de pago Nequi

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `NEQUI_PAYMENT_MODE` | `static` | QR fijo del negocio (`NEQUI_STATIC_QR_URL`). Listo para producción sin credenciales. |
| `NEQUI_PAYMENT_MODE` | `dynamic` | QR por transacción vía API oficial (requiere credenciales QA/sandbox). |

- **Modo estático**: se muestra la imagen QR configurada en `NEQUI_STATIC_QR_URL`. No depende de la API de Nequi.
- **Modo dinámico**: preparado en `NequiDynamicProvider`; requiere credenciales de `docs.conecta.nequi.com.co` (auth AWS-Sv4 + API Key) y pruebas en la app sandbox de Nequi.

### Variables de entorno (`.env`)

```
NEQUI_ENABLED=True
NEQUI_ENVIRONMENT=sandbox
NEQUI_PAYMENT_MODE=static
NEQUI_CLIENT_ID=...
NEQUI_CLIENT_SECRET=...
NEQUI_API_KEY=...
NEQUI_MERCHANT_CODE=...
NEQUI_AUTH_URI=https://oauth.sandbox.nequi.com/token
NEQUI_API_BASE_PATH=https://api.sandbox.nequi.com/payments/v2
NEQUI_NOTIFICATION_URL=https://tudominio.com/api/payments/nequi-webhook/?token=<NEQUI_WEBHOOK_SECRET>
NEQUI_WEBHOOK_SECRET=<secreto-largo-y-aleatorio>
NEQUI_STATIC_QR_URL=https://tudominio.com/media/qr-nequi.png
NEQUI_BUSINESS_NAME=IO QUE Artesanías
NEQUI_PAYMENT_EXPIRATION_MINUTES=15
```

### Confirmación del pago

- **Polling**: el frontend consulta `payment/status/` cada 5s y se detiene en estados terminales (`APPROVED`, `REJECTED`, `EXPIRED`, `CANCELLED`, `ERROR`). El frontend **nunca** confirma un pago: solo lee el estado.
- **Webhook**: `POST /api/payments/nequi-webhook/` valida la firma y actualiza el pedido; si la API no notifica, el polling con `getStatusPayment` es la fuente de verdad.
  - Firma HMAC-SHA256 del cuerpo en `X-Nequi-Signature` (hex o `sha256=<hex>`), o `?token=<NEQUI_WEBHOOK_SECRET>`.
  - Si `NEQUI_WEBHOOK_SECRET` está vacío, el endpoint responde `503`: nunca queda abierto.
  - Los endpoints legados `/api/payments/nequi-pay/` y `/api/payments/nequi-status/` fueron eliminados (ahora `404`).

### Tests

```bash
docker compose exec django python manage.py test apps.orders apps.catalog.products --noinput
```

Cubren: creación de pedido, cálculo de totales desde BD, snapshot de OrderItems, idempotencia, validación y descuento de stock, QR estático, aprobado/rechazado/expirado, doble pago, tokens de pedido, firma del webhook y validaciones SSRF/rutas locales.

### Notas de seguridad y despliegue

- `DJANGO_DEBUG=False` en producción. Con `DEBUG=True` Django expone trazas y detalles internos.
- nginx conserva `X-Forwarded-Proto=https` cuando Cloudflare termina TLS (`map $http_x_forwarded_proto`). Si el origen también atiende HTTP directo por IP, deja `SECURE_SSL_REDIRECT=False`; actívalo solo cuando todo el tráfico llegue por HTTPS.
- PostgreSQL se publica únicamente en `127.0.0.1:5432`, no en todas las interfaces.
- `.env` debe tener permisos `600` y no se versiona (solo `.env.example`).
- El admin de imágenes solo descarga URLs públicas HTTP(S) en puertos 80/443, con límite de tamaño y redirecciones, y solo lee archivos de imagen dentro de `/Recursos`. El contenido se valida con Pillow (JPEG/PNG/WebP).

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

# Verificar/regenerar miniaturas y versiones medianas (ImageKit -> R2)
docker compose exec django python manage.py regenerate_thumbnails
```

### Imágenes que devuelven 404 en `/CACHE/images/...`

Las URLs `CACHE/images/...` las genera ImageKit. Con la estrategia `Optimistic`
el archivo **no** se crea al pedir la URL: se genera al guardar la imagen. Si se
borra la caché del SKU sin regenerarla, la URL queda en 404 aunque la imagen
original exista.

Para repararlo:

```bash
docker compose exec django python manage.py regenerate_thumbnails
```

No borres manualmente `CACHE/images/products/<SKU>/`; para invalidar una imagen
usa el panel de administración o `sync_product_images`, que regeneran todas las
variantes del producto.



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