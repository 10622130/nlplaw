import requests
import json
from flask import Flask, request, abort,render_template, jsonify, redirect, url_for,session
from urllib import parse
from linebot import LineBotApi
from linebot.models import *
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
from openai import OpenAI
from pprint import pprint
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart




app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 應該使用安全的隨機字符串


#
@app.route('/',  methods=['GET','POST'])
def index():

    userId = session.get('userId')
    name = session.get('name')
    dialogList = session.get('dialogList')

    if userId == None:
        print('not in session')
        dialogList = []
        session['dialogList'] = dialogList
        print(f"對話內容:{session['dialogList']}")
    if userId :
        print(name,userId)
        return render_template('index.html',dialogList=dialogList, name=name,userId=userId)
    else:
        print(userId)
        return render_template('index.html',dialogList=dialogList, client_id=line_login_id, end_point=end_point, userId=userId)
    

@app.route('/process_data' , methods=["POST"])
def process_data():
    dialogList = session.get('dialogList')
    userId = session.get('userId')
    Udata = request.form.get("Udata")
    print(Udata)

    # DB
    response = requests.post(f'{DB_end_point}/question_answer', 
                        json={"userId":userId, "question": Udata})
    Rdata = response.text
    

    dialog = { "You" : Udata, "LawBot" : Rdata }
    dialogList.append(dialog)
    session['dialogList'] = dialogList
    print(dialogList)
    identity = {"userId":userId ,"dialogList":dialogList}
    return identity


@app.route('/line_login', methods=['GET'])
def login():
    code = request.args.get("code", None)
    state = request.args.get("state", None)
    if code and state:
        HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
        url = "https://api.line.me/oauth2/v2.1/token"
        FormData = {"grant_type": 'authorization_code', "code": code, "redirect_uri": F"{end_point}/line_login", "client_id": line_login_id, "client_secret":line_login_secret}
        data = parse.urlencode(FormData)
        content = requests.post(url=url, headers=HEADERS, data=data).text
        content = json.loads(content)
        
        url = "https://api.line.me/v2/profile"
        HEADERS = {'Authorization': content["token_type"]+" "+content["access_token"]}
        content = requests.get(url=url, headers=HEADERS).text
        content = json.loads(content)
        session['userId'] = content["userId"]
        session['name'] = content["displayName"]
        
        response = requests.get(f'{DB_end_point}/history', params={"userId":session['userId'] })
        pprint(response.text)


        session['dialogList'] = response.text

        cont = session['dialogList'][0]["LawBot"]
        if cont == "" : session['dialogList'] = []

        print(f"對話內容:{session['dialogList']}")

        return redirect(url_for('index'))


@app.route('/logout')
def logout():

    # 從 session 中移除用戶信息
    session.pop('userId', None)
    session.pop('name', None)
    session.pop('dialogList',[])
    return redirect(url_for('index'))


def send_email(sender_email, receiver_email, subject, message_body):
    
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject
    message.attach(MIMEText(message_body, 'plain'))
    smtp_server = 'smtp.gmail.com'
    port = 587  
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()  
    server.login(username, password)
    text = message.as_string()
    server.sendmail(sender_email, receiver_email, text)

    server.quit()

@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        subject = 'New message from your website 法律問答'
        message_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        send_email(sender_email, receiver_email, subject, message_body)
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)


