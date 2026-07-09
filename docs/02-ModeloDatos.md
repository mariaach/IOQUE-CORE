# Modelo de Datos

## Diagrama de Entidades

```
┌──────────────────┐       ┌─────────────────────┐
│     Category      │       │  CategoryTranslation │
├──────────────────┤       ├─────────────────────┤
│ id               │──1:N──│ id                  │
│ active           │       │ category (FK)       │
│ created_at       │       │ language            │
│ updated_at       │       │ name                │
└──────────────────┘       │ description         │
                           └─────────────────────┘
        │ 1:N
        │
┌──────────────────┐       ┌─────────────────────┐
│     Product       │       │  ProductTranslation  │
├──────────────────┤       ├─────────────────────┤
│ id               │──1:N──│ id                  │
│ category (FK)    │       │ product (FK)        │
│ sku              │       │ language            │
│ price            │       │ name                │
│ stock            │       │ slug                │
│ featured         │       │ short_description   │
│ active           │       │ story               │
│ created_at       │       │ seo_title           │
│ updated_at       │       │ seo_description     │
└──────────────────┘       └─────────────────────┘
        │ 1:N
        │
┌──────────────────┐
│   ProductImage    │
├──────────────────┤
│ id               │
│ product (FK)     │
│ image            │
│ type             │
│ sort_order       │
│ created_at       │
└──────────────────┘
```

## Modelos

### Category (apps.catalog.categories.models)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | AutoField | Clave primaria |
| active | BooleanField | Activo/inactivo |
| created_at | DateTimeField | Fecha de creación |
| updated_at | DateTimeField | Fecha de actualización |

### CategoryTranslation

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | AutoField | Clave primaria |
| category | ForeignKey | Categoría relacionada |
| language | CharField | Código de idioma (es, en, pt, fr) |
| name | CharField | Nombre de la categoría |
| description | TextField | Descripción de la categoría |

### Product (apps.catalog.products.models)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | AutoField | Clave primaria |
| category | ForeignKey | Categoría (nullable) |
| sku | CharField | Código único (KEY-000001) |
| price | DecimalField | Precio |
| stock | PositiveIntegerField | Stock disponible |
| featured | BooleanField | Producto destacado |
| active | BooleanField | Activo/inactivo |
| created_at | DateTimeField | Fecha de creación |
| updated_at | DateTimeField | Fecha de actualización |

### ProductTranslation

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | AutoField | Clave primaria |
| product | ForeignKey | Producto relacionado |
| language | CharField | Código de idioma |
| name | CharField | Nombre del producto |
| slug | SlugField | Slug para URLs |
| short_description | TextField | Descripción corta |
| story | TextField | Historia del producto |
| seo_title | CharField | Título SEO |
| seo_description | TextField | Descripción SEO |

### ProductImage

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | AutoField | Clave primaria |
| product | ForeignKey | Producto relacionado |
| image | ImageField | Archivo de imagen |
| type | CharField | Tipo (REAL, KEYCHAIN, DETAIL, PACKAGE) |
| sort_order | PositiveIntegerField | Orden de visualización |
| created_at | DateTimeField | Fecha de creación |
