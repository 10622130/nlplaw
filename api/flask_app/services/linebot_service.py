from flask import current_app
from api.flask_app.models import db, User, UserInput
from core.ai import get_openai_response
from core.line_api import send_line_reply
from core.spamfilter import validate_input_text


def handle_text_message(user_id: str, user_text: str, reply_token: str) -> None:
    """
    Full pipeline for an inbound LINE text message:
    ensure user exists → validate input → call AI → persist → reply.
    """
    _ensure_user(user_id)

    is_valid, result_text = validate_input_text(user_text)
    if not is_valid:
        respond_text = result_text
    else:
        respond_text = _get_ai_response(user_id, result_text)

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
