from flask import Blueprint, request, jsonify
from ai_bp import get_openai_response
import spamfilter 

web_bp = Blueprint('web_bp', __name__)

@web_bp.route('/user_message', methods=['POST'])
def user_message():
    data = request.get_json()
    user_input = data.get('user_input')
    if not user_input:
        return jsonify({'error': '請用中文輸入法律相關問題'}), 400

    # 訊息正規化
    normalized_input = spamfilter.normalize_punctuation(user_input)
    # 訊息過濾
    if not spamfilter.is_valid_text(normalized_input):
        # 直接用 bot response 格式回應錯誤訊息
        return jsonify({'response': '請輸入有效中文訊息'}), 200
    
    if len(normalized_input) > 200:
        return jsonify({'response': '請將問題縮短至200字以內'}), 400

    try:
        ai_response = get_openai_response(normalized_input)
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500