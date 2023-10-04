import uvicorn
import requests
import json
import re
import json
import random

from fastapi import FastAPI, File, UploadFile
from config import Config
from utils import get_signature, decrypt_token
from loguru import logger
from process import get_cookie_string


app = FastAPI(title="Buyer's order rating API",
              description="API đánh giá đơn hàng Shopee")
cfg = Config()


@app.get("/get_account_info")
async def get_account_info(cookie: str, username: str, password: str):
    cookie_string, x_csrftoken = await get_cookie_string(cookie, username, password)
    logger.info('%s' % cookie_string)
    api = cfg.get_shopee_api().get('get_account_info')
    r = requests.get(
        api, headers={'Cookie': cookie_string})
    return r.json()


def get_unconfirmed_orders(cookie,x_csrftoken):
    api = cfg.get_shopee_api().get('get_all_order')
    params = {
        'limit': 15,
        'offset': 0,
        'list_type': 8
    }
    r = requests.get(
        api, headers={'Cookie': cookie, 'X-Api-Source': 'pc', 'X-Csrftoken':x_csrftoken}, params=params)
    
    if r.json()['data']['next_offset'] == -1:
        return {
            'error': 0,
            'data': []
        }
    else:
        list_unconfirmed = []
        orders_data = r.json()['data']['details_list']
        for order in orders_data:
            list_order_products_data = order['info_card'][
                'order_list_cards'][0]['product_info']['item_groups'][0]['items']
            list_products = []
            for product in list_order_products_data:
                item_id = product['item_id']
                item_name = product['name']
                model_name = product['model_name']
                list_products.append(
                    {'item_id': item_id, 'item_name': item_name, 'model_name': model_name})
            can_confirm_order = {
                'order_id': order['info_card']['order_id'],
                'shop_id': order['info_card']['order_list_cards'][0]['shop_info']['shop_id'],
                'list_products': list_products
            }
            list_unconfirmed.append(can_confirm_order)
        return {
            'error': 0,
            'data': list_unconfirmed
        }


def get_unrated_orders(cookie,x_csrftoken):
    api = cfg.get_shopee_api().get('get_all_order')
    params = {
        'limit': 15,
        'offset': 0,
        'list_type': 3
    }
    r = requests.get(
        api, headers={'Cookie': cookie, 'X-Api-Source': 'pc', 'X-Csrftoken':x_csrftoken}, params=params)
    logger.info(r.json())
    if r.json()['data']['next_offset'] == -1:
        return {
            'error': 0,
            'data': []
        }
    else:
        list_unrated = []
        orders_data = r.json()['data']['details_list']
        # logger.info(orders_data)
        for order in orders_data:
            # Check if order is unrated
            if order['status']['header_text']['text'] == 'order_status_text_completed_buyer_not_rated_can_rate' or order['status']['header_text']['text'] == 'order_status_text_completed_return_refund_by_date':
                list_order_products_data = order['info_card'][
                    'order_list_cards'][0]['product_info']['item_groups'][0]['items']
                list_products = []
                for product in list_order_products_data:
                    item_id = product['item_id']
                    item_name = product['name']
                    model_name = product['model_name']
                    list_products.append(
                        {'item_id': item_id, 'item_name': item_name, 'model_name': model_name})
                can_rate_order = {
                    'order_id': order['info_card']['order_id'],
                    'shop_id': order['info_card']['order_list_cards'][0]['shop_info']['shop_id'],
                    'list_products': list_products
                }
                list_unrated.append(can_rate_order)
        logger.info(list_unrated)
        return {
            'error': 0,
            'data': list_unrated
        }


