from __future__ import annotations

import hashlib
import hmac
import base64
import time
import urllib.parse
import os

import requests


def _build_signed_webhook(webhook: str, secret: str) -> str:
    ts = str(int(time.time() * 1000))
    sign_str = f"{ts}\n{secret}".encode("utf-8")
    sign = base64.b64encode(hmac.new(secret.encode("utf-8"), sign_str, digestmod=hashlib.sha256).digest())
    sign_q = urllib.parse.quote_plus(sign)
    sep = "&" if "?" in webhook else "?"
    return f"{webhook}{sep}timestamp={ts}&sign={sign_q}"


def push_wecom(webhook: str, text: str) -> None:
    if not webhook:
        return
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": text[:3900]},
    }
    requests.post(webhook, json=payload, timeout=20).raise_for_status()


def push_wecom_markdown(text: str) -> None:
    webhook = os.getenv("WECOM_WEBHOOK_URL") or os.getenv("WECOM_WEBHOOK")
    secret = os.getenv("WECOM_SECRET", "")
    if not webhook:
        return
    if secret:
        webhook = _build_signed_webhook(webhook, secret)
    push_wecom(webhook, text)
