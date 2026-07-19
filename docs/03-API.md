# API REST

## Base URL

```
http://localhost/api/
```

## Autenticación

La API de catálogo es **pública y de solo lectura** (`AllowAny`). No requiere
token para consultar productos, categorías ni el widget de contacto.

La escritura de datos (crear/editar productos, categorías, etc.) se realiza
desde el **panel de administración de Django** (`/admin/`), que usa autenticación
por sesión.

> Nota: no hay autenticación JWT ni endpoints `/api/token/`. Si en el futuro se
> requiere una API de escritura autenticada, se puede añadir
> `djangorestframework-simplejwt` y exponer las rutas correspondientes.

## Permisos

| Rol | Acceso API |
|-----|-----------|
| Anónimo | Lectura (público) |
| Admin (sesión) | Escritura vía `/admin/` |

## Límites de tasa (throttling)

La API aplica throttling por defecto:
- Anónimo: `60/minute`
- Autenticado: `120/minute`

Configurable con las variables `DRF_THROTTLE_ANON` y `DRF_THROTTLE_USER`.

## Endpoints

### Categorías

#### GET /api/categories/

Lista todas las categorías activas.

**Parámetros query:**
- `language` (opcional): Idioma para traducciones (es, en, pt, fr). Default: es
- `search`: Búsqueda por nombre
- `page`: Número de página
- `page_size`: Tamaño de página

**Respuesta:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Perros",
      "description": "",
      "product_count": 0,
      "active": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/categories/{id}/

Detalle de categoría con todas las traducciones.

### Productos

#### GET /api/products/

Lista todos los productos activos.

**Parámetros query:**
- `language` (opcional): Idioma (es, en, pt, fr). Default: es
- `featured`: Filtrar destacados (true/false)
- `category`: ID de categoría
- `min_price`: Precio mínimo
- `max_price`: Precio máximo
- `in_stock`: Solo en stock (true/false)
- `search`: Búsqueda por nombre, SKU, descripción
- `ordering`: Ordenar por campo (price, -price, created_at, -created_at, name)
- `page`: Número de página
- `page_size`: Tamaño de página

**Respuesta:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "sku": "KEY-000001",
      "name": "Golden Retriever",
      "slug": "golden-retriever",
      "short_description": "",
      "category_name": "Perros",
      "price": "0.00",
      "stock": 1,
      "featured": false,
      "images": [
        {
          "id": 1,
          "url": "/media/products/KEY-000001/real_0.jpg",
          "type": "REAL",
          "sort_order": 0
        }
      ],
      "image_thumbnail": "/media/products/KEY-000001/real_0.jpg",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### GET /api/products/{id}/

Detalle completo del producto con todas las traducciones e imágenes.

#### GET /api/products/search/?q=...

Busca productos por nombre.

**Parámetros query:**
- `q`: Término de búsqueda (requerido)
- `language`: Idioma (opcional, default: es)

## Documentación Swagger

Generada automáticamente con **drf-spectacular**. Disponible en:
- Swagger UI: http://localhost/api/docs/
- Schema OpenAPI (YAML): http://localhost/api/schema/
