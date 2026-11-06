import ipaddress
import os
import tempfile
from io import BytesIO
from unittest import mock

from django.test import SimpleTestCase
from PIL import Image

from . import security
from .security import (
    UnsafeSourceError,
    validate_image_bytes,
    validate_local_path,
    validate_remote_url,
    validate_storage_name,
)


def public_ip(_host, _port):
    return [ipaddress.ip_address("93.184.216.34")]


class RemoteURLTests(SimpleTestCase):
    @mock.patch.object(security, "_resolved_ips", side_effect=public_ip)
    def test_public_https_url_allowed(self, _mock_ips):
        url = "https://example.com/images/foto.jpg"
        self.assertEqual(validate_remote_url(url), url)

    def test_non_http_scheme_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_remote_url("file:///etc/passwd")

    def test_disallowed_port_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_remote_url("http://example.com:8080/foto.jpg")

    def test_credentials_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_remote_url("https://user:pass@example.com/foto.jpg")

    @mock.patch.object(security, "_resolved_ips")
    def test_loopback_rejected(self, mock_ips):
        mock_ips.return_value = [ipaddress.ip_address("127.0.0.1")]
        with self.assertRaises(UnsafeSourceError):
            validate_remote_url("http://localhost/foto.jpg")

    @mock.patch.object(security, "_resolved_ips")
    def test_metadata_endpoint_rejected(self, mock_ips):
        mock_ips.return_value = [ipaddress.ip_address("169.254.169.254")]
        with self.assertRaises(UnsafeSourceError):
            validate_remote_url("http://169.254.169.254/latest/meta-data/")

    @mock.patch.object(security, "_resolved_ips")
    def test_private_network_rejected(self, mock_ips):
        mock_ips.return_value = [ipaddress.ip_address("10.0.0.5")]
        with self.assertRaises(UnsafeSourceError):
            validate_remote_url("http://internal.local/foto.jpg")


class LocalPathTests(SimpleTestCase):
    def test_path_outside_images_root_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_local_path("/etc/passwd")

    def test_traversal_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_local_path("/Recursos/../etc/passwd")

    def test_relative_path_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_local_path("Recursos/foto.jpg")

    def test_non_image_extension_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "secreto.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("no es una imagen")
            with mock.patch.object(security, "LOCAL_IMAGES_ROOT", tmp):
                with self.assertRaises(UnsafeSourceError):
                    validate_local_path(path)

    def test_image_inside_root_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "foto.jpg")
            with open(path, "wb") as fh:
                fh.write(b"contenido")
            with mock.patch.object(security, "LOCAL_IMAGES_ROOT", tmp):
                self.assertEqual(validate_local_path(path), os.path.realpath(path))


class StorageNameTests(SimpleTestCase):
    def test_products_prefix_allowed(self):
        self.assertEqual(
            validate_storage_name("/products/SKU-1/real_0.jpg"),
            "products/SKU-1/real_0.jpg",
        )

    def test_other_prefixes_rejected(self):
        for name in ("CACHE/images/products/x.jpg", "media/x.jpg", "/etc/passwd"):
            with self.subTest(name=name):
                with self.assertRaises(UnsafeSourceError):
                    validate_storage_name(name)

    def test_traversal_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_storage_name("products/../../etc/passwd")


class ImageContentTests(SimpleTestCase):
    def _image_bytes(self, image_format: str) -> bytes:
        buffer = BytesIO()
        Image.new("RGB", (2, 2), color="red").save(buffer, format=image_format)
        return buffer.getvalue()

    def test_jpeg_detected(self):
        self.assertEqual(validate_image_bytes(self._image_bytes("JPEG")), ".jpg")

    def test_png_detected(self):
        self.assertEqual(validate_image_bytes(self._image_bytes("PNG")), ".png")

    def test_webp_detected(self):
        self.assertEqual(validate_image_bytes(self._image_bytes("WEBP")), ".webp")

    def test_text_is_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_image_bytes(b"<html>no soy una imagen</html>")

    def test_empty_is_rejected(self):
        with self.assertRaises(UnsafeSourceError):
            validate_image_bytes(b"")
