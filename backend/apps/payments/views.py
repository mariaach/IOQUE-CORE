import hashlib
import hmac
import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.payments.models import Payment, PaymentTransaction
from apps.payments.providers import log_event

logger = logging.getLogger(__name__)

APPROVED_STATUSES = {
    "0", "200", "APPROVED", "SUCCESS", "SUCCEEDED", "PAYMENT_APPROVED", "COMPLETED",
}
REJECTED_STATUSES = {
    "1", "REJECTED", "FAILED", "ERROR", "DECLINED", "PAYMENT_REJECTED", "CANCELLED",
}


def _deep_get(data, *path, default=""):
    current = data
    for key in path:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _extract_transaction(payload: dict) -> tuple[str, str, str]:
    """Soporta el formato legacy de Nequi y payloads planos de webhook."""
    body = _deep_get(payload, "ResponseMessage", "ResponseBody", "any",
                     "unregisteredPaymentRS", default={}) or {}
    if not isinstance(body, dict):
        body = {}

    transaction_id = (
        body.get("transactionID")
        or payload.get("transaction_id")
        or payload.get("transactionId")
        or payload.get("id")
        or ""
    )
    reference = (
        payload.get("reference")
        or payload.get("provider_reference")
        or body.get("reference")
        or ""
    )
    status_value = (
        _deep_get(payload, "ResponseMessage", "ResponseHeader", "Status", "StatusCode")
        or payload.get("status")
        or payload.get("statusCode")
        or payload.get("StatusCode")
        or ""
    )
    return str(transaction_id), str(reference), str(status_value).upper()


def _normalize_status(value: str) -> str | None:
    if value in APPROVED_STATUSES:
        return PaymentTransaction.Status.APPROVED
    if value in REJECTED_STATUSES:
        return PaymentTransaction.Status.REJECTED
    return None


def _signature_is_valid(request) -> bool | None:
    """Valida el webhook. Devuelve None si el secreto no está configurado."""
    secret = getattr(settings, "NEQUI_WEBHOOK_SECRET", "")
    if not secret:
        return None

    signature = request.headers.get("X-Nequi-Signature", "").strip()
    if signature:
        expected = hmac.new(
            secret.encode("utf-8"), request.body, hashlib.sha256
        ).hexdigest()
        provided = signature.split("=", 1)[1] if "=" in signature else signature
        return hmac.compare_digest(provided.strip().lower(), expected)

    token = request.query_params.get("token", "")
    return hmac.compare_digest(token, secret)


class NequiWebhookView(APIView):
    """Notificación de Nequi.

    Solo se aceptan peticiones firmadas con ``NEQUI_WEBHOOK_SECRET``:
    HMAC-SHA256 del cuerpo en ``X-Nequi-Signature`` (hex o ``sha256=<hex>``)
    o, como alternativa, ``?token=<secreto>``. Si el secreto no está
    configurado el endpoint queda deshabilitado (503), nunca abierto.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        valid = _signature_is_valid(request)
        if valid is None:
            logger.error("Webhook Nequi rechazado: NEQUI_WEBHOOK_SECRET no configurado")
            return Response(
                {"error": "Webhook no configurado"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if not valid:
            logger.warning("Webhook Nequi rechazado: firma inválida")
            return Response(
                {"error": "Firma inválida"},
                status=status.HTTP_403_FORBIDDEN,
            )

        payload = request.data if isinstance(request.data, dict) else {}
        transaction_id, reference, raw_status = _extract_transaction(payload)
        new_status = _normalize_status(raw_status)

        if not new_status:
            logger.info(
                "Webhook Nequi sin estado reconocible transaction=%s status=%s",
                transaction_id,
                raw_status,
            )
            return Response({"status": "ignored"})

        updated = self._update_transaction(transaction_id, reference, new_status, payload)
        self._update_legacy_payment(transaction_id, new_status)

        return Response({"status": "ok", "updated": updated})

    @staticmethod
    def _update_transaction(transaction_id, reference, new_status, payload) -> bool:
        with transaction.atomic():
            queryset = PaymentTransaction.objects.select_for_update().select_related("order")
            txn = None
            if transaction_id:
                txn = queryset.filter(
                    provider_transaction_id=transaction_id
                ).order_by("-created_at").first()
            if txn is None and reference:
                txn = queryset.filter(
                    provider_reference=reference
                ).order_by("-created_at").first()
            if txn is None:
                logger.warning(
                    "Webhook Nequi: transacción desconocida id=%s ref=%s",
                    transaction_id,
                    reference,
                )
                return False

            # No degradar un pago ya aprobado por una notificación tardía.
            if txn.status == PaymentTransaction.Status.APPROVED and new_status != PaymentTransaction.Status.APPROVED:
                return False

            now = timezone.now()
            txn.status = new_status
            # El payload puede contener datos sensibles: se guarda solo en el
            # campo interno raw_response, nunca se devuelve por la API pública.
            txn.raw_response = {
                **(txn.raw_response or {}),
                "last_webhook": payload,
            }
            update_fields = ["status", "raw_response", "updated_at"]
            if new_status == PaymentTransaction.Status.APPROVED and not txn.paid_at:
                txn.paid_at = now
                update_fields.append("paid_at")
            txn.save(update_fields=update_fields)

            order = txn.order
            if new_status == PaymentTransaction.Status.APPROVED:
                order.status = Order.Status.PAID
                order.paid_at = order.paid_at or now
                order.save(update_fields=["status", "paid_at", "updated_at"])
                log_event(
                    "PAYMENT_APPROVED",
                    order_number=order.order_number,
                    provider_reference=txn.provider_reference,
                )
            else:
                order.status = Order.Status.PAYMENT_FAILED
                order.save(update_fields=["status", "updated_at"])
                log_event(
                    "PAYMENT_REJECTED",
                    order_number=order.order_number,
                    provider_reference=txn.provider_reference,
                )
            return True

    @staticmethod
    def _update_legacy_payment(transaction_id, new_status) -> None:
        if not transaction_id:
            return
        legacy_status = (
            Payment.Status.SUCCEEDED
            if new_status == PaymentTransaction.Status.APPROVED
            else Payment.Status.FAILED
        )
        Payment.objects.filter(
            nequi_transaction_id=transaction_id
        ).update(status=legacy_status)
