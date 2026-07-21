"""routes/ai_bp.py — POST /api/ai, GET /api/test_openai_key.

Contrast with test_routes_web.py: when the AI call fails, /api/ai returns
200 with a Chinese fallback message embedded in `response`, whereas
/api/user_message (web_bp) returns 500. Same underlying failure, two
different HTTP contracts — both are tested explicitly here and there.
"""
import pytest

from api.flask_app.models import UserInput, db
from helpers import make_openai_client_mock, route_module

ai_bp_module = route_module("ai_bp")


class TestAiEndpoint:
    def test_non_json_body_returns_400(self, client):
        resp = client.post("/api/ai", data="not json", content_type="text/plain")

        assert resp.status_code == 400
        assert resp.get_json() == {"error": "請傳入 JSON body"}

    def test_invalid_text_field_returns_400(self, client):
        resp = client.post("/api/ai", json={"text": ""})

        assert resp.status_code == 400
        assert resp.get_json() == {"error": "請輸入文字訊息"}

    def test_wrong_field_name_user_input_is_treated_as_empty_text(self, client):
        # ai_bp reads data.get("text", ""), NOT "user_input" like web_bp does
        # — sending "user_input" here still hits the empty-text branch.
        resp = client.post("/api/ai", json={"user_input": "請問租屋糾紛怎麼處理"})

        assert resp.status_code == 400
        assert resp.get_json() == {"error": "請輸入文字訊息"}

    def test_valid_text_ai_success_returns_200(self, client, mocker):
        mocker.patch.object(ai_bp_module, "get_openai_response", return_value="這是 AI 回答")

        resp = client.post("/api/ai", json={"text": "請問租屋糾紛怎麼處理"})

        assert resp.status_code == 200
        assert resp.get_json() == {"response": "這是 AI 回答"}

    def test_ai_exception_returns_200_with_fallback_not_500(self, client, mocker):
        # Divergent from web_bp's /api/user_message, which returns 500 for
        # the identical underlying failure — see test_routes_web.py.
        mocker.patch.object(
            ai_bp_module, "get_openai_response", side_effect=RuntimeError("AI down")
        )

        resp = client.post("/api/ai", json={"text": "請問租屋糾紛怎麼處理"})

        assert resp.status_code == 200
        assert resp.get_json() == {"response": "AI 發生錯誤，請稍後再試。"}

    def test_does_not_persist_to_database(self, client, app_context, mocker):
        mocker.patch.object(ai_bp_module, "get_openai_response", return_value="這是 AI 回答")

        client.post("/api/ai", json={"text": "請問租屋糾紛怎麼處理"})

        assert db.session.query(UserInput).count() == 0


class TestTestOpenaiKey:
    def test_success_returns_stripped_result(self, client, mocker):
        mocker.patch.object(
            ai_bp_module, "OpenAI", return_value=make_openai_client_mock(" hello world ")
        )

        resp = client.get("/api/test_openai_key")

        assert resp.status_code == 200
        assert resp.get_json() == {"success": True, "result": "hello world"}

    def test_constructor_exception_propagates_uncaught(self, client, mocker):
        # `client = OpenAI(api_key=api_key)` sits OUTSIDE the try block in
        # ai_bp.py, same pattern as core/ai.py — a constructor failure isn't
        # caught by this route either, so it propagates rather than
        # producing a {"success": False, ...} response. TESTING=True means
        # this surfaces as a raised exception, not a 500 response — same
        # reasoning as test_routes_linebot.py's unhandled-exception test.
        mocker.patch.object(
            ai_bp_module, "OpenAI", side_effect=Exception("invalid api key format")
        )

        with pytest.raises(Exception, match="invalid api key format"):
            client.get("/api/test_openai_key")

    def test_create_call_exception_returns_success_false(self, client, mocker):
        fake_client = make_openai_client_mock("unused")
        fake_client.chat.completions.create.side_effect = Exception("401 Unauthorized")
        mocker.patch.object(ai_bp_module, "OpenAI", return_value=fake_client)

        resp = client.get("/api/test_openai_key")

        assert resp.status_code == 200
        assert resp.get_json() == {"success": False, "error": "401 Unauthorized"}
