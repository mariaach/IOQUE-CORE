# CONTEXTO DE TRABAJO — IOQUE + MVP-Antirobo

Documento de handoff para continuar en otro equipo. Fecha: 2026-08-17.

---

## 1) IOQUE-CORE — Tienda online de llaveros de mascotas

### Datos generales
- **Ruta local:** `/home/bayron/Documents/PROYECTOS/IOQUE/IOQUE-CORE`
- **Git:** `https://github.com/mariaach/IOQUE-CORE.git` — rama **`feature/02-pay-tmp`** — HEAD `1d9be27` (todo commiteado y pusheado)
- **Stack:** Django (apps: `catalog`, `orders`, `payments`, `contact`) · PostgreSQL 16 · nginx · **R2 de Cloudflare** (API S3) para imágenes · Tailscale
- **Imágenes servidas** desde `https://media.ioqueartesanias.com` (dominio R2 → CDN Cloudflare)
- **URL pública:** `https://ioqueartesanias.com` / `132.145.204.8`
- **Contenedores locales (compose `docker-compose.yml`):** `ioque_postgres`, `ioque_django`, `ioque_nginx`, `ioque_backup`

### Configuración clave (en `backend/config/settings.py`)
- Envío **incluido**: `DEFAULT_SHIPPING_COST=0`; descuento **$15.000** por producto adicional (>2)
- Precios $37.500–$39.500 COP · **stock de los 51 productos = 10**
- **Nequi:** `NEQUI_PAYMENT_MODE=static` (QR fijo). El proveedor dinámico (`apps/payments/providers.py` → `NequiDynamicProvider`) está **completado** (teléfono `3216153977`, extrae qrCode base64) pero las credenciales en `.env` son **placeholders** → falta activarlo.
- **Frontend versionado:** `app.js?v=17`, `style.css?v=13`
  - Flujo de pago con **WhatsApp** tras escanear el QR (`sendOrderWhatsApp()`, `WHATSAPP_NUMBER='573177695006'`)
  - Botón cancelar → **«Regresar al catálogo»**
  - **QR a 264px** (antes 176px), espaciado reducido
  - QR real del negocio: `NEQUI_QR_IMAGE='/static/img/qr-ioque.png'`

### `.env` (IMPORTANTE copiar a la máquina nueva — son secretos, están en `.gitignore`)
Claves de `IOQUE-CORE/.env`: `DJANGO_SECRET_KEY DJANGO_DEBUG DJANGO_ALLOWED_HOSTS CSRF_TRUSTED_ORIGINS DJANGO_LANGUAGE_CODE DJANGO_TIMEZONE POSTGRES_DB POSTGRES_USER POSTGRES_PASSWORD POSTGRES_HOST POSTGRES_PORT JWT_* DJANGO_SUPERUSER_* AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_STORAGE_BUCKET_NAME AWS_DEFAULT_ACL AWS_QUERYSTRING_AUTH NEQUI_CLIENT_ID NEQUI_CLIENT_SECRET NEQUI_API_KEY NEQUI_MERCHANT_CODE NEQUI_AUTH_URI NEQUI_API_BASE_PATH NEQUI_NOTIFICATION_URL NEQUI_STATIC_QR_URL NEQUI_MERCHANT_PHONE`

### Servidor de producción `132.145.204.8` (Oracle Cloud)
- **Acceso SSH:**
  ```
  sudo ssh -i /home/bayron/Documents/CLOUD/OracleCloud/ssh-key-2026-07-18.key ubuntu@132.145.204.8
  ```
- **Despliegue:** repo clonado en `/home/ubuntu/IOQUE/core` (rama `feature/02-pay-tmp`)
- **Contenedores:** `ioque_django`, `ioque_nginx`, `ioque_postgres`
- ⚠️ **`/Recursos`** en el servidor es un **symlink** a `/home/ubuntu/IOQUE/Recursos` (el compose apunta a la ruta local inexistente `/home/bayron/...`; el symlink la resuelve). No borrar.
- **Deploy normal (tras `git pull`):**
  ```
  docker compose up -d --build
  docker compose exec django python manage.py migrate --noinput
  docker compose exec django python manage.py collectstatic --noinput
  ```
