"""Shared test constants and mock-object builders.

These constants are the single source of truth for the fake credentials
injected via environment variables in conftest.py — tests reference them
instead of hardcoding literal strings, so the env vars and the values tests
assert against never drift apart.
"""
import base64
import hashlib
import hmac
import importlib
from unittest.mock import MagicMock

TEST_CHANNEL_SECRET = "test-channel-secret"
TEST_CHANNEL_ACCESS_TOKEN = "test-channel-access-token"
TEST_OPENAI_API_KEY = "test-openai-api-key"
TEST_LINE_LOGIN_CHANNEL_ID = "test-line-login-channel-id"
TEST_LINE_LOGIN_CHANNEL_SECRET = "test-line-login-channel-secret"
TEST_LINE_LOGIN_REDIRECT_URI = "http://localhost:5002/auth/line/callback"
TEST_FRONTEND_URL = "http://localhost:3000"
TEST_EXAM_API_URL = "http://mock-exam.test/random-question"


def compute_line_signature(body: bytes, channel_secret: str = TEST_CHANNEL_SECRET) -> str:
    """Compute a real LINE-style HMAC-SHA256 signature for a raw webhook body."""
    digest = hmac.new(channel_secret.encode("utf-8"), body, hashlib.sha256).digest()
    return base64.b64encode(digest).decode("utf-8")


def make_openai_client_mock(content: str) -> MagicMock:
    """Stand in for an `openai.OpenAI(...)` instance returned by the constructor."""
    client = MagicMock()
    completion = MagicMock()
    completion.choices = [MagicMock(message=MagicMock(content=content))]
    client.chat.completions.create.return_value = completion
    return client


def route_module(name):
    """Import an api.flask_app.routes submodule directly, bypassing a name
    collision: routes/__init__.py does `from .xxx_bp import xxx_bp`, which
    rebinds the package attribute `xxx_bp` to the Blueprint instance —
    shadowing the submodule of the same name. String-based
    `mocker.patch("api.flask_app.routes.xxx_bp.symbol")` resolves through
    that shadowed attribute and hits the Blueprint object instead of the
    module, raising AttributeError. `importlib.import_module` returns the
    real module from sys.modules, unaffected by the package's own rebound
    attribute, so patch against the object returned here with
    `mocker.patch.object(route_module("xxx_bp"), "symbol", ...)` instead.
    """
    return importlib.import_module(f"api.flask_app.routes.{name}")


def make_requests_response_mock(status_code=200, json_data=None, text="", raise_for_status_effect=None):
    """Stand in for a `requests.Response`."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    if json_data is not None:
        resp.json.return_value = json_data
    if raise_for_status_effect is not None:
        resp.raise_for_status.side_effect = raise_for_status_effect
    else:
        resp.raise_for_status.return_value = None
    return resp
