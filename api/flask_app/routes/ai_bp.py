from flask import Blueprint, jsonify, request, current_app
import time
from openai import OpenAI
from core.ai import get_openai_response
from core.spamfilter import validate_input_text

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route("/ai", methods=['POST'])
def ai_endpoint():
    start_time = time.perf_counter()

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "請傳入 JSON body"}), 400

    is_valid, result = validate_input_text(data.get("text", "").strip())
    if not is_valid:
        return jsonify({"error": result}), 400

    try:
        response_text = get_openai_response(result, current_app.config['OPENAI_API_KEY'])
    except Exception as e:
        current_app.logger.error(f"AI service error: {str(e)}")
        response_text = "AI 發生錯誤，請稍後再試。"

    current_app.logger.info(f"Processing time: {time.perf_counter() - start_time:.3f}s")
    return jsonify({"response": response_text})

@ai_bp.route("/test_openai_key", methods=['GET'])
def test_openai_key():
    """Test OpenAI API key validity"""
    api_key = current_app.config['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say hello world"}],
            max_tokens=5
        )
        return jsonify({"success": True, "result": resp.choices[0].message.content.strip()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})