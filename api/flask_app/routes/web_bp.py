from flask import Blueprint, request, jsonify, current_app, session
from core.ai import get_openai_response
from core.spamfilter import validate_input_text

web_bp = Blueprint('web_bp', __name__)


@web_bp.route('/user_message', methods=['POST'])
def user_message():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': '請傳入 JSON body'}), 400

    is_valid, result = validate_input_text(data.get('user_input', '').strip())
    if not is_valid:
        return jsonify({'error': result}), 400

    try:
        ai_response = get_openai_response(result, current_app.config['OPENAI_API_KEY'])
    except Exception as e:
        current_app.logger.error(f"AI service error: {str(e)}")
        return jsonify({'error': 'AI 發生錯誤，請稍後再試。'}), 500

    user_id = session.get('user_id')
    if user_id:
        from api.flask_app.models import db, UserInput
        try:
            db.session.add(UserInput(user_id=user_id, input_text=result, ai_response=ai_response))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"DB write failed: {e}")

    return jsonify({'response': ai_response})