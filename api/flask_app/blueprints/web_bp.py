from flask import Blueprint, request, jsonify, current_app
from core.ai import get_openai_response
from core.validation import validate_input_text

web_bp = Blueprint('web_bp', __name__)

@web_bp.route('/user_message', methods=['POST'])
def user_message():
    """Web API endpoint for user messages"""
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    
    if not user_input:
        return jsonify({'error': '請用中文輸入法律相關問題'}), 400
    
    # Validate and normalize input
    try:
        normalized_input = validate_input_text(user_input)
    except Exception as e:
        return jsonify({'response': str(e)}), 200
    
    # Get AI response
    try:
        ai_response = get_openai_response(
            normalized_input,
            openai_api_key=current_app.config['OPENAI_API_KEY'],
            logger=current_app.logger
        )
        return jsonify({'response': ai_response})
    except Exception as e:
        current_app.logger.error(f"AI service error: {str(e)}")
        return jsonify({'error': 'AI 發生錯誤，請稍後再試。'}), 500