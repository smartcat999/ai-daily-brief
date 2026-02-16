import requests


def push_wecom(webhook: str, text: str) -> None:
    if not webhook:
        return
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": text[:3900]},
    }
    requests.post(webhook, json=payload, timeout=20).raise_for_status()
