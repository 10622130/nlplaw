"""services/linebot_service.py

Unlike exam_service._send, `_send_reply` here calls `send_line_reply` via the
module-level `from core.line_api import send_line_reply` import with no local
shadowing re-import, so it's patched at
`api.flask_app.services.linebot_service.send_line_reply` directly.
"""
from unittest.mock import MagicMock

from api.flask_app.models import ExamSession, User, UserInput, db
from api.flask_app.services.exam_service import SUBJECTS
from api.flask_app.services.linebot_service import (
    NON_TEXT_MESSAGE_WARNING,
    WELCOME_MESSAGE,
    _get_ai_response,
    _send_reply,
    handle_follow_event,
    handle_non_text_message,
    handle_text_message,
)


class TestHandleNonTextMessage:
    def test_sends_plain_text_warning(self, app_context, mocker):
        send = mocker.patch(
            "api.flask_app.services.linebot_service.send_line_reply",
            return_value=(MagicMock(), 200),
        )

        handle_non_text_message("reply-token")

        send.assert_called_once()
        args = send.call_args[0]
        assert args[1] == "reply-token"
        assert args[2] == NON_TEXT_MESSAGE_WARNING == "請輸入純文字訊息"


class TestHandleFollowEvent:
    def test_new_user_is_created_and_receives_welcome_message(self, app_context, mocker):
        user_id = "Ufollownew001"
        send = mocker.patch(
            "api.flask_app.services.linebot_service.send_line_reply",
            return_value=(MagicMock(), 200),
        )

        handle_follow_event(user_id, "reply-token")

        assert User.exists(user_id) is True
        send.assert_called_once()
        args = send.call_args[0]
        assert args[1] == "reply-token"
        assert args[2] == WELCOME_MESSAGE

    def test_existing_user_is_not_duplicated(self, app_context, make_user, mocker):
        user_id = make_user()
        send = mocker.patch(
            "api.flask_app.services.linebot_service.send_line_reply",
            return_value=(MagicMock(), 200),
        )

        handle_follow_event(user_id, "reply-token")  # must not raise IntegrityError

        send.assert_called_once()


class TestHandleTextMessageDispatch:
    def test_subject_text_dispatches_to_subject_selection(self, app_context, mocker):
        mock_subject = mocker.patch("api.flask_app.services.linebot_service.handle_subject_selection")
        mock_year = mocker.patch("api.flask_app.services.linebot_service.handle_year_subject")
        mock_answer = mocker.patch("api.flask_app.services.linebot_service.handle_answer")

        handle_text_message("Udispatch1", SUBJECTS[0], "reply-token")

        mock_subject.assert_called_once_with(SUBJECTS[0], "reply-token")
        mock_year.assert_not_called()
        mock_answer.assert_not_called()

    def test_year_subject_text_dispatches_to_handle_year_subject(self, app_context, mocker):
        mock_subject = mocker.patch("api.flask_app.services.linebot_service.handle_subject_selection")
        mock_year = mocker.patch("api.flask_app.services.linebot_service.handle_year_subject")
        mock_answer = mocker.patch("api.flask_app.services.linebot_service.handle_answer")
        text = f"112 {SUBJECTS[0]}"

        handle_text_message("Udispatch2", text, "reply-token")

        mock_year.assert_called_once_with("Udispatch2", text, "reply-token")
        mock_subject.assert_not_called()
        mock_answer.assert_not_called()

    def test_option_letter_with_pending_exam_session_dispatches_to_handle_answer(
        self, app_context, make_user, mocker
    ):
        user_id = make_user()
        ExamSession.set(user_id, "A")
        mock_subject = mocker.patch("api.flask_app.services.linebot_service.handle_subject_selection")
        mock_year = mocker.patch("api.flask_app.services.linebot_service.handle_year_subject")
        mock_answer = mocker.patch("api.flask_app.services.linebot_service.handle_answer")

        handle_text_message(user_id, "A", "reply-token")

        mock_answer.assert_called_once_with(user_id, "A", "reply-token")
        mock_subject.assert_not_called()
        mock_year.assert_not_called()

    def test_option_letter_without_pending_exam_session_falls_through_to_ai_branch(
        self, app_context, make_user, mocker
    ):
        # "A" alone matches neither SUBJECT_RE nor YEAR_SUBJECT_RE, and is in
        # OPTIONS — but with no ExamSession row, the guard
        # `ExamSession.get_answer(user_id) is not None` is False, so this
        # must fall through to the AI-question branch, not handle_answer.
        user_id = make_user()
        mock_answer = mocker.patch("api.flask_app.services.linebot_service.handle_answer")
        mock_validate = mocker.patch(
            "api.flask_app.services.linebot_service.validate_input_text",
            return_value=(False, "驗證失敗訊息"),
        )
        mock_send_reply = mocker.patch("api.flask_app.services.linebot_service._send_reply")

        handle_text_message(user_id, "A", "reply-token")

        mock_answer.assert_not_called()
        mock_validate.assert_called_once_with("A")
        mock_send_reply.assert_called_once_with("reply-token", "驗證失敗訊息")

    def test_plain_valid_question_calls_ai_and_sends_reply(self, app_context, make_user, mocker):
        user_id = make_user()
        mocker.patch(
            "api.flask_app.services.linebot_service.get_openai_response",
            return_value="這是 AI 的回答",
        )
        send = mocker.patch("api.flask_app.services.linebot_service._send_reply")

        handle_text_message(user_id, "請問租屋糾紛怎麼處理", "reply-token")

        send.assert_called_once_with("reply-token", "這是 AI 的回答")
        row = db.session.query(UserInput).filter_by(user_id=user_id).first()
        assert row is not None
        assert row.ai_response == "這是 AI 的回答"

    def test_invalid_text_sends_validation_error_without_calling_ai(self, app_context, make_user, mocker):
        user_id = make_user()
        mock_ai = mocker.patch("api.flask_app.services.linebot_service.get_openai_response")
        send = mocker.patch("api.flask_app.services.linebot_service._send_reply")

        handle_text_message(user_id, "a", "reply-token")  # non-Chinese, fails validation

        mock_ai.assert_not_called()
        send.assert_called_once_with("reply-token", "請用中文輸入台灣法律相關問題")


