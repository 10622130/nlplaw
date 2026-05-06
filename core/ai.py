from openai import OpenAI

# 系統提示詞
PROMPT_SYSTEM = (
    "你是一個專業的法律顧問，只能提供法律建議，且回答只能在200字內。"
    "若使用者輸入不屬於法律相關問題，就只回答『請輸入法律問題』。"
)

def get_openai_response(user_input, openai_api_key):

    client = OpenAI(api_key=openai_api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": PROMPT_SYSTEM},
                {"role": "user", "content": user_input}
            ],
        )
        msg = response.choices[0].message.content
        return msg
    except Exception as e:
        return "AI 發生錯誤，請稍後再試。"