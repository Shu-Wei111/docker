import json
import Remind
import time
from linebot.models import CarouselTemplate, CarouselColumn, PostbackTemplateAction, MessageTemplateAction, \
    URITemplateAction, TemplateSendMessage, MessageAction, ButtonsTemplate, ConfirmTemplate, PostbackAction


def refresh_data():
    with open('registered_data.json', 'r', encoding="utf-8") as f:
        registered_data = json.load(f)
    with open("order.json", "r", encoding='utf-8-sig') as f:
        buyer_data = json.load(f)
    with open("user_dict.json", "r", encoding='utf-8') as f:
        seller_data = json.load(f)
    return registered_data, buyer_data, seller_data


def back(user_id):
    registered_data = refresh_data()[0]
    if registered_data[user_id]["Step"] >= 3:
        registered_data[user_id]["Step"] = 3
    else:
        del registered_data[user_id]
    with open('registered_data.json', 'w', encoding='utf-8') as f:
        json.dump(registered_data, f, ensure_ascii=False, indent=4)
    return "已回首頁!"


def Register(text, user_id):
    registered_data, buyer_data, seller_data = refresh_data()
    if registered_data.get(user_id) is None:
        registered_data[user_id] = {'Step': 0}
        registered_data[user_id]["Buyer_step"] = [0, 0, 0]
        registered_data[user_id]["Page"] = 1
        reply = "請輸入姓名"
    elif registered_data[user_id]['Step'] == 0:  # Name
        registered_data[user_id]['Step'] += 1
        registered_data[user_id]['Name'] = text
        reply = '請輸入手機'
    elif registered_data[user_id]['Step'] == 1:  # Phone
        registered_data[user_id]['Step'] += 1
        registered_data[user_id]['Phone'] = text
        reply = "請輸入學號"
    elif registered_data[user_id]['Step'] == 2:  # Student_id
        registered_data[user_id]['Step'] += 1
        registered_data[user_id]['Student_id'] = text
        if user_id not in buyer_data:  # 以user_id在訂單系統建立個人資料
            buyer_data[user_id] = {
                "favorites": [],
                "current_order": {},
                "history_order": {},
            }
        with open('order.json', 'w', encoding='utf-8-sig') as f:
            json.dump(buyer_data, f, ensure_ascii=False, indent=4)
        reply = "註冊完成，點開選單開始團購吧(⁎⁍̴̛ᴗ⁍̴̛⁎)!"
    with open('registered_data.json', 'w', encoding='utf-8') as f:
        json.dump(registered_data, f, ensure_ascii=False, indent=4)
    return reply


def Basic_Information(text, userid):
    registered_data = {}
    reply = ''
    with open('registered_data.json', 'r', encoding="utf-8") as f:
        registered_data = json.load(f)
        if registered_data.get(userid) == None:
            return '尚未註冊，查無資料'

    name = registered_data[userid]['Name']
    phone = registered_data[userid]['Phone']
    studentID = registered_data[userid]['Student_id']

    reply += '姓名：{}\n'.format(name)
    reply += '手機：{}\n'.format(phone)
    reply += '學號：{}'.format(studentID)

    return reply


def Modify_Information(text, userid):
    registered_data = {}
    with open('registered_data.json', 'r', encoding="utf-8") as f:
        registered_data = json.load(f)
        if registered_data.get(userid) == None:
            return '尚未註冊'

    if text[2:4] == '姓名':
        if text.find(':') != -1:
            modify = text.split(':')[1]
        elif text.find('：') != -1:
            modify = text.split('：')[1]
        registered_data[userid]['Name'] = modify
        with open('registered_data.json', 'w', encoding='utf-8') as f:
            json.dump(registered_data, f, ensure_ascii=False, indent=4)
        return '姓名更改完畢'

    elif text[2:4] == '手機':
        if text.find(':') != -1:
            modify = text.split(':')[1]
        elif text.find('：') != -1:
            modify = text.split('：')[1]
        registered_data[userid]['Phone'] = modify
        with open('registered_data.json', 'w', encoding='utf-8') as f:
            json.dump(registered_data, f, ensure_ascii=False, indent=4)
        return '手機更改完畢'

    elif text[2:4] == '學號':
        if text.find(':') != -1:
            modify = text.split(':')[1]
        elif text.find('：') != -1:
            modify = text.split('：')[1]
        registered_data[userid]['Student_ID'] = modify
        with open('registered_data.json', 'w', encoding='utf-8') as f:
            json.dump(registered_data, f, ensure_ascii=False, indent=4)
        return '學號更改完畢'

    else:
        return '輸入格式錯誤'