- **Hot-deploy sin rebuild** (solo archivos sueltos: app.js/css/index.html):
  ```
  docker cp backend/static/js/app.js ioque_django:/app/static/js/app.js
  docker exec -w /app ioque_django python manage.py collectstatic --noinput
  docker exec -w /app ioque_django python -c "import os, signal; os.kill(1, signal.SIGHUP)"
  ```
- ⚠️ **Un `docker compose up -d --force-recreate` SIN `--build` pierde los archivos copiados con `docker cp`** (viven en la capa writable). El rebuild los hornea.

### Base de datos
- Local y servidor usan: db **`ioque_catalog`**, usuario **`ioque`** (postgres 16)
- **Exportar local:**
  ```
  docker exec ioque_postgres sh -c 'pg_dump -U ioque -d ioque_catalog --no-owner --no-privileges' > ioque_backup_$(date +%Y%m%d).sql
  ```
- **Restaurar en el servidor** (reemplaza la BD):
  ```
  cd /home/ubuntu/IOQUE/core
  docker exec -i ioque_postgres sh -c 'psql -U ioque -d postgres -c "DROP DATABASE IF EXISTS ioque_catalog WITH (FORCE);" -c "CREATE DATABASE ioque_catalog OWNER ioque;"'
  docker exec -i ioque_postgres sh -c 'psql -U ioque -d ioque_catalog' < ioque_backup_YYYYMMDD.sql
  ```
- **Último backup:** `/home/bayron/Documents/PROYECTOS/IOQUE/ioque_backup_20260816.sql` (también copiado a `/home/ubuntu/IOQUE/` en el servidor).

### Comandos útiles (dentro del contenedor django)
- `python manage.py import_products` → idempotente (solo crea por slug, no sobrescribe)
- `python manage.py sync_product_images --check` → previsualiza imágenes que difieren/ faltan en R2
- `python manage.py sync_product_images` → **corregir imágenes de mascotas** (sube desde `/Recursos/img-breeds` e `img-keychain`, purga caché, regenera thumbnails)
- `python manage.py regenerate_thumbnails`
- Tests: 23 en `apps.orders` (`manage.py test apps.orders`)

### Cambios recientes (resumen)
- Flujo de pago con WhatsApp (carrito + comprobante de pago en mensaje), QR real del negocio, botón cancelar «Regresar al catálogo», QR 264px.
- nginx (`docker/nginx/default.conf`): **sin `proxy_cache` en `/api/`** (causaba ids obsoletos y 400 tras restaurar la BD) y CSP con `https://static.cloudflareinsights.com`.
- stock=10, botón cancelar dorado visible, entrypoint con regeneración de thumbnails en background.
- `docker/entrypoint.sh`: eliminado `create_superuser` duplicado; thumbnails en background.

### Pendientes IOQUE
1. **Nequi real:** conseguir credenciales reales de Nequi Conecta; en `.env` fijar `NEQUI_PAYMENT_MODE=dynamic`, `NEQUI_CLIENT_ID/SECRET/API_KEY/MERCHANT_CODE`, y `NEQUI_NOTIFICATION_URL` real (`https://tudominio.com/api/payments/nequi-webhook/`). Recrear contenedor con rebuild tras cambiar `.env`.
2. **Limpiar pedidos de prueba:** la BD del servidor (restaurada desde local) tiene ~19 órdenes (`IOQUE-20260815-0001..0006` etc., PENDING_PAYMENT).
3. Nada pendiente de commit local (árbol limpio, pusheado).

---

## 2) MVP-Antirobo — Detección de robos en almacenes

### Datos generales
- **Ruta local:** `/home/bayron/Documents/PROYECTOS/MVP-Antirobo` (aún **sin git**)
- **Stack:** Python 3.11 · OpenCV · **YOLOv8 nano** (ultralytics) · **MediaPipe fijado a `0.10.14`** · FastAPI/Uvicorn · httpx (Telegram)
- **Estructura:** `app/{config, ingestion, ai, services, api, notifications}`, `main.py`, `Dockerfile` (multi-stage), `docker-compose.yml`
- **Pipeline multihilo:** captura → inferencia (YOLO+pose) → grabador de clips → notificador Telegram. Búfer circular JPEG (10 s antes + 5 s después) → MP4 en `./media/alerts/`
- **Endpoints:** `/` (dashboard), `/status`, `/alerts`, `/alerts/{id}`, `/alerts/{id}/snapshot`, `/alerts/{id}/clip`, `/stream` (MJPEG), `/ws`

