# ai_bp.py 
# web could call this api without login
from flask import Blueprint, jsonify, request, current_app
from openai import OpenAI
import time

from core.ai import get_openai_response

ai_bp = Blueprint('ai_bp', __name__)
    

@ai_bp.route("/ai", methods=['POST'])
def ai_endpoint():
    """提供 RESTful API，直接回傳使用者輸入的內容"""
    # API key 驗證
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    if api_key != current_app.config.get("API_KEY"):
        return jsonify({"error": "Unauthorized"}), 401

    start_time = time.perf_counter()  # 1. 記錄開始時間

    user_input = request.json.get("text", "")
    if not user_input:
        return jsonify({"error": "Missing text"}), 400

    response_text = get_openai_response(
        user_input,
        openai_api_key=current_app.config['OPENAI_API_KEY'],
        logger=current_app.logger
    )

    end_time = time.perf_counter()    # 2. record end time
    elapsed_time = end_time - start_time  # 3.  calculate elapsed time

    # 4.   log the elapsed time
    current_app.logger.info(f"Total processing time: {elapsed_time:.3f} seconds")

    return jsonify({"response": response_text})

#   For testing OpenAI API key validity
@ai_bp.route("/test_openai_key", methods=['GET'])
def test_openai_key():
    """測試 OpenAI API key 是否可用（用最簡單的 completion endpoint）"""
    from openai import OpenAI
    api_key = current_app.config['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)
    try:
        resp = client.completions.create(
            model="text-davinci-003",
            prompt="Say hello world",
            max_tokens=5
        )
        return jsonify({"success": True, "result": resp.choices[0].text.strip()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
