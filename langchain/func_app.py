from flask import Flask, request
from func_langchain import Rachel_langchain
import json
app = Flask(__name__)
def get_history_data(userId):
    try:
        with open('./chat_history.json', 'r') as f:
            db = json.load(f.readline())
            if userId == 'ALL':
                chat_history = db
            else:
                chat_history = db[userId]
    except:
        chat_history = ''
    return chat_history

def get_detailed_history_data():
    try:
        with open('./chat_detailed_history.json', 'r') as f:
            db = json.load(f.readine())
    except:
        db = ''
    return db

def store_history_data(userId, history):
    try:
        with open('./chat_history.json', 'r') as f:
            db = json.load(f.readline())
        print(f'read_history: {db}')
    except:
        db = {}
        db[userId] = history

    print(f'store_history: {history}')
    db[userId] = history
    with open('./chat_history.json', 'w') as f:
        json.dump(db, f)

def store_detailed_history_data(userId, history):
    try:
        with open('./chat_detailed_history.json', 'r') as f:
            db = json.load(f.readline())
    except:
        db = {}
    if userId in db:
        db[userId].append(history)
    else:
        db[userId] = []
        db[userId].append(history)

    with open('./chat_detailed_history.json', 'w') as f:
        json.dump(db, f)
        
@app.route("/history", methods=['GET'])
def history():
    userId = request.args['userId']
    return get_history_data(userId)

@app.route("/detailed_history", methods=['GET'])
def detailed_history():
    return get_detailed_history_data()

@app.route("/question_answer", methods=['POST'])
def question_answer():
    body = request.get_json()
    userId = body['userId']
    question = body['question']

    index_name = 'tt01'
    namespace_name = 'test1'

    qa_object = Rachel_langchain(index_name, namespace_name, get_history_data(userId))
    answer, detailed_history = qa_object.answer_question(question)

    store_history_data(userId, qa_object.get_history())
    store_detailed_history_data(userId, detailed_history)

    return answer

if __name__ == '__main__':
    app.run(port=9876,debug=True)