def print_1(text, user_id):
    registered_data, buyer_data, seller_data = refresh_data()
    order_list = []
    for i in seller_data:
        if seller_data[i]["seller_user_id"] == user_id and seller_data[i]["status"] == 1:
            order_list.append(i)
    if len(order_list) == 0:
        reply = "沒有待成團的訂單!"
    elif registered_data[user_id]["Step"] == 4:
        if text not in order_list:
            reply = "訂單編號錯誤!"
        else:
            reply = "以下是" + text + "號訂單目前的情況:\n"
            reply += '%-10s' % "姓名　" + '%-9s' % "|數量" + '%-10s' % "|金額" + "\n"
            customer_list = seller_data[text]["customer_id"]
            customer_list = [i[0] for i in customer_list]  # 紀錄所有訂單的顧客user_id
            lower_bound = seller_data[text]['group_condition_product_number'][0]
            current_total = 0  # 計算目前訂單總數量
            for i in customer_list:
                name = registered_data[i]["Name"]  # 名字
                number = buyer_data[i]["current_order"][text]["number"]  # 數量
                sum = buyer_data[i]["current_order"][text]["sum"]  # 金額
                current_total += number
                reply += '{:10}'.format(name) + '{:10}'.format("|" + str(number)) + '{:10}'.format(
                    "　|" + str(sum)) + "\n"
            if current_total >= lower_bound:
                reply += "\n恭喜已達成開團條件，隨時可以提前出發(˶‾᷄ ⁻̫ ‾᷅˵)!\n"
            else:
                diff = lower_bound - current_total
                reply += "\n再湊" + str(diff) + "個就可以出團啦，再等等吧!ಥ_ಥ"
            reply += "若想提前開團，請再次輸入開團編號確認!"
            registered_data[user_id]["Step"] = 5
    elif registered_data[user_id]["Step"] == 5:
        if text in seller_data.keys() and seller_data[text]["seller_user_id"] == user_id and seller_data[text][
            "status"] == 1:
            seller_data[text]["status"] = 2
            reply = text + "號商品已出團!\n請去已成團查詢訂單!"
            with open('user_dict.json', 'w', encoding='utf-8') as f:
                json.dump(seller_data, f, ensure_ascii=False, indent=4)
        else:
            reply = "輸入錯誤，已回首頁!"
        registered_data[user_id]["Step"] = 3  # 不管有沒有提前出團，step都回到3(初始化)
    elif len(order_list) == 1:
        reply = "以下是" + order_list[0] + "號訂單目前的情況:\n"
        reply += '%-10s' % "姓名　" + '%-9s' % "|數量" + '%-10s' % "|金額" + "\n"
        customer_list = seller_data[order_list[0]]["customer_id"]
        customer_list = [i[0] for i in customer_list]  # 紀錄所有訂單的顧客user_id
        lower_bound = seller_data[order_list[0]]['group_condition_product_number'][0]
        current_total = 0  # 計算目前訂單總數量
        for i in customer_list:
            name = registered_data[i]["Name"]  # 名字
            number = buyer_data[i]["current_order"][order_list[0]]["number"]  # 數量
            sum = buyer_data[i]["current_order"][order_list[0]]["sum"]  # 金額
            current_total += number
            reply += '{:10}'.format(name) + '{:10}'.format("|" + str(number)) + '{:10}'.format(
                "　|" + str(sum)) + "\n"
        if current_total >= lower_bound:
            reply += "\n恭喜已達成開團條件，隨時可以提前出發(˶‾᷄ ⁻̫ ‾᷅˵)!\n"
        else:
            diff = lower_bound - current_total
            reply += "\n再湊" + str(diff) + "個就可以出團啦，再等等吧!ಥ_ಥ"
        reply += "若想提前開團，請再次輸入開團編號確認!"
        registered_data[user_id]["Step"] = 5

    else:
        reply = "您目前的訂單有: \n訂單編號 : 商品名稱\n"
        for j in order_list:
            reply += j + " : " + seller_data[j]["product_name"] + "\n"
        reply += "請輸入想查詢的訂單編號(*¯︶¯*)"
        registered_data[user_id]["Step"] = 4
    with open('registered_data.json', 'w', encoding='utf-8') as f:
        json.dump(registered_data, f, ensure_ascii=False, indent=4)

    return reply