class TestGetAiResponse:
    def test_success_persists_user_input_row(self, app_context, make_user, mocker):
        user_id = make_user()
        mocker.patch(
            "api.flask_app.services.linebot_service.get_openai_response",
            return_value="AI 回答內容",
        )

        result = _get_ai_response(user_id, "驗證後的文字")

        assert result == "AI 回答內容"
        row = db.session.query(UserInput).filter_by(user_id=user_id).first()
        assert row.input_text == "驗證後的文字"
        assert row.ai_response == "AI 回答內容"

    def test_ai_failure_returns_fallback_without_persisting(self, app_context, make_user, mocker):
        user_id = make_user()
        mocker.patch(
            "api.flask_app.services.linebot_service.get_openai_response",
            side_effect=RuntimeError("AI down"),
        )

        result = _get_ai_response(user_id, "會失敗的文字")

        assert result == "AI 發生錯誤，請稍後再試。"
        row = db.session.query(UserInput).filter_by(user_id=user_id).first()
        assert row is None

    def test_db_commit_failure_rolls_back_and_returns_fallback(self, app_context, make_user, mocker):
        # Documents a real product behavior: even a good AI answer is
        # discarded if persisting it fails.
        user_id = make_user()
        mocker.patch(
            "api.flask_app.services.linebot_service.get_openai_response",
            return_value="這個回答會被丟棄",
        )
        mocker.patch.object(db.session, "commit", side_effect=RuntimeError("db write failed"))

        result = _get_ai_response(user_id, "會 commit 失敗的文字")

        assert result == "AI 發生錯誤，請稍後再試。"
        row = db.session.query(UserInput).filter_by(user_id=user_id).first()
        assert row is None


class TestSendReply:
    def test_success_does_not_raise(self, app_context, mocker):
        mocker.patch(
            "api.flask_app.services.linebot_service.send_line_reply",
            return_value=(MagicMock(), 200),
        )
        _send_reply("reply-token", "some text")

    def test_non_200_logs_error_without_raising(self, app_context, mocker):
        mocker.patch(
            "api.flask_app.services.linebot_service.send_line_reply",
            return_value=(MagicMock(text="Bad Request"), 400),
        )
        _send_reply("reply-token", "some text")
