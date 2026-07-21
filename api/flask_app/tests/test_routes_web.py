"""routes/web_bp.py — POST /api/user_message.

Contrast with test_routes_ai.py: this route returns 500 when the AI call
fails, whereas ai_bp's /api/ai returns 200 with a fallback message for the
same failure. Both test files reference each other for that divergence.
"""
from api.flask_app.models import UserInput, db
from helpers import route_module

web_bp_module = route_module("web_bp")


class TestUserMessage:
    def test_non_json_body_returns_400(self, client):
        resp = client.post("/api/user_message", data="not json", content_type="text/plain")

        assert resp.status_code == 400
        assert resp.get_json() == {"error": "請傳入 JSON body"}

    def test_invalid_input_returns_400_with_spamfilter_message(self, client):
        resp = client.post("/api/user_message", json={"user_input": ""})

        assert resp.status_code == 400
        assert resp.get_json() == {"error": "請輸入文字訊息"}

    def test_valid_input_anonymous_returns_200_and_does_not_persist(self, client, app_context, mocker):
        mocker.patch.object(web_bp_module, "get_openai_response", return_value="這是 AI 回答")

        resp = client.post("/api/user_message", json={"user_input": "請問租屋糾紛怎麼處理"})

        assert resp.status_code == 200
        assert resp.get_json() == {"response": "這是 AI 回答"}
        assert db.session.query(UserInput).count() == 0

    def test_valid_input_logged_in_persists_user_input(self, logged_in_client, app_context, mocker):
        mocker.patch.object(web_bp_module, "get_openai_response", return_value="這是 AI 回答")

        resp = logged_in_client.post("/api/user_message", json={"user_input": "請問租屋糾紛怎麼處理"})

        assert resp.status_code == 200
        row = db.session.query(UserInput).first()
        assert row is not None
        assert row.input_text == "請問租屋糾紛怎麼處理"
        assert row.ai_response == "這是 AI 回答"

    def test_ai_exception_returns_500(self, client, mocker):
        mocker.patch.object(
            web_bp_module, "get_openai_response", side_effect=RuntimeError("AI down")
        )

        resp = client.post("/api/user_message", json={"user_input": "請問租屋糾紛怎麼處理"})

        assert resp.status_code == 500
        assert resp.get_json() == {"error": "AI 發生錯誤，請稍後再試。"}

    def test_logged_in_db_commit_failure_still_returns_200(self, logged_in_client, app_context, mocker):
        mocker.patch.object(web_bp_module, "get_openai_response", return_value="這是 AI 回答")
        mocker.patch.object(db.session, "commit", side_effect=RuntimeError("db write failed"))

        resp = logged_in_client.post("/api/user_message", json={"user_input": "請問租屋糾紛怎麼處理"})

        assert resp.status_code == 200
        assert resp.get_json() == {"response": "這是 AI 回答"}
