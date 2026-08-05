import hashlib
import hmac
import json
import time
import uuid

import requests
from django.conf import settings


def _sign_message(secret_key: str, message: str) -> str:
    return hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()


def get_access_token() -> str:
    resp = requests.post(
        settings.NEQUI_AUTH_URI,
        headers={"Content-Type": "application/json"},
        json={
            "grant_type": "client_credentials",
            "client_id": settings.NEQUI_CLIENT_ID,
            "client_secret": settings.NEQUI_CLIENT_SECRET,
        },
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def create_payment(*, phone_number: str, amount: int, reference: str) -> dict:
    token = get_access_token()
    message_id = str(uuid.uuid4())

    body = {
        "RequestMessage": {
            "RequestHeader": {
                "Channel": "PAYMENT",
                "RequestDate": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                "MessageID": message_id,
                "ClientID": settings.NEQUI_CLIENT_ID,
                "Destination": {
                    "ServiceName": "PaymentsService",
                    "ServiceOperation": "unregisteredPayment",
                    "ServiceRegion": "C001",
                    "ServiceVersion": "1.0.0",
                },
            },
            "RequestBody": {
                "any": {
                    "unregisteredPaymentRQ": {
                        "phoneNumber": phone_number,
                        "code": settings.NEQUI_MERCHANT_CODE,
                        "value": str(amount),
                        "reference": reference,
                        "notificationUrl": settings.NEQUI_NOTIFICATION_URL,
                    }
                }
            },
        }
    }

    payload_str = json.dumps(body)
    signature = _sign_message(settings.NEQUI_CLIENT_SECRET, payload_str)

    resp = requests.post(
        f"{settings.NEQUI_API_BASE_PATH}/-services-paymentservice-unregisteredpayment",
        headers={
            "Content-Type": "application/json",
            "x-api-key": settings.NEQUI_API_KEY,
            "Authorization": f"Bearer {token}",
            "x-signature": signature,
        },
        json=body,
        timeout=15,
    )

    if resp.status_code != 200:
        raise Exception(f"Nequi error: {resp.status_code} {resp.text}")

    data = resp.json()
    status_code = (
        data.get("ResponseMessage", {})
        .get("ResponseHeader", {})
        .get("Status", {})
        .get("StatusCode", "1")
    )

    if status_code != "0":
        desc = (
            data.get("ResponseMessage", {})
            .get("ResponseHeader", {})
            .get("Status", {})
            .get("StatusDesc", "Error desconocido")
        )
        raise Exception(f"Nequi payment error: {desc}")

    return data


def check_payment_status(transaction_id: str) -> dict:
    token = get_access_token()
    message_id = str(uuid.uuid4())

    body = {
        "RequestMessage": {
            "RequestHeader": {
                "Channel": "PAYMENT",
                "RequestDate": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                "MessageID": message_id,
                "ClientID": settings.NEQUI_CLIENT_ID,
                "Destination": {
                    "ServiceName": "PaymentsService",
                    "ServiceOperation": "getStatusPayment",
                    "ServiceRegion": "C001",
                    "ServiceVersion": "1.0.0",
                },
            },
            "RequestBody": {
                "any": {
                    "getStatusPaymentRQ": {
                        "transactionID": transaction_id,
                    }
                }
            },
        }
    }

    payload_str = json.dumps(body)
    signature = _sign_message(settings.NEQUI_CLIENT_SECRET, payload_str)

    resp = requests.post(
        f"{settings.NEQUI_API_BASE_PATH}/-services-paymentservice-getstatuspayment",
        headers={
            "Content-Type": "application/json",
            "x-api-key": settings.NEQUI_API_KEY,
            "Authorization": f"Bearer {token}",
            "x-signature": signature,
        },
        json=body,
        timeout=15,
    )

    if resp.status_code != 200:
        raise Exception(f"Nequi status error: {resp.status_code} {resp.text}")

    return resp.json()
