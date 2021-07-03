#!/usr/bin/env python
# coding: utf-8

# In[37]:


import json
import time


# In[134]:


with open("order.json", "r", encoding='utf-8-sig') as f:
    buyer_data = json.load(f)



# In[133]:


with open("user_dict.json", "r", encoding='utf-8') as f:
    seller_data = json.load(f)



# 提醒:
# 1. 取貨時間到之前一天12點提醒
# 2. 購物車貨物到期前一天
# 3. 貨物成團條件達成(通知購物車買家and通知該賣家)
# 4. 賣家廣播

# In[164]:



# In[155]:



# In[ ]:


def f1(user_id,buyer_data,seller_data): #每天凌晨跑一次程式即可
    current_time = time.time()
    text = ""
    for i in buyer_data[user_id]["current_order"]:
        item_name = seller_data[i]['product_name']
        pickup_id = buyer_data[user_id]["current_order"][i]["pickUp_time"]
        trade_place = seller_data[i]["trading_location"]
        pickup_time = seller_data[i]["trading_time"][pickup_id]
        if 0 <= time.mktime(tuple(pickup_time[0]))-time.time() <= 24*60*60:
            text += "請記得在明天"+str(pickup_time[0][3])+"點"+str(pickup_time[0][4])+"分到"+str(pickup_time[1][3])+"點"+str(pickup_time[1][4])+"分到"+trade_place+"面交"+item_name+"!"
        else:
            return False
    return text


# In[160]:


# In[162]:



# In[86]:


def f2(user_id,buyer_data,seller_data):
    current_time = time.time()
    cart_id_list = buyer_data[user_id]["favorites"]
    remind_id_list = []
    for i in cart_id_list:
        if 24*50*60 <=time.mktime(tuple(seller_data[cart_id[i]]['group_condition_date']))-current_time <= 24*60*60 : #假設十分鐘自動執行一次
            remind_id_list += i
    if len(remind_id_list) == 0:
        return False
    else:
        text = seller_data[remind_id_list[0]]["product_name"]
    if len(remind_id_list) >1:
        for i in remind_id_list[1:]:
            text += ", "
            text += seller_data[remind_id_list[i]]["product_name"]
    text = "您的最愛中，"+text+"將在一天後出團!"
    return text


# In[ ]:


#每次買家要下單東西之前，跑這個程式
#若恰好符合團購條件，則return需要傳遞訊息的所有user_id的list，和要傳遞的訊息string
def f3(user_id,seller_data,item_id,item_number):
    item_id = str(item_id)
    item_name = seller_data[item_id]["product_name"]
    condition1 = seller_data[item_id]["current_number"] < seller_data[item_id]["group_condition_product_number"][0]
    condition2 = seller_data[item_id]["group_condition_product_number"][1] >= seller_data[item_id]["current_number"]+item_number >= seller_data[item_id]["group_condition_product_number"][0]
    if condition1 and condition2:
        text = item_name + "已達成團購條件，隨時可以開團!"
        to_list = seller_data[item_id]["customer_id"] #儲存傳訊對象的list(購物車買家and賣家本人的user_id)
        #to_list = [to_list[i][0] for i in range(len(to_list))]
        to_list = user_id
        return text
    else :
        return False


# In[ ]:


# In[57]:


def f4(user_id,item_id,message,seller_data): #user_id代表要求賣家廣播的user_id
    condition1 = user_id == seller_data[item_id]["seller_user_id"] #確認是賣家本人
    condition2 = seller_data[item_id]["status"] < 3
    to_list = seller_data[item_id]["customer_id"] #餐團的買家們的user_id
    to_list = [to_list[i][0] for i in range(len(to_list))]
    if condition1 and condition2:
        return to_list
    else:
        return False

