# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from linebot import LineBotApi, WebhookHandler
import json, requests
import configparser

config = configparser.ConfigParser()
config.read('files/config.ini')
line_bot_api = LineBotApi(config.get('line-bot', 'channel-access-token'))
handler = WebhookHandler(config.get('line-bot', 'channel-secret'))

name_file = json.load(open('../../../Downloads/CTPS final/files/names.json', 'r', encoding='utf-8'))


def richmenu(channel_access_token, line_bot_api, richmenu_num):
    with open("../../../Downloads/CTPS final/files/names.json", "r") as j:
        content = json.load(j)

    headers = {"Authorization": "Bearer " + channel_access_token, "Content-Type": "application/json"}
    body = json.load(open(content[richmenu_num]["json_file_name"], 'r', encoding='utf-8'))

    req = requests.request('POST', "https://api.line.me/v2/bot/richmenu", headers=headers,
                           data=json.dumps(body).encode('utf-8'))

    id = req.text[15:56]
    print(id)

    with open(content[richmenu_num]["pic_name"], 'rb') as f:
        line_bot_api.set_rich_menu_image(id, "image/jpeg", f)

    content[richmenu_num]["id"] = id

    with open("../../../Downloads/CTPS final/files/names.json", "w", encoding='utf-8') as file:
        json.dump(content, file, ensure_ascii=False, indent=4)

    # 啟用 Rich menu
    # req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/' + id, headers=headers)


richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_0")  # 註冊 richmenu
richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_2")  # 註冊 richmenu
richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_2_1")  # 註冊 richmenu
richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_3")  # 註冊 richmenu
richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_3_1")  # 註冊 richmenu
richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_3_1_1")  # 註冊 richmenu
richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_3_2")  # 註冊 richmenu
richmenu(config.get('line-bot', 'channel-access-token'), line_bot_api, "richmenu_3_2_1")  # 註冊 richmenu
