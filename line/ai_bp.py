# ai_bp.py 
# web could call this api without login
from flask import Blueprint, jsonify, request, current_app
from openai import OpenAI
import time

prompt_system = (
        "你是一個專業的法律顧問，只能提供法律建議，且回答只能在200字內。若使用者輸入不屬於法律相關問題，就只回答『請輸入法律問題』。"
        )

ai_bp = Blueprint('ai_bp', __name__)


def get_openai_response(user_input):
    """呼叫 OpenAI API 取得回應""" 
    
    api_key = current_app.config['OPENAI_API_KEY']
    client = OpenAI(api_key=api_key)  # 設定 API 金鑰
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
             {"role": "system", "content": prompt_system},
             {"role": "user", "content": user_input}
            ],
            # temperature=0.7  # 調整回答的隨機性
        )
        current_app.logger.info(f"OpenAI response: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"OpenAI API error: {str(e)}")
        return "AI 發生錯誤，請稍後再試。"
    

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

    response_text = get_openai_response(user_input)

    end_time = time.perf_counter()    # 2. 記錄結束時間
    elapsed_time = end_time - start_time  # 3. 計算花費時間(秒)

    # 4. 將花費時間記錄到日誌，或回傳給用戶
    current_app.logger.info(f"Total processing time: {elapsed_time:.3f} seconds")

    return jsonify({"response": response_text})

# 新增簡單的 OpenAI createCompletion 測試端點
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
