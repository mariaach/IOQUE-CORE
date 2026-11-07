"""Validaciones para evitar SSRF y lectura de archivos arbitrarios.

El formulario de imágenes del admin acepta URLs, rutas locales y nombres del
storage. Sin validación, un usuario con acceso al admin podía hacer que el
servidor descargara recursos internos (por ejemplo 169.254.169.254) o leyera
cualquier archivo del contenedor y lo publicara en R2.
"""

import ipaddress
import os
import socket
from io import BytesIO
from urllib.parse import urljoin, urlparse

import requests
from PIL import Image, UnidentifiedImageError

MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_REDIRECTS = 3
ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {None, 80, 443}
ALLOWED_LOCAL_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_FORMATS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
LOCAL_IMAGES_ROOT = "/Recursos"


class UnsafeSourceError(ValueError):
    """La fuente indicada no es segura o no está permitida."""


def _resolved_ips(host: str, port: int) -> list[ipaddress._BaseAddress]:
    try:
        infos = socket.getaddrinfo(
            host,
            port,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
    except socket.gaierror as exc:
        raise UnsafeSourceError(f"No se pudo resolver el host: {host}") from exc

    addresses = []
    for info in infos:
        raw = info[4][0].split("%", 1)[0]
        try:
            addresses.append(ipaddress.ip_address(raw))
        except ValueError as exc:
            raise UnsafeSourceError(f"Dirección IP inválida: {raw}") from exc
    return addresses


def validate_remote_url(url: str) -> str:
    """Valida una URL antes de descargarla y devuelve la URL normalizada."""
    parsed = urlparse((url or "").strip())

    if parsed.scheme not in ALLOWED_SCHEMES:
        raise UnsafeSourceError("Solo se permiten URLs http o https.")

    if parsed.username or parsed.password:
        raise UnsafeSourceError("La URL no puede incluir credenciales.")

    if parsed.port not in ALLOWED_PORTS:
        raise UnsafeSourceError("Solo se permiten los puertos 80 y 443.")

    host = parsed.hostname
    if not host:
        raise UnsafeSourceError("La URL no tiene un host válido.")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    for address in _resolved_ips(host, port):
        # is_global es False para privadas, loopback, link-local, reservadas,
        # multicast y no especificadas. Es la comprobación más completa.
        if not address.is_global:
            raise UnsafeSourceError(
                "La URL apunta a una dirección interna o reservada."
            )

    return url.strip()


def validate_local_path(path: str) -> str:
    """Permite solo archivos de imagen dentro de /Recursos."""
    if not path or not path.startswith("/"):
        raise UnsafeSourceError("La ruta local debe ser absoluta.")

    root = os.path.realpath(LOCAL_IMAGES_ROOT)
    real_path = os.path.realpath(path)

    if os.path.commonpath([root, real_path]) != root:
        raise UnsafeSourceError(
            f"Solo se permiten archivos dentro de {LOCAL_IMAGES_ROOT}."
        )

    if not os.path.isfile(real_path):
        raise UnsafeSourceError(f"No existe la ruta en el contenedor: {path}")

    extension = os.path.splitext(real_path)[1].lower()
    if extension not in ALLOWED_LOCAL_EXTENSIONS:
        raise UnsafeSourceError(
            "Formato no permitido. Usa JPEG, PNG o WebP."
        )

    return real_path


def validate_storage_name(name: str) -> str:
    """Permite solo objetos de imagen dentro de products/."""
    normalized = (name or "").strip().lstrip("/")
    if not normalized.startswith("products/") or ".." in normalized.split("/"):
        raise UnsafeSourceError(
            "El nombre en el storage debe estar dentro de products/."
        )
    return normalized


def validate_image_bytes(data: bytes) -> str:
    """Comprueba que los bytes sean una imagen soportada y devuelve su extensión.

    No confiamos en la extensión del nombre ni en el Content-Type de la
    respuesta: el formato se detecta con Pillow a partir del contenido real.
    """
    if not data:
        raise UnsafeSourceError("La imagen está vacía.")

    try:
        with Image.open(BytesIO(data)) as image:
            image.verify()
        with Image.open(BytesIO(data)) as image:
            image_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise UnsafeSourceError("El archivo no es una imagen válida.") from exc

    extension = ALLOWED_IMAGE_FORMATS.get(image_format)
    if not extension:
        raise UnsafeSourceError(
            "Formato de imagen no permitido. Usa JPEG, PNG o WebP."
        )
    return extension


def download_remote_image(url: str) -> tuple[bytes, str]:
    """Descarga una imagen validando cada redirección y el tamaño máximo."""
    current_url = url
    for _ in range(MAX_REDIRECTS + 1):
        validate_remote_url(current_url)
        response = requests.get(
            current_url,
            timeout=30,
            allow_redirects=False,
            stream=True,
        )

        if response.is_redirect:
            location = response.headers.get("Location")
            response.close()
            if not location:
                raise UnsafeSourceError("Redirección sin destino.")
            current_url = urljoin(response.url or current_url, location)
            continue

        response.raise_for_status()

        content_length = response.headers.get("Content-Length")
        if content_length:
            try:
                if int(content_length) > MAX_DOWNLOAD_BYTES:
                    response.close()
                    raise UnsafeSourceError("La imagen supera el tamaño máximo (10 MB).")
            except ValueError:
                pass

        chunks = []
        total = 0
        try:
            for chunk in response.iter_content(chunk_size=64 * 1024):
                if not chunk:
                    continue
                total += len(chunk)
                if total > MAX_DOWNLOAD_BYTES:
                    raise UnsafeSourceError("La imagen supera el tamaño máximo (10 MB).")
                chunks.append(chunk)
        finally:
            response.close()

        return b"".join(chunks), current_url

    raise UnsafeSourceError("Demasiadas redirecciones.")
