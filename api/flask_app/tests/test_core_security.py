"""core/security.py — HMAC-SHA256 LINE webhook signature validation."""
from core.security import validate_signature
from helpers import TEST_CHANNEL_SECRET, compute_line_signature


class TestValidateSignature:
    def test_valid_signature_returns_true(self, app_context):
        body = b'{"events":[]}'
        signature = compute_line_signature(body)
        assert validate_signature(body, signature) is True

    def test_signature_computed_with_wrong_secret_returns_false(self, app_context):
        body = b'{"events":[]}'
        signature = compute_line_signature(body, channel_secret="wrong-secret")
        assert validate_signature(body, signature) is False

    def test_tampered_body_returns_false(self, app_context):
        body = b'{"events":[]}'
        signature = compute_line_signature(body)
        tampered_body = b'{"events":[{"tampered":true}]}'
        assert validate_signature(tampered_body, signature) is False

    def test_missing_signature_returns_false(self, app_context):
        # hmac.compare_digest(str, None) raises TypeError internally, which
        # validate_signature's catch-all except turns into False.
        body = b'{"events":[]}'
        assert validate_signature(body, None) is False

    def test_missing_channel_secret_in_config_returns_false(self, app_context):
        original = app_context.config["CHANNEL_SECRET"]
        app_context.config["CHANNEL_SECRET"] = None
        try:
            body = b'{"events":[]}'
            signature = compute_line_signature(body, channel_secret=TEST_CHANNEL_SECRET)
            assert validate_signature(body, signature) is False
        finally:
            app_context.config["CHANNEL_SECRET"] = original