@app.post('/preupload')
async def preupload(cookie: str):
    preupload_api = cfg.get_shopee_api().get('preupload')
    sign, request_id = get_signature()
    preupload_payload = {
        "_header": {
            "version": 1,
            "sign": sign,
            "biz": 4103,
            "app_version": "mms-2.3.1",
            "sdk_version": "mms-2.3.1",
            "os_type": 2,
            "request_id": request_id,
            "device_model": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "client_region": "VN"
        },
        "count": 1
    }
    headers = {
        'Content-Type': 'application/json',
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    preupload_rs = requests.post(
        url=preupload_api, headers=headers, data=json.dumps(preupload_payload)).json()
    logger.info(request_id)
    return preupload_rs


@app.post('/decrypt')
async def decrypt(token: str, request_id: str):
    authorization = decrypt_token(token=token, request_id=request_id)
    return authorization



@app.post('/rate_order')
async def rate_order(cookie: str, username: str, password: str, comment:str):
    try:
        cookie_string, x_csrftoken = await get_cookie_string(cookie, username, password)
        logger.info(cookie_string)
        logger.info(x_csrftoken)
        list_comments = comment.split(',')

        logger.info('LẤY DANH SÁCH ĐƠN CHƯA XÁC NHẬN HOÀN THÀNH')
        # Get unconfirmed orders and process confirm
        unconfirmed_orders = get_unconfirmed_orders(cookie=cookie_string,x_csrftoken=x_csrftoken)['data']
        logger.info(unconfirmed_orders)

        # Confirm delivered API
        if len(unconfirmed_orders) != 0:
            logger.info('XÁC NHẬN HOÀN THÀNH')
            confirm_delivered_api = cfg.get_shopee_api().get('confirm_deliverd_order')

            for order in unconfirmed_orders:
                confirm_order = {
                    'order_id': int(order['order_id'])
                }
                json_params = json.dumps(confirm_order)
                confirm_deliverd_request = requests.post(confirm_delivered_api, headers={
                    'Cookie': cookie_string, 
                    'X-Csrftoken':x_csrftoken,
                    'Content-Type': 'application/json'}, data=json_params)
                logger.info(confirm_deliverd_request.json())
                logger.info('Order %s confirmed delivery' % order['order_id'])

        logger.info('LẤY DANH SÁCH ĐƠN CHƯA ĐÁNH GIÁ')
        unrated_orders = get_unrated_orders(cookie=cookie_string,x_csrftoken=x_csrftoken)['data']
        if len(unrated_orders) != 0:
            rate_order_api = cfg.get_shopee_api().get('rate_order')
            count = 0
            for order in unrated_orders:
                try:
                    logger.info('ĐÁNH GIÁ')
                    # preupload_api = cfg.get_shopee_api().get('preupload')
                    # upload_api = cfg.get_shopee_api().get('upload')

                    # Upload rate images
                    # list_upload_img_ids = []
                    # for file in files:
                    #     request_object_content = await file.read()
                    #     image = Image.open(io.BytesIO(request_object_content)).convert('RGB')
                    #     image = (np.array(image) * 255).round().astype(np.uint8)
                    #     print(image)
                    #     # Call API for each file
                    #     sign, request_id = get_signature()
                    #     preupload_payload = {
                    #         "_header": {
                    #             "version": 1,
                    #             "sign": sign,
                    #             "biz": 4103,
                    #             "app_version": "mms-2.3.1",
                    #             "sdk_version": "mms-2.3.1",
                    #             "os_type": 2,
                    #             "request_id": request_id,
                    #             "device_model": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    #             "client_region": "VN"
                    #         },
                    #         "count": 1
                    #     }
                    #     headers = {
                    #         'Content-Type': 'application/json',
                    #         'Cookie': cookie,
                    #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
                    #     }
                    #     preupload_rs = requests.post(
                    #         url=preupload_api, headers=headers, data=json.dumps(preupload_payload)).json()
                    #     logger.info(preupload_rs)
                    #     img_ids = preupload_rs['data']['img_ids'][0]
                    #     token = preupload_rs['data']['services'][0]['token']
                    #     logger.info(img_ids)
                    #     logger.info(token)
                    #     url_upload = '{}/{}'.format(upload_api, img_ids)
                    #     logger.info(url_upload)
                    #     authorization = decrypt_token(token=token, request_id=request_id)
                    #     logger.info(authorization)
                    #     list_upload_img_ids.append(img_ids)
                    # logger.info(list_upload_img_ids)

                    # Create rate form and call rate order api
                    list_rate_products = []
                    for product in order['list_products']:
                        rate_product_form = {
                            "itemid": int(product['item_id']),
                            "product_quality": 5,
                            "comment": random.choice(list_comments),
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
                        "shopid": order['shop_id'],
                        "orderid": order['order_id'],
                        "objectid": 0,
                        "seller_service": 5,
                        "delivery_service": 5,
                        "rate_items_data": list_rate_products,
                        "is_media_gray_user": True,
                        "apply_coin_limits_validate": True,
                        "api_version": 2
                    }
                    json_params = json.dumps(rate_form)
                    rate_order_request = requests.post(rate_order_api, headers={
                        'Cookie': cookie_string , 
                        'X-Api-Source': 'pc', 
                        'Referer': 'https://shopee.vn/user/purchase/?type=3', 
                        'X-Csrftoken': x_csrftoken, 
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76'
                    }, data=json_params)
                    logger.info(rate_order_request.json())
                    count += 1
                except Exception as ex:
                    logger.info(str(ex))
                    return {
                        'status_code': 406,
                        'total_unrated_order': len(unrated_orders),
                        'done': count,
                        'description': 'XỬ LÍ KHÔNG THÀNH CÔNG'
                }
            return {
                'status_code': 200,
                'total_unrated_order': len(unrated_orders),
                'done': count,
                'description': 'XỬ LÍ THÀNH CÔNG'
            }
        else:
            return {
                'status_code': 200,
                'total_unrated_order': 0,
                'done': 0,
                'description': 'KHÔNG CÓ ĐƠN HÀNG CẦN XỬ LÍ'
            }
    except Exception as ex:
        logger.info(str(ex))
        return {
                'status_code': 406,
                'total_unrated_order': 0,
                'done': 0,
                'description': 'XỬ LÍ KHÔNG THÀNH CÔNG'
            }
            


if __name__ == "__main__":
    uvicorn.run(app=app, host='0.0.0.0', port=7878)
