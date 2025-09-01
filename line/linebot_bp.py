# linebot_bp.py
from flask import Blueprint, request, current_app
import requests
import json
import hmac
import hashlib
import base64
from models import db, User, UserInput
from ai_bp import get_openai_response  # 此處用來取得 AI 回應
from spamfilter import is_valid_text

linebot_bp = Blueprint('linebot_bp', __name__)

def validate_signature(body, signature):
    """
    驗證簽名是否有效
    """
    try:
        # 從 current_app.config 取得 Channel Secret
        channel_secret = current_app.config['CHANNEL_SECRET']
        # 使用 Channel Secret 和 body 計算簽名 
        hash = hmac.new(channel_secret.encode('utf-8'),
                        body,  
                        hashlib.sha256).digest()
        expected_signature = base64.b64encode(hash).decode('utf-8')  # byte data 轉成 string

        # 使用 hmac.compare_digest() 進行安全比較
        if hmac.compare_digest(expected_signature, signature):
            return True
        else:
            current_app.logger.error(f"Expected Signature: {expected_signature}, Received: {signature}")
            return False
    except Exception as e:
        current_app.logger.error(f"Error during signature validation: {e}")
        return False

def send_line_reply(reply_token, text):
    """發送 LINE 回應訊息"""
    channel_access_token = current_app.config["CHANNEL_ACCESS_TOKEN"]
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        current_app.logger.error(f"Error sending message: {response.text}")

def send_line_push(user_id, text):
    """用 LINE push API 主動推播訊息"""
    channel_access_token = current_app.config["CHANNEL_ACCESS_TOKEN"]
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        current_app.logger.error(f"Error sending push message: {response.text}")

@linebot_bp.route("/callback", methods=['POST'])
def callback():
    import concurrent.futures

    MAX_TEXT_LENGTH = 205  # 設定最大訊息長度

    signature = request.headers.get('X-Line-Signature')
    # 取得原始 bytes 資料供驗證用
    body = request.get_data(as_text=True)

    if not validate_signature(request.get_data(), signature):
        current_app.logger.error("簽名驗證失敗")
        return "Invalid signature", 400

    # 轉換成文字格式後解析 JSON
    event_data = json.loads(body)
    if "events" not in event_data:
        current_app.logger.error("訊息事件無法解析")
        return "No events found", 400

    if not event_data["events"]:
        current_app.logger.info(" (events 為空)")
        return "OK", 200

    event = event_data["events"][0]  # 避免索引錯誤

    event_type = event.get("type")
    message_type = event.get("message", {}).get("type")

    if not event_type or not message_type:
        current_app.logger.error("訊息類型無法解析")
        return "Invalid event or message type", 400

    if event_type != "message":
        current_app.logger.error("非訊息事件")
        return "No message event", 200

    if message_type != "text":
        send_line_reply(event["replyToken"], "請輸入文字訊息")
        return "Non-text message received", 200

    user_text = event["message"]["text"]
    user_id = event["source"]["userId"]
    reply_token = event["replyToken"]

    if len(user_text) > MAX_TEXT_LENGTH:
        send_line_reply(reply_token, "請將問題縮短至200字以內")
        return "Message too long", 200

    if not is_valid_text(user_text):
        send_line_reply(reply_token, "請用中文輸入台灣法律相關問題")
        return "Invalid text", 200

    # 檢查使用者是否存在，若無則建立新使用者
    user = User.query.get(user_id)
    if not user:
        user = User(id=user_id)
        db.session.add(user)
        db.session.commit()

    # --- 多執行緒處理 AI 回覆與資料庫 ---
    def ai_and_db_task(app, user_id, user_text):
        print("ai_and_db_task: app id =", id(app))
        try:
            print("ai_and_db_task: current_app id =", id(current_app._get_current_object()))
        except Exception as e:
            print("ai_and_db_task: current_app not available:", e)
        with app.app_context():
            print("ai_and_db_task (in app_context): app id =", id(app))
            print("ai_and_db_task (in app_context): current_app id =", id(current_app._get_current_object()))
            reply_text = get_openai_response(user_text)
            new_input = UserInput(user_id=user_id, input_text=user_text, ai_response=reply_text)
            db.session.add(new_input)
            db.session.commit()
            send_line_push(user_id, reply_text)


    executor = getattr(current_app, "_linebot_executor", None)
    if executor is None:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        current_app._linebot_executor = executor

    # 只在背景執行緒用 app_context，主流程直接執行
    app = current_app._get_current_object()

    def ai_task(app, user_id, user_text):
        with app.app_context():
            reply_text = get_openai_response(user_text)
            new_input = UserInput(user_id=user_id, input_text=user_text, ai_response=reply_text)
            db.session.add(new_input)
            db.session.commit()
            return reply_text

    executor = getattr(current_app, "_linebot_executor", None)
    if executor is None:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        current_app._linebot_executor = executor

    future = executor.submit(ai_task, app, user_id, user_text)

    try:
        reply_text = future.result(timeout=2)
        # 2 秒內取得 AI 回覆，直接回覆並寫入資料庫
        send_line_reply(reply_token, reply_text)
    except concurrent.futures.TimeoutError:
        # 2 秒內沒回應，先回「AI 回覆中」
        send_line_reply(reply_token, "AI 回覆中")
        # 背景再執行 AI 回覆、資料庫與推播
        def push_task(fut):
            reply_text = fut.result()
            with app.app_context():
                send_line_push(user_id, reply_text)
        future.add_done_callback(push_task)

    return "OK", 200
