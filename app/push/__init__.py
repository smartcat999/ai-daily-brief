from __future__ import annotations

import os

from .wecom import push_wecom


def push_wecom_markdown(markdown: str) -> None:
    # Backward-compatible wrapper expected by app.main
    webhook = os.getenv("WECOM_WEBHOOK", "")
    push_wecom(webhook, markdown)
