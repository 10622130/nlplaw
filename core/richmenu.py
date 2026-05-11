import requests
import json


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_menu(token: str, menu_object: dict) -> str:
    resp = requests.post(
        "https://api.line.me/v2/bot/richmenu",
        headers={**_headers(token), "Content-Type": "application/json"},
        json=menu_object,
    )
    resp.raise_for_status()
    return resp.json()["richMenuId"]


def _upload_image(token: str, menu_id: str, image_path: str) -> None:
    with open(image_path, "rb") as f:
        resp = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{menu_id}/content",
            headers={**_headers(token), "Content-Type": "image/jpeg"},
            data=f.read(),
        )
    resp.raise_for_status()


def _set_alias(token: str, menu_id: str, alias_id: str) -> None:
    resp = requests.post(
        "https://api.line.me/v2/bot/richmenu/alias",
        headers={**_headers(token), "Content-Type": "application/json"},
        data=json.dumps({"richMenuAliasId": alias_id, "richMenuId": menu_id}).encode(),
    )
    resp.raise_for_status()


def _set_default(token: str, menu_id: str) -> None:
    resp = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{menu_id}",
        headers=_headers(token),
    )
    resp.raise_for_status()


def setup_main_menu(token: str, image_path: str) -> str:
    menu_object = {
        "size": {"width": 2500, "height": 1686},
        "selected": True,
        "name": "main_menu",
        "chatBarText": "主選單",
        "areas": [
            {
                "bounds": {"x": 0, "y": 0, "width": 1250, "height": 843},
                "action": {"type": "richmenuswitch", "richMenuAliasId": "exam_menu", "data": "change-to-exammenu"},
            },
            {
                "bounds": {"x": 1250, "y": 0, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "問答須知"},
            },
            {
                "bounds": {"x": 0, "y": 843, "width": 1250, "height": 843},
                "action": {"type": "uri", "label": "關於我們", "uri": "https://liff.line.me/2002407298-NKqDGjqJ"},
            },
            {
                "bounds": {"x": 1250, "y": 843, "width": 1250, "height": 843},
                "action": {"type": "message", "text": "推薦親友"},
            },
        ],
    }
    menu_id = _create_menu(token, menu_object)
    _upload_image(token, menu_id, image_path)
    _set_alias(token, menu_id, "main_menu")
    _set_default(token, menu_id)
    return menu_id


def setup_exam_menu(token: str, image_path: str) -> str:
    menu_object = {
        "size": {"width": 2500, "height": 1686},
        "selected": True,
        "name": "exam_menu",
        "chatBarText": "考題練習",
        "areas": [
            {
                "bounds": {"x": 0, "y": 0, "width": 2500, "height": 337},
                "action": {"type": "richmenuswitch", "richMenuAliasId": "main_menu", "data": "change-to-mainmenu"},
            },
            {
                "bounds": {"x": 0, "y": 337, "width": 2500, "height": 337},
                "action": {"type": "message", "text": "民法、民事訴訟法"},
            },
            {
                "bounds": {"x": 0, "y": 674, "width": 2500, "height": 337},
                "action": {"type": "message", "text": "刑法、刑事訴訟法、法律倫理"},
            },
            {
                "bounds": {"x": 0, "y": 1011, "width": 2500, "height": 337},
                "action": {"type": "message", "text": "憲法、行政法、國際公法、國際私法"},
            },
            {
                "bounds": {"x": 0, "y": 1348, "width": 2500, "height": 337},
                "action": {"type": "message", "text": "公司法、保險法、票據法、證券交易法、強制執行法、法學英文"},
            },
        ],
    }
    menu_id = _create_menu(token, menu_object)
    _upload_image(token, menu_id, image_path)
    _set_alias(token, menu_id, "exam_menu")
    return menu_id
