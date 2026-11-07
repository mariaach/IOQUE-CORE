"""Tokens firmados para acceder al estado y pago de un pedido.

El número de pedido es corto y predecible (IOQUE-YYYYMMDD-NNNN), por lo que no
sirve como secreto. El token incluye el número de pedido y una marca de tiempo,
firmados con ``SECRET_KEY``; así el frontend puede consultar su propio pedido
sin que terceros enumeren pedidos ajenos.
"""

from django.conf import settings
from django.core import signing

ORDER_ACCESS_SALT = "orders.access"
ORDER_ACCESS_MAX_AGE = getattr(
    settings, "ORDER_ACCESS_TOKEN_MAX_AGE", 60 * 60 * 24 * 30
)  # 30 días


def make_order_token(order) -> str:
    """Genera un token de acceso para un pedido."""
    return signing.dumps(
        {"order": order.order_number},
        salt=ORDER_ACCESS_SALT,
    )


def validate_order_token(token: str, order) -> bool:
    """Devuelve True si el token es válido y pertenece al pedido indicado."""
    if not token:
        return False
    try:
        data = signing.loads(
            token,
            salt=ORDER_ACCESS_SALT,
            max_age=ORDER_ACCESS_MAX_AGE,
        )
    except signing.BadSignature:
        return False
    return data.get("order") == order.order_number