def print_2(text, user_id):
    registered_data, buyer_data, seller_data = refresh_data()
    order_list = []
    for i in seller_data:
        if seller_data[i]["seller_user_id"] == user_id and seller_data[i]["status"] == 2:
            order_list.append(i)
    if len(order_list) == 0:
        reply = "沒有已成團的訂單!"
    elif registered_data[user_id]["Step"] == 6:
        if text not in order_list:
            reply = "訂單編號錯誤!"
        else:
            reply = "以下是" + text + "號訂單目前的情況:\n\n"
            reply += '%-3s' % "姓名　" + '%-4s' % "|數量" + '%-5s' % "|金額" + '%-10s' % "|電話" + "\n"
            customer_list = seller_data[text]["customer_id"]
            customer_list = [i[0] for i in customer_list]  # 紀錄所有訂單的顧客user_id
            for i in customer_list:
                name = registered_data[i]["Name"]  # 名字
                number = buyer_data[i]["current_order"][text]["number"]  # 數量
                sum = buyer_data[i]["current_order"][text]["sum"]  # 金額
                phone = buyer_data[i]["current_order"][text]["phone_num"]  # 電話
                reply += '{:3}'.format(name) + '{:5}'.format("|" + str(number)) + '{:8}'.format(
                    "　|" + str(sum)) + '{:10}'.format("|" + phone) + "\n"
            registered_data[user_id]["Step"] = 3
    else:
        reply = "您目前的訂單有: \n訂單編號 : 商品名稱\n\n"
        for j in order_list:
            reply += j + " : " + seller_data[j]["product_name"] + "\n"
        reply += "\n請輸入想查詢的訂單編號(*¯︶¯*)"
        registered_data[user_id]["Step"] = 6
    with open('registered_data.json', 'w', encoding='utf-8') as f:
        json.dump(registered_data, f, ensure_ascii=False, indent=4)
    return reply


def print_3(text, user_id):
    registered_data, buyer_data, seller_data = refresh_data()
    order_list = []
    for i in seller_data:
        if seller_data[i]["seller_user_id"] == user_id and seller_data[i]["status"] == 3:
            order_list.append(i)
    if len(order_list) == 0:
        reply = "沒有歷史訂單!"
    elif registered_data[user_id]["Step"] == 7:
        if text not in order_list:
            reply = "訂單編號錯誤!"
        else:
            reply = "以下是" + text + "號訂單的歷史紀錄:\n"
            reply += '{:3}'.format("姓名　") + '%-4s' % "|取貨" + '%-4s' % "|付款" + '%-5s' % "|給買家的評分" + "\n"
            customer_list = seller_data[text]["customer_id"]
            customer_list = [i[0] for i in customer_list]  # 紀錄所有訂單的顧客user_id
            for i in customer_list:
                name = registered_data[i]["Name"]  # 名字
                if buyer_data[i]["history_order"][text]["pay_If"]:  # 付款與否
                    pay = "v"
                else:
                    pay = "x"
                if buyer_data[i]["history_order"][text]["get_If"]:  # 取貨與否
                    get = "v"
                else:
                    get = "x"
                rate = buyer_data[i]["history_order"][text]["buyer_getRate"]  # 賣家給買家的評價
                reply += '{:3}'.format(name) + "|" + '{:^8}'.format(pay) + "|" + '{:^8}'.format(get) + "|" + '{:^16}'.format(str(rate)) + "\n"
            registered_data[user_id]["Step"] = 3
    else:
        reply = "歷史訂單有: \n訂單編號 : 商品名稱\n"
        for j in order_list:
            reply += j + " : " + seller_data[j]["product_name"] + "\n"
        reply += "請輸入想查詢的訂單編號(*¯︶¯*)"
        registered_data[user_id]["Step"] = 7
    with open('registered_data.json', 'w', encoding='utf-8') as f:
        json.dump(registered_data, f, ensure_ascii=False, indent=4)
    return reply


def seller_broadcast(text, user_id):
    registered_data, buyer_data, seller_data = refresh_data()
    if registered_data[user_id]["Step"] != 8:
        reply = "請按照以下格式推播訊息:\n\n" + "開團編號:要推播的訊息\n\n(舉例)3:大家明天記得領貨!"
        registered_data[user_id]["Step"] = 8
        with open('registered_data.json', 'w', encoding='utf-8') as f:
            json.dump(registered_data, f, ensure_ascii=False, indent=4)
        return reply
    else:
        registered_data[user_id]["Step"] = 3
        with open('registered_data.json', 'w', encoding='utf-8') as f:
            json.dump(registered_data, f, ensure_ascii=False, indent=4)
        item_id = text.split(":")[0]
        item_name = seller_data[item_id]["product_name"]
        message = "以下是來自'" + item_name + "'賣家的推播 :\n\n"
        message += text.split(":")[1]
        f4 = Remind.f4(user_id, item_id, message, seller_data)
        if f4:
            customer_list = f4
            return customer_list, message
        else:
            return False


