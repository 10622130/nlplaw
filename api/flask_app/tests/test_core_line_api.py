"""core/line_api.py — LINE Messaging API / OAuth HTTP wrappers.

All requests.post/.get calls are mocked directly at `core.line_api.requests`
(the module-level `import requests`), establishing the patching pattern
reused by test_core_exam_api.py and, at a higher level, by the service/route
tests.
"""
import pytest
import requests

from core.line_api import (
    exchange_code_for_token,
    get_line_profile,
    send_line_reply,
    send_reply_messages,
    text_message,
    text_with_quick_reply,
)
from helpers import make_requests_response_mock


class TestMessageBuilders:
    def test_text_message_shape(self):
        assert text_message("hello") == {"type": "text", "text": "hello"}

    def test_text_with_quick_reply_shape(self):
        msg = text_with_quick_reply("pick one", [("A", "reply-a"), ("B", "reply-b")])
        assert msg == {
            "type": "text",
            "text": "pick one",
            "quickReply": {
                "items": [
                    {"type": "action", "action": {"type": "message", "label": "A", "text": "reply-a"}},
                    {"type": "action", "action": {"type": "message", "label": "B", "text": "reply-b"}},
                ]
            },
        }


class TestSendReplyMessages:
    def test_success_returns_response_and_status(self, mocker):
        mock_resp = make_requests_response_mock(status_code=200)
        mocker.patch("core.line_api.requests.post", return_value=mock_resp)

        resp, status = send_reply_messages("token", "reply-token", [text_message("hi")])

        assert status == 200
        assert resp is mock_resp

    def test_non_200_does_not_raise(self, mocker):
        mock_resp = make_requests_response_mock(status_code=400, text="Bad Request")
        mocker.patch("core.line_api.requests.post", return_value=mock_resp)

        resp, status = send_reply_messages("token", "reply-token", [text_message("hi")])

        assert status == 400
        assert resp.text == "Bad Request"


class TestSendLineReply:
    def test_delegates_to_send_reply_messages_with_single_text_message(self, mocker):
        mock_resp = make_requests_response_mock(status_code=200)
        post = mocker.patch("core.line_api.requests.post", return_value=mock_resp)

        send_line_reply("token", "reply-token", "hello there")

        _, kwargs = post.call_args
        assert kwargs["json"]["messages"] == [{"type": "text", "text": "hello there"}]
        assert kwargs["json"]["replyToken"] == "reply-token"


class TestExchangeCodeForToken:
    def test_success_returns_access_token(self, mocker):
        mock_resp = make_requests_response_mock(json_data={"access_token": "tok123"})
        mocker.patch("core.line_api.requests.post", return_value=mock_resp)

        token = exchange_code_for_token(
            code="code123",
            redirect_uri="http://localhost/cb",
            client_id="cid",
            client_secret="csecret",
        )

        assert token == "tok123"

    def test_http_error_propagates(self, mocker):
        mock_resp = make_requests_response_mock(
            raise_for_status_effect=requests.HTTPError("401 Unauthorized")
        )
        mocker.patch("core.line_api.requests.post", return_value=mock_resp)

        with pytest.raises(requests.HTTPError):
            exchange_code_for_token(
                code="bad", redirect_uri="http://localhost/cb", client_id="cid", client_secret="csecret"
            )


class TestGetLineProfile:
    def test_success_returns_profile_dict(self, mocker):
        mock_resp = make_requests_response_mock(
            json_data={"userId": "U1", "displayName": "Test Name"}
        )
        mocker.patch("core.line_api.requests.get", return_value=mock_resp)

        profile = get_line_profile("access-token")

        assert profile == {"userId": "U1", "displayName": "Test Name"}

    def test_http_error_propagates(self, mocker):
        mock_resp = make_requests_response_mock(
            raise_for_status_effect=requests.HTTPError("401 Unauthorized")
        )
        mocker.patch("core.line_api.requests.get", return_value=mock_resp)

        with pytest.raises(requests.HTTPError):
            get_line_profile("bad-token")
