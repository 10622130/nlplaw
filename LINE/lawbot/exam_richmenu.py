import requests
import json
from linebot import LineBotApi
from linebot.models import *

channel_access_token = ""

rich_menu_image_path = "exam.jpg"

rich_menu_object = {
    "size": {"width": 2500,"height": 1686},
    "selected": True,
    "name": "exam_menu",
    "chatBarText": "考題練習",
    "areas":[
      {
        "bounds": {"x": 0, "y": 0, "width": 2500, "height": 337.2},
        "action": {"type": "richmenuswitch","richMenuAliasId": "main_menu","data": "change-to-mainmenu"}
      },
      {
        "bounds": {"x": 0, "y": 337.2, "width": 2500, "height": 337.2},
        "action": {"type": "message", "text": "民法、民事訴訟法"}
      },
      {
        "bounds": {"x": 0, "y": 674.4, "width": 2500, "height": 337.2},
        "action": {"type": "message", "text": "刑法、刑事訴訟法、法律倫理"}
      },
      {
        "bounds": {"x": 0, "y": 1011.6, "width": 2500, "height": 337.2},
        "action": {"type": "message", "text": "憲法、行政法、國際公法、國際私法"}
      },
      {
        "bounds": {"x": 0, "y": 1348.8, "width": 2500, "height": 337.2},
        "action": {"type": "message", "text": "公司法、保險法、票據法、證券交易法、強制執行法、法學英文"}
      }
  ]
}

# Create a rich menu
create_rich_menu_url = "https://api.line.me/v2/bot/richmenu"
create_rich_menu_headers = {
    "Authorization": "Bearer " + channel_access_token,
    "Content-Type": "application/json"
}
create_rich_menu_response = requests.post(create_rich_menu_url, headers=create_rich_menu_headers, json=rich_menu_object)
create_rich_menu_response.raise_for_status()

# Get the rich menu ID
rich_menu_id = create_rich_menu_response.json()["richMenuId"]

# Upload the rich menu image
upload_rich_menu_image_url = "https://api-data.line.me/v2/bot/richmenu/" + rich_menu_id + "/content"
upload_rich_menu_image_headers = {
    "Authorization": "Bearer " + channel_access_token,
    "Content-Type": "image/jpeg"
}
upload_rich_menu_image_data = open(rich_menu_image_path, "rb").read()
upload_rich_menu_image_response = requests.post(upload_rich_menu_image_url, headers=upload_rich_menu_image_headers, data=upload_rich_menu_image_data)
upload_rich_menu_image_response.raise_for_status()

# 將圖文選單 id 和別名 Alias id 綁定
headers = {"Authorization":"Bearer " + channel_access_token,"Content-Type":"application/json"}
body = {
    "richMenuAliasId":"exam_menu",
    "richMenuId":rich_menu_id
}
req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu/alias',
                      headers=headers,data=json.dumps(body).encode('utf-8'))
print(req.text)
