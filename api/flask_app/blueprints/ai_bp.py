from flask import Blueprint, jsonify, request, current_app
import time
from openai import OpenAI
from core.ai import get_openai_response
from core.validation import validate_input_text

ai_bp = Blueprint('ai_bp', __name__)

@ai_bp.route("/ai", methods=['POST'])
def ai_endpoint():
    """AI API endpoint with API key authentication"""
    # No authentication - public API
    
    start_time = time.perf_counter()
    
    # Get and validate user input
    user_input = request.json.get("text", "").strip()
    user_input = validate_input_text(user_input)
    
    # Get AI response
    try:
        response_text = get_openai_response(
            user_input,
            openai_api_key=current_app.config['OPENAI_API_KEY'],
            logger=current_app.logger
        )
    except Exception as e:
        current_app.logger.error(f"AI service error: {str(e)}")
        response_text = "AI 發生錯誤，請稍後再試。"
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    # Log processing time
    current_app.logger.info(f"Total processing time: {elapsed_time:.3f} seconds")
    
    return jsonify({"response": response_text})

@ai_bp.route("/test_openai_key", methods=['GET'])
def test_openai_key():
    """Test OpenAI API key validity"""
    api_key = current_app.config['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)
    
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello world"}],
            max_tokens=5
        )
        return jsonify({"success": True, "result": resp.choices[0].message.content.strip()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})