### Estado actual
- **Imagen `antirobo-mvp:latest` = `docker commit`** (se instaló mediapipe 0.10.14 en un contenedor y se committeó). **No es reproducible desde el Dockerfile todavía**, pero `requirements.txt` ya fija `mediapipe==0.10.14`, así que un futuro `docker compose up -d --build` quedará bien.
- Fix aplicados: `app/ai/pose_analyzer.py` (import explícito de `mp.solutions`), `app/ingestion/source.py` (`VideoSource.start()` ya no derriba el proceso si la fuente no abre, reintenta en background).
- Verificado: `/status` → 200, `detector: true`, `pose: true`.
- **Causa del crash anterior:** mediapipe ≥0.10.21 y 1.x eliminaron la API legacy `mp.solutions`.

### `.env` (copiar a la máquina nueva; si inicializan git, agregar `.env` al `.gitignore`)
Claves de `MVP-Antirobo/.env`: `RTSP_URL VIDEO_WIDTH VIDEO_HEIGHT VIDEO_LOOP PROCESS_FPS MODEL_PATH CONFIDENCE_THRESHOLD DEVICE PERSON_ONLY POSE_ANALYSIS_ENABLED POSE_MIN_CONFIDENCE BEHAVIOR_CONSECUTIVE_FRAMES HAND_POCKET_RATIO HAND_JACKET_RATIO ALERT_COOLDOWN_SECONDS BUFFER_SECONDS_BEFORE BUFFER_SECONDS_AFTER MAX_ALERTS_MEMORY SAVE_ALERT_CLIPS SAVE_ALERT_SNAPSHOT CLIP_OUTPUT_DIR MAX_CLIPS_RETAINED TELEGRAM_ENABLED TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID TELEGRAM_SEND_CLIP API_HOST API_PORT MJEPG_FPS LOG_LEVEL`

### Cómo levantar
```bash
cd /home/bayron/Documents/PROYECTOS/MVP-Antirobo
# Fuente de video: RTSP_URL=0 (webcam) NO funciona dentro de Docker.
# Usar video local: RTSP_URL=./media/test.mp4 y VIDEO_LOOP=true, o una URL RTSP real.
docker compose up -d --build
curl http://localhost:8000/status
# Dashboard: http://localhost:8000/
```
Sin Docker (webcam): `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py`

### Notas
- GPU no configurada: `DEVICE=auto` → CPU. Para GPU NVIDIA: instalar nvidia-container-toolkit, descomentar `gpus: all` en compose, `DEVICE=cuda:0`.
- Si el puerto 8000 está ocupado, cambiar el mapeo en `docker-compose.yml`.

---

## 3) Para continuar en otra máquina
1. Copiar los `.env` de ambos proyectos (contienen secretos: R2, Nequi, Telegram, Postgres).
2. Copiar la **llave SSH del servidor** `/home/bayron/Documents/CLOUD/OracleCloud/ssh-key-2026-07-18.key` (y el archivo `~/.ssh/config` si se usa).
3. `git clone` IOQUE-CORE desde GitHub (rama `feature/02-pay-tmp`) y levantar con `docker compose up -d --build`.
4. MVP-Antirobo: copiar la carpeta (o inicializar git) + `.env` + `docker compose up -d --build`.
5. Este archivo `CONTEXTO.md` resume todo el estado, comandos y pendientes.

## 4) Seguridad
- NO commitear `.env`, llaves SSH, ni datos de acceso. `.gitignore` de IOQUE ya excluye `.env`; MVP-Antirobo debe agregarlo si se inicializa git.
- Las credenciales Nequi/R2/Telegram/Postgres viven solo en los `.env` locales y del servidor.
