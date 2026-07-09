# Floating WhatsApp Widget

Widget de WhatsApp flotante estilo Intercom/Crisp. Componente web independiente con Shadow DOM, sin dependencias externas.

## Uso

```html
<link rel="stylesheet" href="/static/whatsapp-widget/widget.css">
<script type="module" src="/static/whatsapp-widget/widget.js"></script>
```

El widget se inicializa automáticamente al cargar el script. Consume `GET /api/contact/widget/` para obtener configuración.

## Configuración desde Django Admin

`/admin/contact/whatsappwidget/`

- **Habilitado**: mostrar/ocultar widget
- **Número WhatsApp**: ej. `573177695006`
- **Color del tema**: cualquier hex (#25D366 por defecto)
- **Posición**: izquierda/derecha
- **Logo**: imagen opcional (aparece como avatar circular)
- **Campos**: mostrar/requerir Teléfono, Correo, Empresa
- **Traducciones**: ES, EN, PT, FR — títulos, mensajes, textos

## API

```
GET /api/contact/widget/
```

Respuesta: `WhatsAppWidgetSerializer` con config, traducciones y `logo_url`.

## Arquitectura

- `widget.css` — estilos Shadow DOM (cargado dentro del shadowRoot)
- `widget.js` — Custom Element `<wa-widget>`:
  - `HTMLElement` + `attachShadow({ mode: 'open' })`
  - `fetch()` a la API Django
  - Formulario con validación nativa
  - Construye URL `wa.me/<numero>?text=<mensaje>` y abre en nueva pestaña
  - Detecta idioma desde `<html lang="...">` mediante `MutationObserver`
  - Soporta tema oscuro vía `data-theme="dark"` o clase `.dark`
  - Animaciones CSS (pulse ring, slide-up/down, status blink)

## Compatibilidad

- ES Module (type="module")
- Chrome, Firefox, Safari, Edge (últimas 2 versiones)
- No requiere polyfills
