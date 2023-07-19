import uvicorn
import requests
import json
import uuid
import random
import math
import hashlib
from fastapi import FastAPI, File, UploadFile
from config import Config
from typing import List
from datetime import datetime
import os
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

app = FastAPI(title="Buyer's order rating API", description="API đánh giá đơn hàng Shopee")
cfg = Config()

@app.post("/get_account_info")
def get_account_info(cookie:str):
    api = cfg.get_shopee_api().get('get_account_info')
    r = requests.get(api, headers={'Cookie':cookie})
    return r.json()

@app.post("/get_unrated_orders")
def get_unrated_orders(cookie:str):
    api = cfg.get_shopee_api().get('get_all_order')
    params = {
        'limit':1,
        'offset':0,
        'list_type':3
    }
    r = requests.get(api, headers={'Cookie':cookie, 'X-Api-Source':'pc'}, params=params)
    order_data = r.json()['data']['details_list'][0]
    list_order_products_data = order_data['info_card']['order_list_cards'][0]['product_info']['item_groups']
    list_products = []
    for product in list_order_products_data:
        item_id = product['items'][0]['item_id']
        item_name = product['items'][0]['name']
        model_name = product['items'][0]['model_name']
        list_products.append({'item_id':item_id, 'item_name':item_name, 'model_name':model_name})
    can_rate_order = {
        'order_id': order_data['info_card']['order_id'],
        'shop_id': order_data['info_card']['order_list_cards'][0]['shop_info']['shop_id'],
        'list_products':list_products
    }
    return can_rate_order

def get_signature():
    r = str(datetime.timestamp(datetime.now()))[0:10]
    aha = ''
    e = str(uuid.uuid4()).replace('-','')
    print(e)
    t = 4103
    temp = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(0,6):
        aha += temp[math.floor(random.random() * len(temp))]
    bha = '{}@{}@{}@shopee@{}'.format(aha, e, t, r)
    print(bha)
    return '{}-{}-{}'.format(aha, hashlib.md5(bha.encode()).hexdigest(), r)

@app.post('/rate_order')
def rate_order(order_id:int, shop_id:int, list_product_ids: str, cookie:str, files: List[UploadFile] = File(...)):
    # Confirm delivered API
    confirm_delivered_api = cfg.get_shopee_api().get('confirm_deliverd_order')
    confirm_order = {
        'order_id':order_id
    }
    r_confirm = requests.post(confirm_delivered_api, headers={'Cookie':cookie, 'X-Api-Source':'pc'}, data=confirm_order)
    print('Order deliver confirmed')
    
    # Upload rate images
    for file in files:
        print(file)
        # Call API for each file
    
    # Create rate form and call rate order api
    rate_order_api = cfg.get_shopee_api().get('rate_order')
    list_rate_products = []
    for product_id in list_product_ids.split(','):
        rate_product_form = {
            "itemid": int(product_id),
            "product_quality": 5,
            "comment": "",
            "photos": [],
            "videos": [],
            "tagids": [],
            "anonymous": False,
            "template_tag_comments": {
                "Đúng với mô tả": "Tuyệt",
                "Màu sắc": "Chuẩn",
                "Chất liệu": "Tuyệt"
            }
        }
        list_rate_products.append(rate_product_form)
    rate_form = {
        "shopid": shop_id,
        "orderid": order_id,
        "objectid": 0,
        "seller_service": 5,
        "delivery_service": 5,
        "rate_items_data": list_rate_products,
        "is_media_gray_user": True,
        "apply_coin_limits_validate": True,
        "api_version": 2
    }
    json_params = json.dumps(rate_form)
    print(json_params)
    r = requests.post(rate_order_api, headers={'Cookie':cookie, 'X-Api-Source':'pc'}, data=json_params)
    return {'data': r.json()}

@app.get('/generate_signature')
def test():
    a = get_signature()
    return {'cc':a}

@app.post('/test_decrypt_token')
def test_decrypt_token(token: str, request_id: str):
    # Test
    #Token
    data = b64decode(token)
    #Request-id
    key = request_id.encode(encoding = 'UTF-8')
    iv = "1234567887654321".encode(encoding = 'UTF-8')

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(data), 16)

    print(decrypted)
    print(b64decode(decrypted))
    return { 'Authorization': decrypted}

if __name__ == "__main__":
    uvicorn.run(app=app, host='0.0.0.0',port=2210)