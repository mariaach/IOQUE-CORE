import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "insecure-dev-key-change-in-production")

DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Cloudflare / Reverse Proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# --- Security hardened for production ---
_INSECURE_KEYS = frozenset({
    "insecure-dev-key-change-in-production",
    "change-this-to-a-random-secret-key",
})
if not DEBUG and SECRET_KEY in _INSECURE_KEYS:
    raise RuntimeError(
        "SECRET_KEY inseguro en producción. "
        "Define DJANGO_SECRET_KEY en las variables de entorno."
    )

if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() in ("true", "1", "yes")
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "imagekit",
    # Local apps
    "apps.catalog.categories",
    "apps.catalog.products",
    "apps.catalog.translations",
    "apps.catalog.common",
    "apps.api",
    "apps.contact",
    "apps.payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "ioque_catalog"),
        "USER": os.getenv("POSTGRES_USER", "ioque"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "ioque_secret_password"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "600")),
    }
}

CACHES = {
    "default": {
        "BACKEND": os.getenv(
            "CACHE_BACKEND",
            "django.core.cache.backends.locmem.LocMemCache",
        ),
        "LOCATION": os.getenv("CACHE_LOCATION", "ioque-cache"),
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = os.getenv("DJANGO_LANGUAGE_CODE", "es")

LANGUAGES = [
    ("es", "Español"),
    ("en", "English"),
    ("pt", "Português"),
    ("fr", "Français"),
]

TIME_ZONE = os.getenv("DJANGO_TIMEZONE", "America/Mexico_City")

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]


MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

# Cloudflare R2 Storage Settings
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "auto")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN")
AWS_DEFAULT_ACL = os.getenv("AWS_DEFAULT_ACL") or None
AWS_QUERYSTRING_AUTH = os.getenv("AWS_QUERYSTRING_AUTH", "False").lower() == "true"
AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION", "s3v4")
AWS_S3_ADDRESSING_STYLE = "path"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Optimistic: genera la caché al guardar la imagen y no consulta el storage
# al acceder a .url, evitando la generación perezosa (lenta) dentro del request.
# Se debe pre-generar con regenerate_thumbnails tras importar productos.
IMAGEKIT_DEFAULT_CACHEFILE_STRATEGY = "imagekit.cachefiles.strategies.Optimistic"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Limit request body and file upload sizes (10 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:4200,http://localhost:80,http://127.0.0.1:4200",
    ).split(",")

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS",
    "http://localhost:80,http://127.0.0.1:80",
).split(",")

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
    "DEFAULT_PAGINATION_CLASS": "apps.api.pagination.StandardPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": os.getenv("DRF_THROTTLE_ANON", "60/minute"),
        "user": os.getenv("DRF_THROTTLE_USER", "120/minute"),
    },
}

SPECTACULAR_SETTINGS = {
    "TITLE": "IOQUE - API de Catálogo",
    "DESCRIPTION": "API REST del catálogo de productos artesanales de IOQUE.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

# Nequi
NEQUI_CLIENT_ID = os.getenv("NEQUI_CLIENT_ID", "")
NEQUI_CLIENT_SECRET = os.getenv("NEQUI_CLIENT_SECRET", "")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "")
NEQUI_MERCHANT_CODE = os.getenv("NEQUI_MERCHANT_CODE", "")
NEQUI_AUTH_URI = os.getenv("NEQUI_AUTH_URI", "https://oauth.sandbox.nequi.com/token")
NEQUI_API_BASE_PATH = os.getenv("NEQUI_API_BASE_PATH", "https://api.sandbox.nequi.com/payments/v2")
NEQUI_NOTIFICATION_URL = os.getenv("NEQUI_NOTIFICATION_URL", "")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
