"""Microsoft Graph sender. Mock mode when credentials are not set."""
import requests

from . import config

MOCK_OUTBOX: list[dict] = []


def is_live() -> bool:
    return all([config.GRAPH_TENANT_ID, config.GRAPH_CLIENT_ID, config.GRAPH_CLIENT_SECRET, config.GRAPH_SENDER_MAILBOX])


def _token() -> str:
    import msal

    app = msal.ConfidentialClientApplication(
        config.GRAPH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{config.GRAPH_TENANT_ID}",
        client_credential=config.GRAPH_CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in result:
        raise RuntimeError(result.get("error_description", "token request failed"))
    return result["access_token"]


def send_mail(to: str, subject: str, body: str, cc: list[str] | None = None) -> None:
    """Raises on failure. Needs Mail.Send (application) on the sender mailbox only."""
    if not is_live():
        MOCK_OUTBOX.append({"to": to, "subject": subject, "body": body, "cc": cc or []})
        return
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": to}}],
            "ccRecipients": [{"emailAddress": {"address": c}} for c in (cc or [])],
        },
        "saveToSentItems": True,
    }
    r = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{config.GRAPH_SENDER_MAILBOX}/sendMail",
        headers={"Authorization": f"Bearer {_token()}"},
        json=payload,
        timeout=30,
    )
    r.raise_for_status()
