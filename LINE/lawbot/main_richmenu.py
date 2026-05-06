import requests
import json
from linebot import LineBotApi
from linebot.models import *

channel_access_token = ""

rich_menu_image_path = "main.jpg"

rich_menu_object = {
    "size": {"width": 2500,"height": 1686},
    "selected": True,
    "name": "main_menu",
    "chatBarText": "主選單",
    "areas":[
      {
        "bounds": {"x": 0, "y": 0, "width": 1250, "height": 843},
        "action": {"type": "richmenuswitch","richMenuAliasId": "exam_menu","data": "change-to-exammenu"}
      },
      {
        "bounds": {"x": 1250, "y": 0, "width": 1250, "height": 843},
        "action": {"type": "message", "text": "問答須知"}
      },
      {
        "bounds": {"x": 0, "y": 843, "width": 1250, "height": 843},
        "action": {"type": "uri","label": "關於我們","uri": "https://liff.line.me/2002407298-NKqDGjqJ"}
      },
      {
        "bounds": {"x": 1250, "y": 843, "width": 1250, "height": 843},
        "action": {"type": "message", "text": "推薦親友"}
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
    "richMenuAliasId":"main_menu",
    "richMenuId":rich_menu_id
}
req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu/alias',
                      headers=headers,data=json.dumps(body).encode('utf-8'))
print(req.text)

# Set the default rich menu
set_default_rich_menu_url = "https://api.line.me/v2/bot/user/all/richmenu/" + rich_menu_id
set_default_rich_menu_headers = {
    "Authorization": "Bearer " + channel_access_token
}
set_default_rich_menu_response = requests.post(set_default_rich_menu_url, headers=set_default_rich_menu_headers)
set_default_rich_menu_response.raise_for_status()

# Print the result
print("Rich menu created and uploaded successfully!")