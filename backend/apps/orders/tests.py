from datetime import timedelta
from unittest import mock

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.categories.models import Category, CategoryTranslation
from apps.catalog.products.models import Product, ProductTranslation
from apps.orders.models import Order, OrderItem
from apps.payments.models import PaymentTransaction


def make_product(sku="SKU-1", price=40000, stock=5, **kwargs):
    category = Category.objects.create()
    CategoryTranslation.objects.create(category=category, language="es", name=f"Cat {sku}")
    product = Product.objects.create(
        category=category,
        sku=sku,
        price=price,
        stock=stock,
        **kwargs,
    )
    ProductTranslation.objects.create(
        product=product,
        language="es",
        name=f"Producto {sku}",
        slug=sku.lower(),
    )
    return product


class FakeProvider:
    status_to_return = PaymentTransaction.Status.PENDING

    def generate_payment_qr(self, order, transaction):
        transaction.provider_reference = f"REF-{order.order_number}"
        transaction.status = transaction.Status.QR_GENERATED
        transaction.save()
        return {
            "qr_code": "https://example.com/qr.png",
            "qr_payload": "",
            "provider_reference": transaction.provider_reference,
            "provider_transaction_id": "",
            "expires_at": None,
        }

    def get_payment_status(self, transaction):
        return self.status_to_return, {"status": self.status_to_return}

    def cancel_payment(self, transaction):
        pass

    def reverse_payment(self, transaction):
        pass


class OrderCreateTests(APITestCase):
    def test_create_order_computes_totals_from_db(self):
        product = make_product()
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 2}]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order = Order.objects.get(order_number=resp.data["order_number"])
        self.assertEqual(order.subtotal, 80000)
        self.assertEqual(order.shipping_cost, 0)
        self.assertEqual(order.discount, 0)
        self.assertEqual(order.total, 80000)
        self.assertEqual(order.currency, "COP")

    def test_frontend_price_is_ignored(self):
        product = make_product(price=41000)
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1, "price": 1}]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["total"], 41000)

    def test_order_items_snapshot(self):
        product = make_product(price=40000)
        self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 3}]},
            format="json",
        )
        item = OrderItem.objects.get()
        self.assertEqual(item.product_name, "Producto SKU-1")
        self.assertEqual(item.unit_price, 40000)
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.subtotal, 120000)

    def test_insufficient_stock(self):
        product = make_product(stock=2)
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 5}]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Stock insuficiente", resp.data["error"])

    def test_nonexistent_product(self):
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": 9999, "quantity": 1}]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_items_rejected(self):
        resp = self.client.post("/api/orders/", {"items": []}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_positive_quantity_rejected(self):
        product = make_product()
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 0}]},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stock_is_decremented(self):
        product = make_product(stock=5)
        self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 2}]},
            format="json",
        )
        product.refresh_from_db()
        self.assertEqual(product.stock, 3)

    def test_idempotency_returns_same_order(self):
        product = make_product()
        payload = {
            "items": [{"product_id": product.id, "quantity": 1}],
            "idempotency_key": "key-123",
        }
        first = self.client.post("/api/orders/", payload, format="json")
        second = self.client.post("/api/orders/", payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first.data["order_number"], second.data["order_number"])
        self.assertEqual(Order.objects.count(), 1)


