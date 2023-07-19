import uuid
import random
import math
import hashlib

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
