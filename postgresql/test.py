from flask import Flask, request, jsonify
import openai
from postgresql.Postgresql import *
import logging
import time  # 导入time模块

# 设置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def track_time(func):
    """装饰器用于追踪函数执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始执行的时间
        result = func(*args, **kwargs)  # 执行函数
        end_time = time.time()  # 记录函数结束执行的时间
        logging.debug(f"{func.__name__}: 执行时间 {(end_time - start_time) * 1000} 毫秒")  # 计算并记录函数执行时间
        return result
    return wrapper

@track_time
def OpenAI_process_data(user_input):
    logging.debug("OpenAI_process_data: 开始处理用户输入")
    try:
        organization_id = ''
        api_key = ''
        client = openai.Client(organization=organization_id, api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ]
        )
        logging.debug("OpenAI_process_data: 成功获取响应")
        return response.choices[0].message.content
    except Exception as e:
        logging.error("OpenAI_process_data: 处理过程中发生错误 - " + str(e))
        raise

app = Flask(__name__)

@app.route('/process_query', methods=['POST'])
@track_time
def process_query():
    logging.debug("process_query: 接收到POST请求")
    data = request.json
    user_input = data.get('query')

    if not user_input:
        logging.warning("process_query: 未提供查询内容")
        return jsonify({"error": "No query provided"}), 400

    user_id = data.get('user_id', 'default_user_id')
    user_name = data.get('user_name', 'Anonymous')

    insert_user(user_id, user_name)

    if user_input == "問答須知":
        response_text = "請用繁體中文明確敘述事件經過"
    elif user_input == "推薦親友":
        response_text = "加入法律智能小幫手連結: https://lin.ee/vNsToGI"
    else:
        try:
            with psycopg2.connect(connection_string) as conn:
                logging.debug("process_query: 成功连接数据库")
                response_text = process_input_with_retrieval(user_id, user_input, conn)
                insert_conversation(user_id, user_input, response_text)
        except Exception as e:
            logging.error("process_query: 处理请求时发生错误 - " + str(e))
            response_text = "處理您的请求时出错，请稍后再试。"

    response = jsonify({"response": response_text})
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

if __name__ == "__main__":
    app.run(debug=True)
