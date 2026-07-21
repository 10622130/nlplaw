"""services/exam_service.py

IMPORTANT mocking quirk: `_send()` (exam_service.py line 72) does a LOCAL
`from core.line_api import send_reply_messages` inside the function body,
which shadows the module-level import on line 5. That means patching
`api.flask_app.services.exam_service.send_reply_messages` has NO EFFECT on
`_send()` — every test here must patch `core.line_api.send_reply_messages`
instead. `get_random_question`, in contrast, is called directly via its
module-level imported name with no such shadowing, so it IS patched at
`api.flask_app.services.exam_service.get_random_question`.
"""
from api.flask_app.models import ExamSession
from api.flask_app.services.exam_service import (
    SUBJECT_RE,
    SUBJECTS,
    YEAR_SUBJECT_RE,
    YEARS,
    handle_answer,
    handle_subject_selection,
    handle_year_subject,
)
from helpers import make_requests_response_mock


class TestSubjectRegex:
    def test_matches_each_exact_subject(self):
        for subject in SUBJECTS:
            assert SUBJECT_RE.match(subject) is not None

    def test_does_not_match_partial_text(self):
        assert SUBJECT_RE.match(SUBJECTS[0][:5]) is None

    def test_does_not_match_garbage(self):
        assert SUBJECT_RE.match("隨便打的文字") is None


class TestYearSubjectRegex:
    def test_matches_valid_year_and_subject(self):
        assert YEAR_SUBJECT_RE.match(f"112 {SUBJECTS[0]}") is not None

    def test_matches_lower_boundary_year_103(self):
        assert YEAR_SUBJECT_RE.match(f"103 {SUBJECTS[0]}") is not None

    def test_matches_upper_boundary_year_112(self):
        assert YEAR_SUBJECT_RE.match(f"112 {SUBJECTS[0]}") is not None

    def test_does_not_match_year_below_range(self):
        assert YEAR_SUBJECT_RE.match(f"102 {SUBJECTS[0]}") is None

    def test_does_not_match_year_above_range(self):
        assert YEAR_SUBJECT_RE.match(f"113 {SUBJECTS[0]}") is None

    def test_does_not_match_missing_space(self):
        assert YEAR_SUBJECT_RE.match(f"112{SUBJECTS[0]}") is None

    def test_does_not_match_wrong_subject_text(self):
        assert YEAR_SUBJECT_RE.match("112 不存在的科目") is None


class TestHandleSubjectSelection:
    def test_sends_year_quick_reply_buttons(self, app_context, mocker):
        mock_resp = make_requests_response_mock(status_code=200)
        send = mocker.patch("core.line_api.send_reply_messages", return_value=(mock_resp, 200))

        handle_subject_selection(SUBJECTS[0], "reply-token")

        send.assert_called_once()
        token, reply_token, messages = send.call_args[0]
        assert reply_token == "reply-token"
        assert len(messages) == 1
        buttons = messages[0]["quickReply"]["items"]
        assert len(buttons) == len(YEARS)
        assert buttons[0]["action"]["text"] == f"{YEARS[0]} {SUBJECTS[0]}"


class TestHandleYearSubject:
    def test_success_stores_answer_and_sends_question(self, app_context, make_user, mocker):
        user_id = make_user()
        mock_resp = make_requests_response_mock(status_code=200)
        send = mocker.patch("core.line_api.send_reply_messages", return_value=(mock_resp, 200))
        mocker.patch(
            "api.flask_app.services.exam_service.get_random_question",
            return_value={"question": "民法上的不當得利是什麼？", "answer": "B"},
        )

        handle_year_subject(user_id, f"112 {SUBJECTS[0]}", "reply-token")

        assert ExamSession.get_answer(user_id) == "B"
        send.assert_called_once()
        _, _, messages = send.call_args[0]
        assert messages[0]["text"] == "民法上的不當得利是什麼？"
        labels = [item["action"]["label"] for item in messages[0]["quickReply"]["items"]]
        assert labels == ["A", "B", "C", "D"]

    def test_exam_api_exception_sends_failure_message_and_does_not_set_session(
        self, app_context, make_user, mocker
    ):
        user_id = make_user()
        mock_resp = make_requests_response_mock(status_code=200)
        send = mocker.patch("core.line_api.send_reply_messages", return_value=(mock_resp, 200))
        mocker.patch(
            "api.flask_app.services.exam_service.get_random_question",
            side_effect=RuntimeError("exam API down"),
        )

        handle_year_subject(user_id, f"112 {SUBJECTS[0]}", "reply-token")

        assert ExamSession.get_answer(user_id) is None
        send.assert_called_once()
        _, _, messages = send.call_args[0]
        assert messages == [{"type": "text", "text": "題目取得失敗，請稍後再試。"}]


class TestHandleAnswer:
    def test_correct_answer(self, app_context, make_user, mocker):
        user_id = make_user()
        ExamSession.set(user_id, "A")
        mock_resp = make_requests_response_mock(status_code=200)
        send = mocker.patch("core.line_api.send_reply_messages", return_value=(mock_resp, 200))

        handle_answer(user_id, "A", "reply-token")

        _, _, messages = send.call_args[0]
        assert messages == [{"type": "text", "text": "恭喜你答對了！"}]
        assert ExamSession.get_answer(user_id) is None

    def test_incorrect_answer(self, app_context, make_user, mocker):
        user_id = make_user()
        ExamSession.set(user_id, "A")
        mock_resp = make_requests_response_mock(status_code=200)
        send = mocker.patch("core.line_api.send_reply_messages", return_value=(mock_resp, 200))

        handle_answer(user_id, "B", "reply-token")

        _, _, messages = send.call_args[0]
        assert messages == [{"type": "text", "text": "答錯了⋯答案是 A"}]
        assert ExamSession.get_answer(user_id) is None

    def test_no_pending_question(self, app_context, make_user, mocker):
        user_id = make_user()
        mock_resp = make_requests_response_mock(status_code=200)
        send = mocker.patch("core.line_api.send_reply_messages", return_value=(mock_resp, 200))

        handle_answer(user_id, "A", "reply-token")

        _, _, messages = send.call_args[0]
        assert messages == [{"type": "text", "text": "目前沒有待作答的題目，請先選擇科目與年份。"}]
