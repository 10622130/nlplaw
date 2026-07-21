"""routes/linebot_bp.py — POST /callback (LINE webhook).

Signature checks use a real HMAC-SHA256 computed with the test
CHANNEL_SECRET (via helpers.compute_line_signature), not a mocked
validate_signature, so these tests exercise the actual crypto path end to
end.

Note on the unhandled-exception test: the `app` fixture sets `TESTING=True`,
and Flask defaults `PROPAGATE_EXCEPTIONS` to True whenever TESTING/DEBUG is
True. That means an unhandled exception raised inside a view during a test
client call propagates as a real Python exception out of `client.post(...)`
rather than being turned into a 500 response — so this is asserted with
`pytest.raises`, not by checking `resp.status_code`.
"""
import json

import pytest

from api.flask_app.models import ProcessedEvent
from helpers import compute_line_signature, route_module

linebot_bp_module = route_module("linebot_bp")


def _text_event(user_id, text, reply_token, webhook_event_id=None):
    event = {
        "type": "message",
        "message": {"type": "text", "text": text},
        "replyToken": reply_token,
        "source": {"userId": user_id},
    }
    if webhook_event_id is not None:
        event["webhookEventId"] = webhook_event_id
    return event


def _sticker_event(user_id, reply_token, webhook_event_id=None):
    event = {
        "type": "message",
        "message": {"type": "sticker", "packageId": "1", "stickerId": "1"},
        "replyToken": reply_token,
        "source": {"userId": user_id},
    }
    if webhook_event_id is not None:
        event["webhookEventId"] = webhook_event_id
    return event


def _follow_event(user_id, reply_token, webhook_event_id=None):
    event = {"type": "follow", "replyToken": reply_token, "source": {"userId": user_id}}
    if webhook_event_id is not None:
        event["webhookEventId"] = webhook_event_id
    return event


def _post_callback(client, events):
    body = json.dumps({"events": events}).encode("utf-8")
    headers = {"X-Line-Signature": compute_line_signature(body)}
    return client.post("/callback", data=body, headers=headers, content_type="application/json")


class TestCallbackSignatureAndParsing:
    def test_invalid_signature_returns_400(self, client, mocker):
        handle = mocker.patch.object(linebot_bp_module, "handle_text_message")
        body = json.dumps({"events": [_text_event("U1", "hi", "rt1")]}).encode("utf-8")

        resp = client.post(
            "/callback", data=body, headers={"X-Line-Signature": "not-a-real-signature"},
            content_type="application/json",
        )

        assert resp.status_code == 400
        handle.assert_not_called()

    def test_missing_signature_header_returns_400(self, client, mocker):
        handle = mocker.patch.object(linebot_bp_module, "handle_text_message")
        body = json.dumps({"events": [_text_event("U1", "hi", "rt1")]}).encode("utf-8")

        resp = client.post("/callback", data=body, content_type="application/json")

        assert resp.status_code == 400
        handle.assert_not_called()

    def test_malformed_json_returns_400(self, client):
        body = b"not valid json{"
        headers = {"X-Line-Signature": compute_line_signature(body)}

        resp = client.post("/callback", data=body, headers=headers, content_type="application/json")

        assert resp.status_code == 400


class TestCallbackDispatch:
    def test_text_message_event_dispatches_to_handle_text_message(self, client, mocker):
        handle = mocker.patch.object(linebot_bp_module, "handle_text_message")

        resp = _post_callback(client, [_text_event("Udispatch1", "哈囉", "rt1")])

        assert resp.status_code == 200
        assert resp.get_data(as_text=True) == "OK"
        handle.assert_called_once_with(user_id="Udispatch1", user_text="哈囉", reply_token="rt1")

    def test_follow_event_dispatches_to_handle_follow_event(self, client, mocker):
        follow = mocker.patch.object(linebot_bp_module, "handle_follow_event")

        resp = _post_callback(client, [_follow_event("Ufollow1", "rt1")])

        assert resp.status_code == 200
        follow.assert_called_once_with(user_id="Ufollow1", reply_token="rt1")

    def test_unknown_event_type_is_ignored_but_still_returns_200(self, client, mocker):
        handle = mocker.patch.object(linebot_bp_module, "handle_text_message")
        follow = mocker.patch.object(linebot_bp_module, "handle_follow_event")

        resp = _post_callback(client, [{"type": "unsend"}])

        assert resp.status_code == 200
        handle.assert_not_called()
        follow.assert_not_called()

    def test_non_text_message_prompts_for_plain_text_and_returns_200(self, client, mocker):
        handle = mocker.patch.object(linebot_bp_module, "handle_text_message")
        non_text = mocker.patch.object(linebot_bp_module, "handle_non_text_message")

        resp = _post_callback(client, [_sticker_event("Usticker1", "rt1")])

        assert resp.status_code == 200
        handle.assert_not_called()
        non_text.assert_called_once_with(reply_token="rt1")


class TestCallbackIdempotency:
    def test_duplicate_webhook_event_id_is_handled_only_once(self, client, app_context, mocker):
        handle = mocker.patch.object(linebot_bp_module, "handle_text_message")
        event = _text_event("Uidem1", "哈囉", "rt1", webhook_event_id="evt-dup-1")

        resp1 = _post_callback(client, [event])
        resp2 = _post_callback(client, [event])

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        handle.assert_called_once_with(user_id="Uidem1", user_text="哈囉", reply_token="rt1")
        assert ProcessedEvent.exists("evt-dup-1") is True

    def test_event_without_webhook_event_id_is_handled_every_time(self, client, mocker):
        handle = mocker.patch.object(linebot_bp_module, "handle_text_message")
        event = _text_event("Uidem2", "哈囉", "rt1")  # no webhookEventId

        _post_callback(client, [event])
        _post_callback(client, [event])

        assert handle.call_count == 2


class TestCallbackUnhandledException:
    def test_exception_from_service_propagates(self, client, mocker):
        mocker.patch.object(
            linebot_bp_module, "handle_text_message", side_effect=RuntimeError("service exploded")
        )
        event = _text_event("Uexc1", "哈囉", "rt1", webhook_event_id="evt-exc-1")

        with pytest.raises(RuntimeError):
            _post_callback(client, [event])
