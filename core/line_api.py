import requests

_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
_PUSH_URL  = "https://api.line.me/v2/bot/message/push"


def _auth_headers(token: str) -> dict:
    return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}


def send_line_reply(channel_access_token: str, reply_token: str, text: str):
    """Send a plain text reply."""
    return send_reply_messages(channel_access_token, reply_token, [text_message(text)])


def send_reply_messages(channel_access_token: str, reply_token: str, messages: list[dict]):
    """Send one or more LINE message objects as a reply."""
    resp = requests.post(
        _REPLY_URL,
        headers=_auth_headers(channel_access_token),
        json={"replyToken": reply_token, "messages": messages},
    )
    return resp, resp.status_code


def text_message(text: str) -> dict:
    return {"type": "text", "text": text}


def text_with_quick_reply(text: str, buttons: list[tuple[str, str]]) -> dict:
    """
    Text message with quick reply buttons.
    buttons: list of (label, reply_text) tuples.
    """
    return {
        "type": "text",
        "text": text,
        "quickReply": {
            "items": [
                {"type": "action", "action": {"type": "message", "label": label, "text": reply}}
                for label, reply in buttons
            ]
        },
    }

def exchange_code_for_token(code: str, redirect_uri: str, client_id: str, client_secret: str) -> str:
    """Exchange LINE Login authorization code for an access token."""
    resp = requests.post(
        "https://api.line.me/oauth2/v2.1/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def get_line_profile(access_token: str) -> dict:
    """Get LINE user profile (userId, displayName) from a valid access token."""
    resp = requests.get(
        "https://api.line.me/v2/profile",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    resp.raise_for_status()
    return resp.json()


def send_line_push(channel_access_token: str, user_id: str, text: str):
    """Push a plain-text message to a user (not limited by reply token)."""
    resp = requests.post(
        _PUSH_URL,
        headers=_auth_headers(channel_access_token),
        json={"to": user_id, "messages": [text_message(text)]},
    )
    return resp