### ---------------------------------------------------------------HW---------------------------------------------------------
'''
with open('./registered_data.json', 'r', encoding='utf-8-sig') as f_reg:
    registered_data = json.load(f_reg)

with open('./order.json', 'r', encoding='utf-8-sig') as f_ord:
    buyer_data = json.load(f_ord)

with open('./user_dict.json', 'r', encoding='utf-8-sig') as f_sell:
    seller_data = json.load(f_sell)
'''

# ----威澄----

# V新增收藏
def favoriteAdd(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()

    if user_id not in buyer_data:  # 以user_id在訂單系統建立個人資料
        buyer_data[user_id] = {
            "favorites": [],
            "current_order": {},
            "history_order": {},
        }

    text = text.split(":")[1]
    item_id = text

    # 檢查商品是否存在
    if str(item_id) not in seller_data.keys():
        return '此商品不存在'

    # 新增收藏
    if item_id not in buyer_data[user_id]['favorites']:
        buyer_data[user_id]['favorites'].append(item_id)

        with open('order.json', 'w', encoding='utf-8-sig') as f2:
            json.dump(buyer_data, f2, ensure_ascii=False, indent=4)

        return '收藏成功'
    else:
        return "已收藏過囉!"


# step == 9 : 未進入購買程序、初始化、return輸入數量  => step = 10
# step == 10 : 檢查數量、return輸入時段             => step = 11
# step == 11 : 檢查時段、建立訂單、完成訂單           => step = 9


# Vif step == 9, 未進入購買程序、初始化、return輸入數量
def order_step_9(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()

    item_id = text.split(':')[1]

    # 檢查團購是否還存在
    if item_id not in seller_data.keys():
        return '此團不存在'

    # 紀錄item_id
    registered_data[user_id]['Buyer_step'][0] = int(item_id)

    # 檢查是否還有團購空間
    current_num = int(seller_data[item_id]['current_number'])
    max_num = int(seller_data[item_id]['group_condition_product_number'][1])
    if current_num < max_num:
        registered_data[user_id]['Step'] = 10  # 前進下一步
        reply = '請輸入購買數量：' + \
                '\n\n* 請用數字表示' + \
                '\n* 購買數量不可超過' + str(max_num - current_num)

        with open('registered_data.json', 'w', encoding='utf-8') as f1:
            json.dump(registered_data, f1, ensure_ascii=False, indent=4)

        return reply
    else:
        return '此團購已額滿'


# Vif step == 10, 檢查數量、return輸入時段
def order_step_10(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()

    try:
        # 檢查是否回傳數字
        num = int(text)
        item_id = str(registered_data[user_id]['Buyer_step'][0])

        # 檢查購買數量是否超過上限
        current_num = int(seller_data[item_id]['current_number'])
        max_num = int(seller_data[item_id]['group_condition_product_number'][1])
        if (current_num + num) > max_num:
            return '購買數量已經超過上限囉！請再輸入一次購買數量！'
        else:
            registered_data[user_id]['Buyer_step'][1] = num  # 暫存number
            registered_data[user_id]['Step'] = 11  # 進入step2

            with open('registered_data.json', 'w', encoding='utf-8') as f1:
                json.dump(registered_data, f1, ensure_ascii=False, indent=4)

            trading_time = tradingtime(item_id)  # 取貨時段
            reply = '請輸入取貨時段選項：\n\n*' + trading_time
            return reply
    except ValueError:
        return '您的輸入非數字，請再輸入一次購買數量！'


# Vif step == 11, 檢查時段、建立訂單、完成訂單
def order_step_11(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()

    try:
        # 檢查是否回傳數字
        pickup_time = int(text)
        item_id = registered_data[user_id]['Buyer_step'][0]

        # 檢查時段是否存在
        if pickup_time <= len(seller_data[str(item_id)]['trading_time']):  # 存在
            registered_data[user_id]['Buyer_step'][2] = pickup_time  # 暫存pickUp_time

            order_decide(user_id, registered_data)  # 建立訂單

            registered_data[user_id]['Step'] = 9  # Step歸位

            with open('registered_data.json', 'w', encoding='utf-8') as f2:
                json.dump(registered_data, f2, ensure_ascii=False, indent=4)  # 更新registered

            return '完成訂單'
        else:
            return '該時段不存在，請再輸入一次時段！'
    except ValueError:
        return '您的輸入非數字，請再輸入一次時段！'


# V判斷user
def order_decide(user_id, registered_data):
    registered_data, buyer_data, seller_data = refresh_data()

    if user_id not in buyer_data:  # 以user_id在訂單系統建立個人資料
        buyer_data[user_id] = {
            "favorites": [],
            "current_order": {},
            "history_order": {},
        }
        with open('order.json', 'w', encoding='utf-8-sig') as f2:  # json.dump()將資料寫成json檔案
            json.dump(buyer_data, f2, ensure_ascii=False, indent=4)

    orderAdd(user_id, registered_data)


# V建立訂單
def orderAdd(user_id, registered_data):
    registered_data, buyer_data, seller_data = refresh_data()

    item_id = str(registered_data[user_id]['Buyer_step'][0])

    # 建立新訂單
    buyer_data[user_id]['current_order'][item_id] = {
        "number": registered_data[user_id]['Buyer_step'][1],
        "sum": registered_data[user_id]['Buyer_step'][1] * int(seller_data[item_id]['price']),
        "order_time": time.localtime(),  # 下訂時間（訂單建立時間）
        "pickUp_time": registered_data[user_id]['Buyer_step'][2],  # 取貨時間(第幾個時段)
        "phone_num": registered_data[user_id]['Phone'],  # 手機號碼（string）
        "pay_If": False,  # 建立訂單之初，未付款
        "get_If": False,  # 建立訂單之初，未取貨
        "cancel_If": False,  # 建立訂單之初，未取消
        "buyer_getRate": 0,  # 建立訂單之初，評價0
        "seller_getRate": 0,  # 建立訂單之初，評價0
    }

    # 在開團資訊紀錄更新資料
    seller_data[item_id]['current_number'] = seller_data[item_id]['current_number'] + registered_data[user_id]['Buyer_step'][1]  # 新增訂單數量
    seller_data[item_id]['customer_id'].append([user_id, registered_data[user_id]['Buyer_step'][2]])  # 儲存訂單客戶的user_id對應下單數量

    with open('order.json', 'w', encoding='utf-8-sig') as f1:  # json.dump()將資料寫成json檔案
        json.dump(buyer_data, f1, ensure_ascii=False, indent=4)

    with open('user_dict.json', 'w', encoding='utf-8') as f2:  # json.dump()將資料寫成json檔案
        json.dump(seller_data, f2, ensure_ascii=False, indent=4)


# V查看商品詳細資料
def productGet_one(text):
    registered_data, buyer_data, seller_data = refresh_data()
    if text.find(':') != -1:
        item_id = text.split(':')[1]
    elif text.find('：') != -1:
        item_id = text.split('：')[1]
    # 成團狀態判斷
    sta = ''
    current_num = int(seller_data[item_id]['current_number'])
    min_num = int(seller_data[item_id]['group_condition_product_number'][0])
    max_num = int(seller_data[item_id]['group_condition_product_number'][1])

    if current_num < min_num:
        sta = '還差' + str(min_num - current_num) + '個就成團了！'
    elif current_num >= min_num:
        sta = '已經成團！再' + str(max_num - current_num) + '個就達上限囉！'

    # 取貨時段
    trading_time = tradingtime(item_id)

    reply = '名稱：' + seller_data[item_id]['product_name'] + \
            '\n描述：' + seller_data[item_id]['product_description'] + \
            '\n單價：' + '$' + seller_data[item_id]['price'] + \
            '\n取貨地點：' + seller_data[item_id]['trading_location'] + \
            '\n' + trading_time + \
            '\n統計截止時間：' + str(
        time.strftime("%Y/%m/%d  %H:%M", time.struct_time(seller_data[item_id]['group_condition_date']))) + \
            '\n成團狀態：' + sta
    #            '\n團媽的Line_id：' + seller_data[item_id]['Line_id'] + \
    return reply


def tradingtime(item_id):
    registered_data, buyer_data, seller_data = refresh_data()

    # 取貨時段
    trading_time = '取貨時段：'
    i = 0
    for x, y in seller_data[item_id]['trading_time']:
        i = i + 1
        trading_time = trading_time + \
                       '\n  ' + str(i) + ' -> ' + str(
            time.strftime("%Y/%m/%d  %H:%M", time.struct_time(x))) + ' ~ ' + str(
            time.strftime("%H:%M", time.struct_time(y)))
    return trading_time


# ----威澄----

# 以下淑薇(還沒debug)
class production:

    def __init__(self):
        self.item_id = ' '
        self.title = ' '
        self.text = ' '
        self.url = ' '  # 圖片連結
        self.btn1 = ' '  # 查看
        self.btn2 = ' '  # 收藏
        self.btn3 = ' '  # 購買


# 更新產品物件
def new_production_obj(p, item_id):
    registered_data, buyer_data, seller_data = refresh_data()
    p.item_id = item_id
    p.title = seller_data[item_id]['product_name']
    p.text = seller_data[item_id]['product_description']
    p.url = seller_data[item_id]['picture']  # 圖片連結
    p.btn1 = '查看商品:' + item_id  # 查看
    p.btn2 = '新增收藏:' + item_id  # 收藏
    p.btn3 = '加入團購:' + item_id  # 購買

# 商品總攬(自己家的)
def refresh_item(page):  # 暫定1是前五項，2是後五項
    registered_data, buyer_data, seller_data = refresh_data()
    p1 = production()
    p2 = production()
    p3 = production()
    p4 = production()
    p5 = production()
    product = [p1, p2, p3, p4, p5]
    li = []
    for i in seller_data:
        if seller_data[i]["status"] != 3:
            li.append(i)
    if len(li) >= page*5:
        li = li[(page-1)*5:page*5]
    else:
        li = li[-5:]
    p = 0
    for i in li:
        new_production_obj(product[p], i)
        p = p + 1
    page_1 = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url=p1.url,
                    title=p1.title,
                    text=p1.text,
                    actions=[
                        MessageAction(
                            label='查看商品',
                            text=p1.btn1
                        ),
                        MessageAction(
                            label='點擊收藏',
                            text=p1.btn2
                        ),
                        MessageAction(
                            label='點擊購買',
                            text=p1.btn3
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=p2.url,
                    title=p2.title,
                    text=p2.text,
                    actions=[
                        MessageAction(
                            label='查看商品',
                            text=p2.btn1
                        ),
                        MessageAction(
                            label='點擊收藏',
                            text=p2.btn2
                        ),
                        MessageAction(
                            label='點擊購買',
                            text=p2.btn3
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=p3.url,
                    title=p3.title,
                    text=p3.text,
                    actions=[
                        MessageAction(
                            label='查看商品',
                            text=p3.btn1
                        ),
                        MessageAction(
                            label='點擊收藏',
                            text=p3.btn2
                        ),
                        MessageAction(
                            label='點擊購買',
                            text=p3.btn3
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=p4.url,
                    title=p4.title,
                    text=p4.text,
                    actions=[
                        MessageAction(
                            label='查看商品',
                            text=p4.btn1
                        ),
                        MessageAction(
                            label='點擊收藏',
                            text=p4.btn2
                        ),
                        MessageAction(
                            label='點擊購買',
                            text=p4.btn3
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url=p5.url,
                    title=p5.title,
                    text=p5.text,
                    actions=[
                        MessageAction(
                            label='查看商品',
                            text=p5.btn1
                        ),
                        MessageAction(
                            label='點擊收藏',
                            text=p5.btn2
                        ),
                        MessageAction(
                            label='點擊購買',
                            text=p5.btn3
                        )
                    ]
                )
            ]
        )
    )
    return page_1





'''

# 更新按鈕模板

def new_template_btn(p1, p2, p3, p4, p5, p6, p7, p8, p9, p10):
    product = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10]
    li = list(seller_data.keys())

    p = 0

    for i in li:
        if seller_data[i]['status'] != 3:
            new_production_obj(product[p], i)
        p = p + 1
        
# 更新按鈕模板
        
def new_template_btn(p1, p2, p3):
    li = list(seller_data.keys())
    new_production_obj(p1, li[0])
    new_production_obj(p2, li[1])
    new_production_obj(p3, li[2])
'''


# 取消收藏
def favoritePOP(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()

    item_id = text

    # 檢查商品是否存在
    if item_id not in buyer_data[user_id]["favorites"]:
        return '查無此商品!'

    # 刪除收藏
    if item_id in buyer_data[user_id]['favorites']:
        buyer_data[user_id]['favorites'] = [i for i in buyer_data[user_id]['favorites'] if i != item_id]
        #buyer_data[user_id]['favorites'].pop(item_id)

    with open('order.json', 'w', encoding='utf-8-sig') as f2:
        json.dump(buyer_data, f2, ensure_ascii=False, indent=4)
    return '已刪除收藏'


# 查看收藏夾
def favoriteGet(user_id):
    registered_data, buyer_data, seller_data = refresh_data()

    if len(buyer_data[user_id]['favorites']) == 0:
        return "收藏夾是空的!"

    # 查看收藏
    reply = '編號 | 名稱\n'

    for x in buyer_data[user_id]['favorites']:  # 全部收藏
        reply += '\n' + str(x) + '：' + seller_data[str(x)]['product_name']
    return reply

def favorite_get_one(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()
    item_id = text
    if item_id not in buyer_data[user_id]["favorites"]:
        return "收藏裡沒有此商品，請去商品總覽加入收藏!"
    # 成團狀態判斷
    sta = ''
    current_num = int(seller_data[item_id]['current_number'])
    min_num = int(seller_data[item_id]['group_condition_product_number'][0])
    max_num = int(seller_data[item_id]['group_condition_product_number'][1])

    if current_num < min_num:
        sta = '還差' + str(min_num - current_num) + '個就成團了！'
    elif current_num >= min_num:
        sta = '已經成團！再' + str(max_num - current_num) + '個就達上限囉！'

    # 取貨時段
    trading_time = tradingtime(item_id)

    reply = '名稱：' + seller_data[item_id]['product_name'] + \
            '\n描述：' + seller_data[item_id]['product_description'] + \
            '\n單價：' + '$' + seller_data[item_id]['price'] + \
            '\n取貨地點：' + seller_data[item_id]['trading_location'] + \
            '\n' + trading_time + \
            '\n統計截止時間：' + str(
        time.strftime("%Y/%m/%d  %H:%M", time.struct_time(seller_data[item_id]['group_condition_date']))) + \
            '\n成團狀態：' + sta
    #            '\n團媽的Line_id：' + seller_data[item_id]['Line_id'] + \
    return reply

# 買家取消訂單
def orderCancel(user_id, text):  # 取消訂單:33
    registered_data, buyer_data, seller_data = refresh_data()

    item_id = text

    # 檢查是否存在該訂單
    if item_id not in buyer_data[user_id]['current_order'].keys():
        return '查無該筆訂單'
    number = buyer_data[user_id]['current_order'][item_id]['number']
    # 取消訂單
    buyer_data[user_id]['current_order'][item_id]['cancel_If'] = True

    # 將取消的訂單加進history_order
    buyer_data[user_id]['history_order'][item_id] = buyer_data[user_id]['current_order'][item_id]

    buyer_data[user_id]['current_order'].pop(item_id)  # 將取消的訂單從current_order刪掉

    # 在開團資訊紀錄更新
    seller_data[item_id]['current_number'] = seller_data[item_id]['current_number'] - number  # 更新訂單數量
    seller_data[item_id]["customer_id"] = [i for i in seller_data[item_id]["customer_id"] if i[0] != item_id]

    with open('order.json', 'w', encoding='utf-8-sig') as f2:
        json.dump(buyer_data, f2, ensure_ascii=False, indent=4)

    with open('user_dict.json', 'w', encoding='utf-8') as f2:  # json.dump()將資料寫成json檔案
        json.dump(seller_data, f2, ensure_ascii=False, indent=4)

    return '已取消訂單'


# 買家完成訂單 （先不測試～）
def orderFinish(user_id, item_id, rate):
    registered_data, buyer_data, seller_data = refresh_data()

    buyer_data[user_id]['current_order'][str(item_id)]['get_If'] = True
    buyer_data[user_id]['current_order'][str(item_id)]['seller_getRate'] = rate
    buyer_data[user_id]['history_order'][str(item_id)] = buyer_data[user_id]['current_order'][str(item_id)]

    buyer_data[user_id]['current_order'].pop(str(item_id))  # 將完成的訂單從current_order刪掉

    with open('order.json', 'w', encoding='utf-8-sig') as f2:  # json.dump()將資料寫成json檔案
        json.dump(buyer_data, f2, ensure_ascii=False, indent=4)
        f2.close()


# 查看進行中訂單（總覽）
def current_1_order_Read_for_all(user_id):
    registered_data, buyer_data, seller_data = refresh_data()

    order_list = []
    for i in list(buyer_data[user_id]['current_order'].keys()):
        if seller_data[i]["status"] == 1:
            order_list.append(i)

    if len(order_list) == 0:
        return '目前沒有訂單正在進行中喔！'

    # 查看進行中訂單
    reply = '(訂單編號 : 名稱)\n'

    for x in order_list:  # 全部進行中訂單
        reply += "\n" + x + '：' + seller_data[x]['product_name']

    return reply

def current_2_order_Read_for_all(user_id):
    registered_data, buyer_data, seller_data = refresh_data()

    order_list = []
    for i in list(buyer_data[user_id]['current_order'].keys()):
        if seller_data[i]["status"] == 2:
            order_list.append(i)

    if len(order_list) == 0:
        return '目前沒有訂單正在進行中喔！'

    # 查看進行中訂單
    reply = '(訂單編號 : 名稱)\n'

    for x in order_list:  # 全部進行中訂單
        reply += "\n" + x + '：' + seller_data[x]['product_name']

    return reply



# 查看進行中訂單(單筆) ##########################################
def current_order_Read_for_one(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()

    item_id = text

    # 檢查是否存在該訂單
    if item_id not in buyer_data[user_id]['current_order'].keys():
        return '查無該筆訂單'

    T1 = int(buyer_data[user_id]['current_order'][item_id]['pickUp_time'] - 1)
    T2 = int(buyer_data[user_id]['current_order'][item_id]['pickUp_time'] - 1)
    trading_time = str(time.strftime("%Y-%m-%d  %H:%M",
                                     time.struct_time(seller_data[item_id]['trading_time'][T1][0]))) + ' ~ ' + str(
        time.strftime("%H:%M", time.struct_time(seller_data[item_id]['trading_time'][T2][1])))

    reply = '名稱：' + seller_data[item_id]['product_name'] + \
            '\n單價：' + seller_data[item_id]['price'] + \
            '\n描述：' + seller_data[item_id]['product_description'] + \
            '\n取貨地點：' + seller_data[item_id]['trading_location'] + \
            '\n取貨時段：' + trading_time + \
            '\n統計截止時間：' + str(
        time.strftime("%Y-%m-%d %H:%M:%S", time.struct_time(seller_data[item_id]['group_condition_date']))) + \
            '\n開團者的Line_id：' + seller_data[item_id]['Line_id'] + \
            '\n訂單狀態：進行中'

    return reply


# 查看全部歷史訂單
def history_order_Read_for_all(user_id):
    registered_data, buyer_data, seller_data = refresh_data()

    if len(buyer_data[user_id]['history_order']) == 0:
        return '查無歷史訂單！'

    # 查看歷史訂單
    reply = '(編號 : 名稱)\n\n'

    for x in buyer_data[user_id]['history_order'].keys():  # 全部歷史訂單
        reply = reply + str(x) + '：' + seller_data[str(x)]['product_name'] + '\n\n'

    reply = reply + "想查看訂單詳情，請輸入訂單編號"

    return reply


# 查看單筆歷史訂單（詳細資料）
def history_order_Read_for_one(user_id, text):
    registered_data, buyer_data, seller_data = refresh_data()

    item_id = text

    # 檢查是否存在該訂單
    if item_id not in buyer_data[user_id]['history_order'].keys():
        return '查無該筆訂單'

    reply = ''

    T1 = int(buyer_data[user_id]['history_order'][item_id]['pickUp_time'] - 1)
    T2 = int(buyer_data[user_id]['history_order'][item_id]['pickUp_time'] - 1)
    trading_time = str(time.strftime("%Y-%m-%d  %H:%M", time.struct_time(seller_data[item_id]['trading_time'][T1][0]))) + ' ~ ' + str(time.strftime("%H:%M", time.struct_time(seller_data[item_id]['trading_time'][T2][1])))

    if buyer_data[user_id]['history_order'][item_id]["cancel_If"]:
        order_status = "已取消"
    else:
        order_status = "已完成"

    reply = '名稱：' + seller_data[item_id]['product_name'] + \
            '\n單價：' + seller_data[item_id]['price'] + \
            '\n描述：' + seller_data[item_id]['product_description'] + \
            '\n取貨地點：' + seller_data[item_id]['trading_location'] + \
            '\n取貨時段：' + trading_time + \
            '\n統計截止時間：' + str(
        time.strftime("%Y-%m-%d  %H:%M", time.struct_time(seller_data[item_id]['group_condition_date']))) + \
            '\n開團者的Line_id：' + seller_data[item_id]['Line_id'] + \
            '\n訂單狀態：' + order_status

    return reply
