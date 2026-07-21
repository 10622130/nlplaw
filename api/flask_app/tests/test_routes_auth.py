"""routes/auth_bp.py — /auth/line, /auth/line/callback, /auth/logout, /auth/me."""
from api.flask_app.models import User
from helpers import route_module

auth_bp_module = route_module("auth_bp")


class TestLineLogin:
    def test_redirects_to_line_auth_url_with_matching_state(self, client):
        resp = client.get("/auth/line")

        assert resp.status_code == 302
        location = resp.headers["Location"]
        assert location.startswith("https://access.line.me/oauth2/v2.1/authorize")
        assert "response_type=code" in location
        assert "scope=profile" in location

        with client.session_transaction() as sess:
            state = sess["oauth_state"]
        assert f"state={state}" in location


class TestLineCallback:
    def test_state_mismatch_returns_400(self, client):
        with client.session_transaction() as sess:
            sess["oauth_state"] = "correct-state"

        resp = client.get("/auth/line/callback?state=wrong-state&code=abc123")

        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Invalid state"}

    def test_missing_code_returns_400(self, client):
        with client.session_transaction() as sess:
            sess["oauth_state"] = "s1"

        resp = client.get("/auth/line/callback?state=s1")

        assert resp.status_code == 400
        assert resp.get_json() == {"error": "Missing code"}

    def test_new_user_logs_in_and_redirects_to_frontend(self, client, app_context, mocker):
        with client.session_transaction() as sess:
            sess["oauth_state"] = "s1"
        mocker.patch.object(auth_bp_module, "exchange_code_for_token", return_value="access-tok")
        mocker.patch.object(
            auth_bp_module,
            "get_line_profile",
            return_value={"userId": "Unewuser001", "displayName": "New User"},
        )

        resp = client.get("/auth/line/callback?state=s1&code=abc123")

        assert resp.status_code == 302
        assert resp.headers["Location"] == "http://localhost:3000"
        assert User.exists("Unewuser001") is True
        with client.session_transaction() as sess:
            assert sess["user_id"] == "Unewuser001"
            assert sess["display_name"] == "New User"

    def test_existing_user_logs_in_without_duplicate_create(self, client, app_context, make_user, mocker):
        user_id = make_user("Uexisting001")
        with client.session_transaction() as sess:
            sess["oauth_state"] = "s1"
        mocker.patch.object(auth_bp_module, "exchange_code_for_token", return_value="access-tok")
        mocker.patch.object(
            auth_bp_module,
            "get_line_profile",
            return_value={"userId": user_id, "displayName": "Existing User"},
        )

        resp = client.get("/auth/line/callback?state=s1&code=abc123")  # must not raise

        assert resp.status_code == 302

    def test_token_exchange_failure_returns_502(self, client, mocker):
        with client.session_transaction() as sess:
            sess["oauth_state"] = "s1"
        mocker.patch.object(
            auth_bp_module,
            "exchange_code_for_token",
            side_effect=RuntimeError("LINE token endpoint down"),
        )

        resp = client.get("/auth/line/callback?state=s1&code=abc123")

        assert resp.status_code == 502
        assert resp.get_json() == {"error": "LINE 登入失敗，請稍後再試。"}

    def test_profile_fetch_failure_returns_502(self, client, mocker):
        with client.session_transaction() as sess:
            sess["oauth_state"] = "s1"
        mocker.patch.object(auth_bp_module, "exchange_code_for_token", return_value="access-tok")
        mocker.patch.object(
            auth_bp_module,
            "get_line_profile",
            side_effect=RuntimeError("LINE profile endpoint down"),
        )

        resp = client.get("/auth/line/callback?state=s1&code=abc123")

        assert resp.status_code == 502
        assert resp.get_json() == {"error": "LINE 登入失敗，請稍後再試。"}

    def test_profile_missing_display_name_falls_back_to_empty_string(self, client, app_context, mocker):
        with client.session_transaction() as sess:
            sess["oauth_state"] = "s1"
        mocker.patch.object(auth_bp_module, "exchange_code_for_token", return_value="access-tok")
        mocker.patch.object(
            auth_bp_module,
            "get_line_profile",
            return_value={"userId": "Unodisplay001"},
        )

        client.get("/auth/line/callback?state=s1&code=abc123")

        with client.session_transaction() as sess:
            assert sess["display_name"] == ""


class TestLogout:
    def test_clears_session(self, logged_in_client):
        resp = logged_in_client.post("/auth/logout")
        assert resp.status_code == 200
        assert resp.get_json() == {"ok": True}

        me_resp = logged_in_client.get("/auth/me")
        assert me_resp.get_json() == {"logged_in": False}


class TestMe:
    def test_logged_out_returns_false(self, client):
        resp = client.get("/auth/me")
        assert resp.get_json() == {"logged_in": False}

    def test_logged_in_returns_user_info(self, logged_in_client):
        resp = logged_in_client.get("/auth/me")
        data = resp.get_json()
        assert data["logged_in"] is True
        assert data["user_id"] is not None
        assert data["display_name"] == "Test User"
