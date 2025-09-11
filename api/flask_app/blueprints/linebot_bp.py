from flask import Blueprint, request, current_app
import json
from core.security import validate_signature
from core.line_api import send_line_reply, send_line_push
from core.ai import get_openai_response
from api.flask_app.models import db, User, UserInput
from core.spamfilter import validate_input_text
from flask import abort


linebot_bp = Blueprint('linebot_bp', __name__)



@linebot_bp.route("/callback", methods=['POST'])
def callback():
    """LINE Bot webhook callback"""
    current_app.logger.info("Webhook received")
    try:
        # Get signature and body
        signature = request.headers.get('X-Line-Signature')
        body = request.get_data(as_text=True)
        
        # Validate signature
        if not validate_signature(request.get_data(), signature):
            current_app.logger.error("Invalid signature")
            abort(400, "Invalid signature")
        
        # Parse event data
        try:
            event_data = json.loads(body)
        except json.JSONDecodeError:
            abort(400, "Invalid JSON")
        
        if "events" not in event_data:
            current_app.logger.error("No events found")
            abort(400, "No events found")
        
        if not event_data["events"]:
            current_app.logger.info("events is empty")
            return "OK", 200
        
        # Process first event
        
        event = event_data["events"][0]

        event_type = event.get("type")
        message_type = event.get("message", {}).get("type")
        
        if not event_type or not message_type:
            current_app.logger.error("Invalid event or message type")
            abort(400, "Invalid event or message type")
        
        if event_type != "message":
            current_app.logger.info("not message event")
            print("not message event")
            return "OK", 200
        
        if message_type != "text":
            current_app.logger.info("not text message")
            print("not text message")
            return "OK", 200
        
        # Extract and validate message
        user_text = event["message"]["text"]
        user_id = event["source"]["userId"]
        reply_token = event["replyToken"]
        
        # Validate input text
        respond_text = get_openai_response(validate_input_text(user_text))
        
        # Create user if needed
        if not User.exists(user_id):
            User.create(user_id)
        
        # Simple reply for now
        response = send_line_reply(current_app.config['CHANNEL_ACCESS_TOKEN'], reply_token, respond_text)
        current_app.logger.info(f"LINE reply status: {response.status_code}, body: {response.text}")
        
        return "OK", 200
    except Exception as e:
        print("Exception in callback:", e)
        current_app.logger.error(f"Exception in callback: {e}")
        return "ERROR", 500