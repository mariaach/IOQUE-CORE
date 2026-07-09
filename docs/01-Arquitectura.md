# Arquitectura del Proyecto

## Visión General

IOQUE es una plataforma backend diseñada para administrar un catálogo de productos artesanales. La arquitectura sigue principios SOLID y está preparada para evolucionar hacia un e-commerce completo.

## Principios Arquitectónicos

1. **Separación por capas**: Modelos, lógica de negocio (servicios), presentación (API/Admin)
2. **Desacoplamiento**: Cada app de Django es independiente y reemplazable
3. **Preparación futura**: La arquitectura soporta la incorporación de clientes, pedidos, pagos, etc. sin cambios estructurales
4. **Multilenguaje**: Soporte nativo para múltiples idiomas mediante tablas de traducción

## Capas de la Aplicación

```
┌─────────────────────────────────────────┐
│              Nginx (proxy)              │
├─────────────────────────────────────────┤
│         Gunicorn (WSGI server)          │
├─────────────────────────────────────────┤
│           Django Application            │
│  ┌──────────┐  ┌────────────────────┐   │
│  │  Admin   │  │   REST API (DRF)   │   │
│  └──────────┘  └────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │        Service Layer             │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │         Models (ORM)             │   │
│  └──────────────────────────────────┘   │
├─────────────────────────────────────────┤
│           PostgreSQL 16                  │
└─────────────────────────────────────────┘
```

## Apps de Django

### apps.catalog.common
Modelos base abstractos (BaseModel con timestamps y active).

### apps.catalog.categories
Gestión de categorías con traducciones.

### apps.catalog.products
Gestión de productos, traducciones e imágenes.

### apps.catalog.translations
Utilidades compartidas para el sistema de traducciones.

### apps.api
Configuración de la API REST (paginación, urls principales).

## Preparación para E-commerce

Para agregar funcionalidad de e-commerce:

1. Crear nuevas apps: `apps.ecommerce.orders`, `apps.ecommerce.cart`, `apps.ecommerce.payments`
2. Extender `Product` con variantes, inventario, etc. mediante herencia o relaciones
3. Agregar servicios para lógica de negocio (carrito, pagos)
4. Agregar nuevos endpoints en `apps.api.urls`

No es necesario modificar las apps existentes del catálogo.
