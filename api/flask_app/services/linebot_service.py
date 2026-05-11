from flask import current_app
from api.flask_app.models import db, User, UserInput, ExamSession
from api.flask_app.services.exam_service import (
    SUBJECT_RE, YEAR_SUBJECT_RE, OPTIONS,
    handle_subject_selection, handle_year_subject, handle_answer,
)
from core.ai import get_openai_response
from core.line_api import send_line_reply
from core.spamfilter import validate_input_text

WELCOME_MESSAGE = (
    "👋 歡迎使用法律智能小幫手！\n\n"
    "我提供兩項功能：\n"
    "⚖️ 法律問答 — 直接用中文輸入法律問題\n"
    "📝 考題練習 — 點選下方選單「考題練習」開始\n\n"
    "有任何法律疑問，隨時問我！"
)


def handle_follow_event(user_id: str, reply_token: str) -> None:
    """Triggered when a user adds or re-adds the bot."""
    _ensure_user(user_id)
    _send_reply(reply_token, WELCOME_MESSAGE)


def handle_text_message(user_id: str, user_text: str, reply_token: str) -> None:
    _ensure_user(user_id)

    if SUBJECT_RE.match(user_text):
        handle_subject_selection(user_text, reply_token)
    elif YEAR_SUBJECT_RE.match(user_text):
        handle_year_subject(user_id, user_text, reply_token)
    elif user_text in OPTIONS and ExamSession.get_answer(user_id) is not None:
        handle_answer(user_id, user_text, reply_token)
    else:
        is_valid, result_text = validate_input_text(user_text)
        respond_text = result_text if not is_valid else _get_ai_response(user_id, result_text)
        _send_reply(reply_token, respond_text)


def _ensure_user(user_id: str) -> None:
    if not User.exists(user_id):
        User.create(user_id)


def _get_ai_response(user_id: str, validated_text: str) -> str:
    try:
        response = get_openai_response(validated_text, current_app.config['OPENAI_API_KEY'])
        db.session.add(UserInput(
            user_id=user_id,
            input_text=validated_text,
            ai_response=response,
        ))
        db.session.commit()
        return response
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"AI pipeline failed: {e}")
        return "AI 發生錯誤，請稍後再試。"


def _send_reply(reply_token: str, text: str) -> None:
    response, status = send_line_reply(
        current_app.config['CHANNEL_ACCESS_TOKEN'], reply_token, text
    )
    if status != 200:
        current_app.logger.error(f"LINE reply failed: {status} {response.text}")
    else:
        current_app.logger.info("LINE reply success")
