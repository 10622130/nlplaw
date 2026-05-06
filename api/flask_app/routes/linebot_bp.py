from flask import Blueprint, request, current_app, abort
import json
from core.security import validate_signature
from api.flask_app.services.linebot_service import handle_text_message


linebot_bp = Blueprint('linebot_bp', __name__)


@linebot_bp.route("/callback", methods=['POST'])
def callback():
    """LINE Bot webhook callback — validates signature then dispatches events."""
    signature = request.headers.get('X-Line-Signature')
    raw_body = request.get_data()

    if not validate_signature(raw_body, signature):
        current_app.logger.error("Invalid signature")
        abort(400, "Invalid signature")

    try:
        event_data = json.loads(raw_body)
    except json.JSONDecodeError:
        abort(400, "Invalid JSON")

    for event in event_data.get("events", []):
        _handle_event(event)

    return "OK", 200


def _handle_event(event):
    event_type = event.get("type")
    if event_type == "message":
        _handle_message_event(event)
    else:
        current_app.logger.info(f"Ignored event type: {event_type}")


def _handle_message_event(event):
    if event.get("message", {}).get("type") != "text":
        current_app.logger.info("Ignored non-text message")
        return

    handle_text_message(
        user_id=event["source"]["userId"],
        user_text=event["message"]["text"],
        reply_token=event["replyToken"],
    )