class PaymentFlowTests(APITestCase):
    def test_static_qr_generated(self):
        product = make_product()
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        order_number = resp.data["order_number"]
        order = Order.objects.get(order_number=order_number)

        qr_resp = self.client.post(f"/api/orders/{order_number}/payment/nequi/")
        self.assertEqual(qr_resp.status_code, status.HTTP_201_CREATED)
        txn = PaymentTransaction.objects.get(order=order)
        self.assertEqual(txn.status, PaymentTransaction.Status.QR_GENERATED)
        self.assertEqual(txn.amount, order.total)
        self.assertIn("qr_code", qr_resp.data)

    def test_payment_approved(self):
        product = make_product()
        order_resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        order_number = order_resp.data["order_number"]
        self.client.post(f"/api/orders/{order_number}/payment/nequi/")

        with mock.patch(
            "apps.orders.services.get_payment_provider",
            return_value=FakeProvider(),
        ):
            FakeProvider.status_to_return = PaymentTransaction.Status.APPROVED
            resp = self.client.get(f"/api/orders/{order_number}/payment/status/")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order = Order.objects.get(order_number=order_number)
        self.assertEqual(order.status, Order.Status.PAID)
        self.assertIsNotNone(order.paid_at)

    def test_payment_rejected(self):
        product = make_product()
        order_resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        order_number = order_resp.data["order_number"]
        self.client.post(f"/api/orders/{order_number}/payment/nequi/")

        with mock.patch(
            "apps.orders.services.get_payment_provider",
            return_value=FakeProvider(),
        ):
            FakeProvider.status_to_return = PaymentTransaction.Status.REJECTED
            resp = self.client.get(f"/api/orders/{order_number}/payment/status/")

        order = Order.objects.get(order_number=order_number)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(order.status, Order.Status.PAYMENT_FAILED)

    def test_payment_expired(self):
        product = make_product()
        order_resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        order_number = order_resp.data["order_number"]
        order = Order.objects.get(order_number=order_number)
        txn = PaymentTransaction.objects.create(
            order=order,
            amount=order.total,
            currency="COP",
            status=PaymentTransaction.Status.QR_GENERATED,
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        resp = self.client.get(f"/api/orders/{order_number}/payment/status/")
        txn.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(txn.status, PaymentTransaction.Status.EXPIRED)
        self.assertEqual(order.status, Order.Status.PAYMENT_EXPIRED)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_status_endpoint_404_for_unknown_order(self):
        resp = self.client.get("/api/orders/NO-EXISTE/payment/status/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_double_payment_returns_same_transaction(self):
        product = make_product()
        order_resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        order_number = order_resp.data["order_number"]
        first = self.client.post(f"/api/orders/{order_number}/payment/nequi/")
        second = self.client.post(f"/api/orders/{order_number}/payment/nequi/")
        self.assertEqual(first.data["id"], second.data["id"])
        self.assertEqual(PaymentTransaction.objects.filter(order__order_number=order_number).count(), 1)


class OrderModelTests(APITestCase):
    def test_order_number_format(self):
        product = make_product()
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        order_number = resp.data["order_number"]
        parts = order_number.split("-")
        self.assertEqual(parts[0], "IOQUE")
        self.assertEqual(len(parts[2]), 4)

    def test_order_display(self):
        product = make_product()
        order = OrderService_create()
        self.assertIn("IOQUE-", str(order))

    def test_shipping_cost_included(self):
        product = make_product()
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 1}]},
            format="json",
        )
        self.assertEqual(resp.data["subtotal"], 40000)
        self.assertEqual(resp.data["shipping_cost"], 0)
        self.assertEqual(resp.data["discount"], 0)
        self.assertEqual(resp.data["total"], 40000)

    def test_discount_applied_when_quantity_above_threshold(self):
        product = make_product(price=40000, stock=10)
        # 3 productos (cantidad 3 > umbral 2) -> 1 producto adicional -> -15000
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 3}]},
            format="json",
        )
        self.assertEqual(resp.data["subtotal"], 120000)
        self.assertEqual(resp.data["shipping_cost"], 0)
        self.assertEqual(resp.data["discount"], 15000)
        self.assertEqual(resp.data["total"], 105000)

    def test_discount_per_additional_product(self):
        product = make_product(price=40000, stock=10)
        # 5 productos -> 3 adicionales -> -45000
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 5}]},
            format="json",
        )
        self.assertEqual(resp.data["subtotal"], 200000)
        self.assertEqual(resp.data["discount"], 45000)
        self.assertEqual(resp.data["total"], 200000 - 45000)

    def test_discount_accumulates_across_items(self):
        p1 = make_product(price=40000, stock=10)
        p2 = make_product(sku="SKU-2", price=40000, stock=10)
        # 2+1 = 3 total -> 1 adicional -> -15000
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": p1.id, "quantity": 2}, {"product_id": p2.id, "quantity": 1}]},
            format="json",
        )
        self.assertEqual(resp.data["subtotal"], 120000)
        self.assertEqual(resp.data["discount"], 15000)
        self.assertEqual(resp.data["total"], 120000 - 15000)

    def test_discount_only_above_threshold(self):
        product = make_product(price=40000, stock=10)
        # cantidad 2 == umbral -> sin descuento
        resp = self.client.post(
            "/api/orders/",
            {"items": [{"product_id": product.id, "quantity": 2}]},
            format="json",
        )
        self.assertEqual(resp.data["discount"], 0)
        self.assertEqual(resp.data["total"], 80000)


class WebhookTests(APITestCase):
    def test_webhook_unknown_transaction_is_safe(self):
        resp = self.client.post(
            "/api/payments/nequi-webhook/",
            {
                "ResponseMessage": {
                    "ResponseBody": {
                        "any": {"unregisteredPaymentRS": {"transactionID": "NO-EXISTE"}}
                    },
                    "ResponseHeader": {"Status": {"StatusCode": "0"}},
                }
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)


def OrderService_create():
    from apps.orders.services import OrderService

    product = make_product(sku="SKU-SVC")
    return OrderService.create_order(items=[{"product_id": product.id, "quantity": 1}])