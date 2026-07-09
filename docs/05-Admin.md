# Administrador Django

## Acceso

URL: http://localhost/admin/

## Funcionalidades

### Categorías (CategoryAdmin)

| Característica | Descripción |
|----------------|-------------|
| Listado | Nombre, activo, cantidad de productos, fecha |
| Filtros | Activo, fecha de creación |
| Búsqueda | Por nombre de traducción |
| Inline | Traducciones (hasta 4 idiomas) |
| Acciones | Activar/desactivar masivamente |

### Productos (ProductAdmin)

| Característica | Descripción |
|----------------|-------------|
| Listado | SKU, nombre, categoría, precio, stock, destacado, activo, thumbnail, fecha |
| Filtros | Activo, destacado, categoría, fecha, idioma |
| Búsqueda | SKU, nombre, descripción corta |
| Inline | Traducciones + imágenes con vista previa |
| Edición rápida | Precio, stock, destacado, activo (desde listado) |
| Acciones | Activar, desactivar, marcar/desmarcar destacado |

### Vistas previas

Las imágenes se muestran directamente en el admin:
- **Listado**: Thumbnail de 50x50px
- **Inline**: Previsualización de 100x100px

### Roles y Permisos

Utilizar el sistema de permisos de Django:

1. **Staff**: Acceso al admin
2. **Superuser**: Acceso total
3. **Grupos**: Crear grupos con permisos específicos
   - Editores: pueden agregar/editar productos
   - Consultores: solo lectura
