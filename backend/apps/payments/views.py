import time

import stripe
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import nequi as nequi_client
from .models import Payment
from .serializers import (
    CreatePaymentSerializer,
    NequiPaymentSerializer,
    NequiPaymentResponseSerializer,
    NequiStatusSerializer,
    PaymentIntentResponseSerializer,
    PaymentSerializer,
)


class PaymentViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == "create_payment_intent":
            return CreatePaymentSerializer
        if self.action == "create_nequi_payment":
            return NequiPaymentSerializer
        if self.action == "check_nequi_status":
            return NequiStatusSerializer
        return PaymentSerializer

    # ── Stripe (Tarjeta) ──

    @action(detail=False, methods=["post"], url_path="create-payment-intent")
    def create_payment_intent(self, request):
        serializer = CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = Payment.objects.create(
            amount=serializer.validated_data["amount"],
            currency=serializer.validated_data.get("currency", "COP"),
            method=Payment.Method.CARD,
            customer_name=serializer.validated_data.get("customer_name", ""),
            customer_email=serializer.validated_data.get("customer_email", ""),
            customer_phone=serializer.validated_data.get("customer_phone", ""),
            metadata={"cart_items": serializer.validated_data.get("cart_items", [])},
        )

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),
                currency=payment.currency.lower(),
                metadata={
                    "payment_id": str(payment.id),
                    "customer_name": payment.customer_name,
                    "customer_email": payment.customer_email,
                },
                description=f"IOQUE - Pago #{payment.id}",
            )

            payment.stripe_payment_intent_id = intent.id
            payment.stripe_client_secret = intent.client_secret
            payment.save()

            response_data = PaymentIntentResponseSerializer({
                "payment_id": payment.id,
                "client_secret": intent.client_secret,
                "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            }).data

            return Response(response_data, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            payment.status = Payment.Status.FAILED
            payment.save()
            return Response(
                {"error": str(e.user_message or e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"], url_path="stripe-webhook")
    def stripe_webhook(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            self._update_stripe_status(intent.id, Payment.Status.SUCCEEDED)
        elif event["type"] == "payment_intent.payment_failed":
            intent = event["data"]["object"]
            self._update_stripe_status(intent.id, Payment.Status.FAILED)
        elif event["type"] == "payment_intent.canceled":
            intent = event["data"]["object"]
            self._update_stripe_status(intent.id, Payment.Status.CANCELED)

        return Response({"status": "ok"})

    def _update_stripe_status(self, payment_intent_id: str, status_value: str) -> None:
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            payment.status = status_value
            payment.save()
        except Payment.DoesNotExist:
            pass

    # ── Nequi ──

    @action(detail=False, methods=["post"], url_path="nequi-pay")
    def create_nequi_payment(self, request):
        serializer = NequiPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = Payment.objects.create(
            amount=serializer.validated_data["amount"],
            currency=serializer.validated_data.get("currency", "COP"),
            method=Payment.Method.NEQUI,
            nequi_phone_number=serializer.validated_data["phone_number"],
            metadata={"cart_items": serializer.validated_data.get("cart_items", [])},
        )

        try:
            amount_pesos = int(payment.amount)
            reference = f"IOQUE-{payment.id}-{int(time.time())}"
            result = nequi_client.create_payment(
                phone_number=payment.nequi_phone_number,
                amount=amount_pesos,
                reference=reference,
            )

            transaction_id = (
                result.get("ResponseMessage", {})
                .get("ResponseBody", {})
                .get("any", {})
                .get("unregisteredPaymentRS", {})
                .get("transactionID", "")
            )

            payment.nequi_transaction_id = transaction_id
            payment.save()

            return Response(NequiPaymentResponseSerializer({
                "payment_id": payment.id,
                "transaction_id": transaction_id,
                "message": "Revisa tu app de Nequi para aprobar el pago",
            }).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            payment.status = Payment.Status.FAILED
            payment.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

    @action(detail=False, methods=["post"], url_path="nequi-webhook")
    def nequi_webhook(self, request):
        data = request.data
        transaction_id = (
            data.get("ResponseMessage", {})
            .get("ResponseBody", {})
            .get("any", {})
            .get("unregisteredPaymentRS", {})
            .get("transactionID", "")
        )
        status_code = (
            data.get("ResponseMessage", {})
            .get("ResponseHeader", {})
            .get("Status", {})
            .get("StatusCode", "")
        )

        if transaction_id:
            new_status = (
                Payment.Status.SUCCEEDED if status_code == "0"
                else Payment.Status.FAILED
            )
            try:
                payment = Payment.objects.get(nequi_transaction_id=transaction_id)
                payment.status = new_status
                payment.save()
            except Payment.DoesNotExist:
                pass

        return Response({"status": "ok"})

    @action(detail=False, methods=["post"], url_path="nequi-status")
    def check_nequi_status(self, request):
        serializer = NequiStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            payment = Payment.objects.get(id=serializer.validated_data["payment_id"])
            return Response({
                "payment_id": payment.id,
                "status": payment.status,
            })
        except Payment.DoesNotExist:
            return Response(
                {"error": "Pago no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
