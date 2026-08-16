import abc
import logging
import time
import uuid
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

LOG_EVENTS = {
    "ORDER_CREATED",
    "PAYMENT_CREATED",
    "QR_GENERATED",
    "PAYMENT_STATUS_CHECKED",
    "PAYMENT_APPROVED",
    "PAYMENT_REJECTED",
    "PAYMENT_EXPIRED",
    "PAYMENT_CANCELLED",
    "PAYMENT_REVERSED",
}


def log_event(event: str, *, order_number: str = "", provider_reference: str = "", **extra) -> None:
    if event not in LOG_EVENTS:
        return
    safe_extra = {k: v for k, v in extra.items() if "secret" not in k.lower() and "key" not in k.lower() and "token" not in k.lower()}
    logger.info(
        "payment_event=%s order=%s reference=%s extra=%s",
        event,
        order_number,
        provider_reference,
        safe_extra,
    )


class PaymentProviderError(Exception):
    def __init__(self, message: str, code: str = "PROVIDER_ERROR"):
        super().__init__(message)
        self.code = code


class PaymentProvider(abc.ABC):
    name: str = "generic"

    @abc.abstractmethod
    def generate_payment_qr(self, order, transaction) -> dict:
        """Crea/reutiliza la transacción y devuelve datos del QR.

        Devuelve: {qr_code, qr_payload, provider_reference, provider_transaction_id, expires_at}
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_payment_status(self, transaction):
        """Consulta el estado del pago y devuelve una tupla (status, raw_response)."""
        raise NotImplementedError

    def cancel_payment(self, transaction) -> None:
        raise NotImplementedError

    def reverse_payment(self, transaction) -> None:
        raise NotImplementedError


class NequiStaticProvider(PaymentProvider):
    name = "NEQUI_STATIC"

    def generate_payment_qr(self, order, transaction) -> dict:
        reference = f"IOQUE-{order.order_number}-{transaction.id}"
        transaction.provider_reference = reference
        transaction.qr_code = settings.NEQUI_STATIC_QR_URL
        transaction.qr_payload = ""
        transaction.status = transaction.Status.QR_GENERATED
        expires_at = timezone.now() + timedelta(minutes=settings.NEQUI_PAYMENT_EXPIRATION_MINUTES)
        transaction.expires_at = expires_at
        transaction.save(
            update_fields=[
                "provider_reference", "qr_code", "qr_payload",
                "status", "expires_at", "updated_at",
            ]
        )
        log_event("QR_GENERATED", order_number=order.order_number, provider_reference=reference)
        return {
            "qr_code": transaction.qr_code,
            "qr_payload": transaction.qr_payload,
            "provider_reference": reference,
            "provider_transaction_id": transaction.provider_transaction_id,
            "expires_at": expires_at.isoformat(),
        }

    def get_payment_status(self, transaction):
        now = timezone.now()
        if transaction.status == transaction.Status.QR_GENERATED and transaction.expires_at and now > transaction.expires_at:
            transaction.status = transaction.Status.EXPIRED
            transaction.save(update_fields=["status", "updated_at"])
            log_event("PAYMENT_EXPIRED", provider_reference=transaction.provider_reference)
        return transaction.status, {}

    def cancel_payment(self, transaction) -> None:
        if not transaction.is_terminal:
            transaction.status = transaction.Status.CANCELLED
            transaction.save(update_fields=["status", "updated_at"])
            log_event("PAYMENT_CANCELLED", provider_reference=transaction.provider_reference)

    def reverse_payment(self, transaction) -> None:
        if transaction.status == transaction.Status.APPROVED:
            transaction.status = transaction.Status.REVERSED
            transaction.save(update_fields=["status", "updated_at"])
            log_event("PAYMENT_REVERSED", provider_reference=transaction.provider_reference)


class NequiDynamicProvider(PaymentProvider):
    """Preparado para la API oficial de QR dinámico de Nequi.

    Requiere credenciales del ambiente QA/sandbox (docs.conecta.nequi.com.co).
    El QR dinámico se genera vía API, queda asociado a una única transacción y
    se consulta con getStatus. La integración real debe completarse con las
    credenciales habilitadas; aquí se delega en el cliente Nequi existente.
    """

    name = "NEQUI_DYNAMIC"

    def generate_payment_qr(self, order, transaction) -> dict:
        from . import nequi as nequi_client

        reference = f"IOQUE-{order.order_number}-{transaction.id}-{uuid.uuid4().hex[:6].upper()}"
        transaction.provider_reference = reference
        transaction.status = transaction.Status.PENDING
        try:
            result = nequi_client.create_payment(
                phone_number=settings.NEQUI_MERCHANT_PHONE,
                amount=transaction.amount,
                reference=reference,
            )
            rs = (
                result.get("ResponseMessage", {})
                .get("ResponseBody", {})
                .get("any", {})
                .get("unregisteredPaymentRS", {})
            )
            transaction_id = rs.get("transactionID", "")
            qr_code = rs.get("qrCode") or ""
            if qr_code:
                transaction.qr_code = "data:image/png;base64," + qr_code
            transaction.provider_transaction_id = transaction_id
            transaction.raw_response = result
            transaction.status = transaction.Status.QR_GENERATED
            expires_at = timezone.now() + timedelta(minutes=settings.NEQUI_PAYMENT_EXPIRATION_MINUTES)
            transaction.expires_at = expires_at
            transaction.save()
            log_event("QR_GENERATED", order_number=order.order_number, provider_reference=reference)
            return {
                "qr_code": transaction.qr_code,
                "qr_payload": transaction.qr_payload,
                "provider_reference": reference,
                "provider_transaction_id": transaction_id,
                "expires_at": expires_at.isoformat(),
            }
        except Exception as exc:
            transaction.status = transaction.Status.ERROR
            transaction.failure_reason = str(exc)
            transaction.save(update_fields=["status", "failure_reason", "updated_at"])
            logger.exception("Nequi dynamic QR generation failed for %s", reference)
            raise PaymentProviderError(str(exc), code="NEQUI_ERROR")

    def get_payment_status(self, transaction):
        from . import nequi as nequi_client

        if not transaction.provider_transaction_id:
            return transaction.status, {}
        try:
            data = nequi_client.check_payment_status(transaction.provider_transaction_id)
        except Exception as exc:
            transaction.failure_reason = str(exc)
            transaction.save(update_fields=["failure_reason", "updated_at"])
            return transaction.status, {}
        return transaction.status, data

    def cancel_payment(self, transaction) -> None:
        if not transaction.is_terminal:
            transaction.status = transaction.Status.CANCELLED
            transaction.save(update_fields=["status", "updated_at"])
            log_event("PAYMENT_CANCELLED", provider_reference=transaction.provider_reference)

    def reverse_payment(self, transaction) -> None:
        if transaction.status == transaction.Status.APPROVED:
            transaction.status = transaction.Status.REVERSED
            transaction.save(update_fields=["status", "updated_at"])
            log_event("PAYMENT_REVERSED", provider_reference=transaction.provider_reference)


def get_payment_provider() -> PaymentProvider:
    mode = getattr(settings, "NEQUI_PAYMENT_MODE", "static")
    if mode == "dynamic":
        return NequiDynamicProvider()
    return NequiStaticProvider()