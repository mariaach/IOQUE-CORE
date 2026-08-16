import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.catalog.products.models import Product
from apps.orders.models import Order, OrderItem
from apps.payments.models import PaymentTransaction
from apps.payments.providers import (
    PaymentProviderError,
    get_payment_provider,
    log_event,
)

logger = logging.getLogger(__name__)


class OrderValidationError(Exception):
    pass


class OrderNotFoundError(Exception):
    pass


def _product_name(product: Product, language: str = "es") -> str:
    trans = product.translations.filter(language=language).first()
    if trans:
        return trans.name
    trans = product.translations.first()
    return trans.name if trans else product.sku


class OrderService:
    @staticmethod
    def _load_product(product_id: int) -> Product:
        try:
            return Product.objects.select_for_update().get(id=product_id, active=True)
        except Product.DoesNotExist:
            raise OrderValidationError(f"Producto {product_id} no disponible")

    @staticmethod
    def _recover_idempotent(idempotency_key: str):
        if not idempotency_key:
            return None
        return Order.objects.filter(idempotency_key=idempotency_key).first()

    @classmethod
    def create_order(cls, *, items, customer_name="", customer_email="", customer_phone="", idempotency_key="") -> Order:
        existing = cls._recover_idempotent(idempotency_key)
        if existing:
            return existing

        if not items:
            raise OrderValidationError("El pedido no tiene artículos")

        shipping_cost = getattr(settings, "DEFAULT_SHIPPING_COST", 0)
        discount_threshold = getattr(settings, "SHIPPING_DISCOUNT_THRESHOLD", 2)
        discount_per_extra = getattr(settings, "SHIPPING_DISCOUNT_PER_EXTRA", 15000)
        currency = "COP"

        with transaction.atomic():
            products = []
            quantity_by_id = {}
            # Collect item quantities per product
            item_map = {}
            for item in items:
                product_id = item.get("product_id")
                quantity = int(item.get("quantity", 1))
                if product_id in item_map:
                    item_map[product_id] += quantity
                else:
                    item_map[product_id] = quantity

            products = []
            quantity_by_id = {}
            for product_id, quantity in item_map.items():
                product = cls._load_product(product_id)
                if product.stock < quantity:
                    raise OrderValidationError(
                        f"Stock insuficiente para {_product_name(product)}: disponible {product.stock}"
                    )
                products.append(product)
                quantity_by_id[product.id] = quantity
            subtotal = sum(p.price * q for p, q in zip(products, [quantity_by_id[p.id] for p in products]))
            total_qty = sum(quantity_by_id.values())
            discount = 0
            if total_qty > discount_threshold:
                discount = (total_qty - discount_threshold) * discount_per_extra
            total = subtotal + shipping_cost - discount
            if total < 0:
                total = 0

            order = Order(
                customer_name=customer_name.strip(),
                customer_email=customer_email.strip(),
                customer_phone=customer_phone.strip(),
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                discount=discount,
                total=total,
                currency=currency,
                idempotency_key=idempotency_key or None,
            )
            order.save()

            for product in products:
                qty = quantity_by_id[product.id]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=_product_name(product),
                    product_sku=product.sku,
                    unit_price=product.price,
                    quantity=qty,
                )
                # Decrement inventory
            log_event("ORDER_CREATED", order_number=order.order_number)
            order.refresh_from_db()
            return order

    @staticmethod
    def create_payment(order: Order) -> PaymentTransaction:
        provider = get_payment_provider()

        pending = order.payment_transactions.filter(
            status__in=[
                PaymentTransaction.Status.CREATED,
                PaymentTransaction.Status.QR_GENERATED,
                PaymentTransaction.Status.PENDING,
            ]
        ).order_by("-created_at").first()
        if pending and pending.expires_at and pending.expires_at <= timezone.now():
            pending.status = PaymentTransaction.Status.EXPIRED
            pending.save(update_fields=["status", "updated_at"])
            log_event("PAYMENT_EXPIRED", order_number=order.order_number, provider_reference=pending.provider_reference)
            pending = None

        if pending:
            return pending

        with transaction.atomic():
            txn = PaymentTransaction.objects.create(
                order=order,
                amount=order.total,
                currency=order.currency,
                status=PaymentTransaction.Status.CREATED,
                expires_at=timezone.now()
                + timedelta(minutes=settings.NEQUI_PAYMENT_EXPIRATION_MINUTES),
            )
            log_event("PAYMENT_CREATED", order_number=order.order_number)
            try:
                data = provider.generate_payment_qr(order, txn)
            except PaymentProviderError:
                order.status = Order.Status.PAYMENT_FAILED
                order.save(update_fields=["status", "updated_at"])
                raise
            return txn

    @staticmethod
    def check_payment_status(order: Order) -> PaymentTransaction:
        provider = get_payment_provider()
        txn = order.payment_transactions.order_by("-created_at").first()
        if not txn:
            raise OrderNotFoundError("No hay transacción para este pedido")

        if txn.is_terminal:
            return txn

        status, raw = provider.get_payment_status(txn)
        log_event("PAYMENT_STATUS_CHECKED", order_number=order.order_number, provider_reference=txn.provider_reference)

        if raw:
            txn.raw_response = raw
            txn.save(update_fields=["raw_response", "updated_at"])

        if status != txn.status:
            txn.status = status
            txn.save(update_fields=["status", "updated_at"])

        if status == PaymentTransaction.Status.APPROVED:
            order.status = Order.Status.PAID
            order.paid_at = timezone.now()
            order.save(update_fields=["status", "paid_at", "updated_at"])
            txn.paid_at = timezone.now()
            txn.save(update_fields=["paid_at", "updated_at"])
            log_event("PAYMENT_APPROVED", order_number=order.order_number, provider_reference=txn.provider_reference)
        elif status == PaymentTransaction.Status.REJECTED:
            order.status = Order.Status.PAYMENT_FAILED
            order.save(update_fields=["status", "updated_at"])
            log_event("PAYMENT_REJECTED", order_number=order.order_number, provider_reference=txn.provider_reference)
        elif status == PaymentTransaction.Status.EXPIRED:
            order.status = Order.Status.PAYMENT_EXPIRED
            order.save(update_fields=["status", "updated_at"])
        elif status == PaymentTransaction.Status.ERROR:
            order.status = Order.Status.PAYMENT_FAILED
            order.save(update_fields=["status", "updated_at"])

        return txn