import uuid
import random
import math
import hashlib
import re
import json

from datetime import datetime
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt_token(token: str, request_id: str):
    # Token
    data = b64decode(token)
    # Request-id
    key = request_id.encode(encoding='UTF-8')
    iv = "1234567887654321".encode(encoding='UTF-8')

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(data), 16)
    return {'Authorization': decrypted}


def get_signature():
    r = str(datetime.timestamp(datetime.now()))[0:10]
    aha = ''
    e = str(uuid.uuid4()).replace('-', '')
    t = 4103
    temp = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    for i in range(0, 6):
        aha += temp[math.floor(random.random() * len(temp))]
    bha = '{}@{}@{}@shopee@{}'.format(aha, e, t, r)
    return '{}-{}-{}'.format(aha, hashlib.md5(bha.encode()).hexdigest(), r), e


def cookies_to_json(e):
    t = re.search(r'(\.|)shopee(.*?)$', e)
    i = ""
    if not t:
        return ""

    t = t.group(0).split(";")
    for item in t:
        if item:
            s = item.split("=")
            c = s[0]
            r = s[1]
            value_match = re.search(c + "=" + r + "=(.*?)$", item)
            if value_match:
                value = value_match.group(1).replace('"', "")
                cookie_data = {
                    "domain": c,
                    "name": r,
                    "path": "/",
                    "value": value
                }
                i += json.dumps(cookie_data) + ","

    i = "[" + i[:-1] + "]"
    return i
