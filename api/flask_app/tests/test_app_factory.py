"""app.py — create_app() wiring and Config.validate_config() failure path.

Doesn't call create_app() a second time: every other test file's import of
api.flask_app.app already exercises create_app()'s body once (module import
happens exactly once per process, in conftest.py), and re-invoking it here
would run a second db.create_all() against the shared app/db state for no
benefit. Config.validate_config() — the one behavior conftest.py's env vars
are specifically there to neutralize, not test — is verified directly and
in isolation instead, via monkeypatch on the Config class.
"""
import pytest

from api.flask_app.config import Config


class TestCreateApp:
    def test_all_blueprints_are_registered(self, app):
        assert set(app.blueprints.keys()) == {"linebot_bp", "ai_bp", "web_bp", "auth_bp"}

    def test_api_prefixed_routes_have_api_prefix(self, app):
        rules = {rule.rule for rule in app.url_map.iter_rules()}
        assert "/api/ai" in rules
        assert "/api/user_message" in rules

    def test_linebot_and_auth_routes_have_no_api_prefix(self, app):
        rules = {rule.rule for rule in app.url_map.iter_rules()}
        assert "/callback" in rules
        assert "/auth/line" in rules


class TestConfigValidation:
    def test_validate_config_raises_when_required_var_missing(self, monkeypatch):
        monkeypatch.setattr(Config, "OPENAI_API_KEY", "")
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            Config.validate_config()

    def test_validate_config_lists_all_missing_vars(self, monkeypatch):
        monkeypatch.setattr(Config, "CHANNEL_SECRET", "")
        monkeypatch.setattr(Config, "CHANNEL_ACCESS_TOKEN", "")
        with pytest.raises(RuntimeError) as excinfo:
            Config.validate_config()
        assert "CHANNEL_SECRET" in str(excinfo.value)
        assert "CHANNEL_ACCESS_TOKEN" in str(excinfo.value)

    def test_validate_config_passes_when_all_required_vars_present(self):
        Config.validate_config()  # should not raise, given conftest's env vars
