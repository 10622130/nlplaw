from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import re
import requests


app = Flask(__name__)

line_bot_api = LineBotApi('')
handler = WebhookHandler('')

answers = []
options = ["A", "B", "C", "D"]
years = ["112", "111", "110", "109", "108", "107", "106", "105", "104", "103"]


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  global answers
  global options
  global years

  user_id = event.source.user_id
  user_profile = line_bot_api.get_profile(user_id)
  user_name = user_profile.display_name

  def set_quick_reply(user_input, years, event):
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label=year+"年", text=f"{year} {user_input}"))
        for year in years
    ]
    flex_message = TextSendMessage(
        text='請用下方快速回覆鍵選擇要練習的年份',
        quick_reply=QuickReply(items=quick_reply_items)
    )
    line_bot_api.reply_message(event.reply_token, flex_message)


  def send_template_message(user_input, years, event):
    templates = []
    for i in range(0, len(years), 4):
        actions = []
        for year in years[i:i+4]:
            actions.append(MessageAction(label=f"{year}年", text=f"{year} {user_input}"))
        template_message = TemplateSendMessage(
            alt_text='選擇年份',
            template=ButtonsTemplate(
                title='選擇年份',
                text='請上下滑動選擇要練習的年份',
                actions=actions
            )
        )
        templates.append(template_message)
    line_bot_api.reply_message(event.reply_token, templates)


  def get_exam(year_subject):
    url = "https://qaapi-npve5qpyma-uc.a.run.app/random-question"
    # 構建POST請求的JSON體
    payload = {'year_subject': year_subject}

    headers = {"Content-Type": "application/json"}

    # 發送POST請求到API
    response = requests.post(url, json=payload, headers=headers)

    return response.json()


  def get_response(user_input, user_id, user_name):
    url = "https://bornanswerv2-m5snoyxkaq-de.a.run.app/process_query"
    payload = {
          "query": user_input,
          "user_id": user_id,
          "user_name": user_name
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    return response.json().get("response")


  user_input = event.message.text
  quick_reply_pattern = r'^(民法、民事訴訟法|刑法、刑事訴訟法、法律倫理|憲法、行政法、國際公法、國際私法|公司法、保險法、票據法、證券交易法、強制執行法、法學英文)(?!考題)$'
  template_reply_pattern = r'^((民法、民事訴訟法|刑法、刑事訴訟法、法律倫理|憲法、行政法、國際公法、國際私法|公司法、保險法、票據法、證券交易法、強制執行法、法學英文)+考題)$'
  pattern = r'^(10[3-9]|11[0-2])\s+(民法、民事訴訟法|刑法、刑事訴訟法、法律倫理|憲法、行政法、國際公法、國際私法|公司法、保險法、票據法、證券交易法、強制執行法、法學英文)(?!考題)$'
  template_pattern = r'^(10[3-9]|11[0-2])\s+((民法、民事訴訟法|刑法、刑事訴訟法、法律倫理|憲法、行政法、國際公法、國際私法|公司法、保險法、票據法、證券交易法、強制執行法、法學英文)+考題)$'

  if user_input == "問答須知":
    line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text="如您要使用法律問答的功能，請切換到鍵盤，並用繁體中文輸入想要詢問的法律相關問題\n\n如您使用電腦版的LINE，也可直接輸入\"主選單\"以得到對應的資訊唷~"))


  elif user_input == "推薦親友":
    line_bot_api.reply_message(
      event.reply_token,
      TextSendMessage(text="請長按此訊息並選擇分享，將下方加入法律智能小幫手的連結分享給指定親友:\n https://lin.ee/vNsToGI"))


  elif user_input == "考題練習":
    buttons_template_message = TemplateSendMessage(
    alt_text='考題練習',
    template=ButtonsTemplate(
        thumbnail_image_url='https://img.freepik.com/free-vector/intellectual-property-concept-illustrated_52683-48609.jpg?w=900&t=st=1707242979~exp=1707243579~hmac=08b92486458adcb2489cc831cb8a63317c37a6edb0392fd655ee55fca340e3af',
        title='考題練習',
        text='請選擇要練習的考科',
        actions=[
            MessageAction(
                label='民法、民事訴訟法',
                text='民法、民事訴訟法考題'
            ),
            MessageAction(
                label='刑法、刑事訴訟法、法律倫理',
                text='刑法、刑事訴訟法、法律倫理考題'
            ),
            MessageAction(
                label='憲法、行政法、國際公法、國際私法',
                text='憲法、行政法、國際公法、國際私法考題'
            ),
            MessageAction(
                label='公司、保險、票據、證券交易、強制執行法',
                text='公司法、保險法、票據法、證券交易法、強制執行法、法學英文考題'
            )
        ]
      )
    )
    line_bot_api.reply_message(event.reply_token, buttons_template_message)


  elif user_input == "主選單":
    buttons_template_message = TemplateSendMessage(
    alt_text='主選單',
    template=ButtonsTemplate(
        thumbnail_image_url='https://img.freepik.com/free-vector/judge-concept-court-worker-stand-justice-law-judge-traditional-black-robe-hearing-case-sentencing-judgement-punishment-idea-isolated-flat-vector-illustration_613284-1877.jpg?t=st=1709177838~exp=1709181438~hmac=51327d54afbf13b42a57f91c9c213aee1b4633398bc20a172abec4c74bbe950d&w=900',

        title='主選單',
        text='選擇您想使用的功能',
        actions=[
            MessageAction(
                label='歷屆考題練習',
                text='考題練習'
            ),
            MessageAction(
                label='法律智能小幫手',
                text='問答須知'
            ),
            URIAction(
                label='官網',
                uri='https://imagexd-mtfui6kmqq-de.a.run.app'
            ),
            MessageAction(
                label='推薦親友',
                text='推薦親友'
            )
        ]
      )
    )
    line_bot_api.reply_message(event.reply_token, buttons_template_message)


  elif re.match(quick_reply_pattern, user_input):
    set_quick_reply(user_input, years, event)


  elif re.match(template_reply_pattern, user_input):
    send_template_message(user_input, years, event)


  elif re.match(pattern, user_input):
    exam = get_exam(user_input)
    question = exam.get('question')
    answer = exam.get('answer')
    answers.append(answer)

    flex_message = TextSendMessage(text=question, quick_reply=QuickReply(items=[
                                QuickReplyButton(action=MessageAction(label=option, text=option))
                                for option in options
                                ]))

    line_bot_api.reply_message(event.reply_token, flex_message)


  elif re.match(template_pattern, user_input):
    # 提取匹配的結果，去除结尾的 "考題" 兩個字
    user_input = user_input[:-2]

    # 使用處理後的 user_input 請求相關數據
    exam = get_exam(user_input)
    question = exam.get('question')
    answer = exam.get('answer')
    answers.append(answer)

    buttons_template_message = TemplateSendMessage(
    alt_text='選擇答案',
    template=ButtonsTemplate(
        title='選擇答案',
        text="請依上則訊息中的題目選取答案",

        actions=[
            MessageAction(label=option, text=option)
            for option in options
        ]))

    line_bot_api.reply_message(event.reply_token, [TextSendMessage(text=question), buttons_template_message])


  elif user_input in options and answers:
    if user_input == answers[-1]:
      line_bot_api.reply_message(event.reply_token,TextSendMessage(text="恭喜你答對了!"))


    if user_input in [option for option in options if option != answers[-1]]:
      line_bot_api.reply_message(event.reply_token,TextSendMessage(text=f"答錯了...答案是{answers[-1]}"))


  else:
    generated_text = get_response(user_input, user_id, user_name)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=generated_text)
    )

if __name__ == "__main__":
  app.run()