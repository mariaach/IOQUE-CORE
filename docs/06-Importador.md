# Importador Automático

## Comando

```bash
python manage.py import_products
```

## Funcionamiento

1. Lee imágenes del directorio `img-breeds/` (fotos reales)
2. Lee imágenes del directorio `img-keychain/` (fotos de llaveros)
3. Para cada nombre de archivo único (stem), crea un producto con:
   - SKU auto-generado (KEY-000001, KEY-000002...)
   - Precio: 0
   - Stock: 1
   - Categoría: "Perros" (se crea automáticamente si no existe)
   - Traducción al español con nombre, slug, SEO title
   - Imagen REAL desde img-breeds (si existe)
   - Imagen KEYCHAIN desde img-keychain (si existe)

## Reglas de Importación

### Nombres de archivo

```
golden_retriever.jpg → Producto: "Golden Retriever"
                    → Slug: "golden-retriever"
beagle.png           → Producto: "Beagle"
                    → Slug: "beagle"
```

### Formatos soportados

- .jpg / .jpeg
- .png
- .webp
- .gif

### Categoría "Perros"

Si no existe, se crea automáticamente con traducciones:

| Idioma | Nombre |
|--------|--------|
| Español | Perros |
| English | Dogs |
| Português | Cães |
| Français | Chiens |

### Traducciones

Solo se genera la traducción al español automáticamente. Las traducciones a inglés, portugués y francés quedan vacías para ser completadas posteriormente desde el admin.

### Textos generados

El importador genera textos temporales mínimos. Los campos `short_description`, `story` y `seo_description` se crean vacíos para ser editados posteriormente.

## Directorios de Origen

Las imágenes deben estar en:

```
/home/bayron/Documents/PROYECTOS/IOQUE/Recursos/img-breeds/
/home/bayron/Documents/PROYECTOS/IOQUE/Recursos/img-keychain/
```

## Ejecución en Docker

```bash
docker compose exec django python manage.py import_products
```
