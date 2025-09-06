from flask import Blueprint, request, current_app
import json
import concurrent.futures
from core.security import validate_signature
from core.line_api import send_line_reply, send_line_push
from core.ai import get_openai_response
from models import db, User, UserInput
from core.validation import validate_input_text
from flask import abort

linebot_bp = Blueprint('linebot_bp', __name__)

@linebot_bp.route("/callback", methods=['POST'])
def callback():
    """LINE Bot webhook callback"""
    
    # Get signature and body
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    
    # Validate signature
    if not validate_signature(request.get_data(), signature):
        current_app.logger.error("簽名驗證失敗")
        abort(400, "Invalid signature")
    
    # Parse event data
    try:
        event_data = json.loads(body)
    except json.JSONDecodeError:
        current_app.logger.error("JSON 解析失敗")
        abort(400, "Invalid JSON")
    
    if "events" not in event_data:
        current_app.logger.error("訊息事件無法解析")
        abort(400, "No events found")
    
    if not event_data["events"]:
        current_app.logger.info("events 為空")
        return "OK", 200
    
    # Process first event
    event = event_data["events"][0]
    
    event_type = event.get("type")
    message_type = event.get("message", {}).get("type")
    
    if not event_type or not message_type:
        current_app.logger.error("訊息類型無法解析")
        abort(400, "Invalid event or message type")
    
    if event_type != "message":
        current_app.logger.info("非訊息事件")
        return "OK", 200
    
    if message_type != "text":
        send_line_reply(current_app.config['CHANNEL_ACCESS_TOKEN'], event["replyToken"], "請輸入文字訊息")
        return "OK", 200
    
    # Extract and validate message
    user_text = event["message"]["text"]
    user_id = event["source"]["userId"]
    reply_token = event["replyToken"]
    
    # Validate input text
    try:
        validated_text = validate_input_text(user_text)
    except Exception as e:
        send_line_reply(current_app.config['CHANNEL_ACCESS_TOKEN'], reply_token, str(e))
        return "OK", 200
    
    # Create user if needed
    if not User.exists(user_id):
        User.create(user_id)
    
    # Simple reply for now
    send_line_reply(current_app.config['CHANNEL_ACCESS_TOKEN'], reply_token, "收到訊息：" + validated_text)
    
    return "OK", 200