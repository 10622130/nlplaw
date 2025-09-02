import requests

def send_line_reply(channel_access_token, reply_token, text):
    """
    發送 LINE 回應訊息
    :param channel_access_token: LINE channel access token
    :param reply_token: LINE reply token
    :param text: 回覆訊息文字
    :return: requests.Response
    """
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response

def send_line_push(channel_access_token, user_id, text):
    """
    用 LINE push API 主動推播訊息
    :param channel_access_token: LINE channel access token
    :param user_id: LINE user id
    :param text: 推播訊息文字
    :return: requests.Response
    """
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response