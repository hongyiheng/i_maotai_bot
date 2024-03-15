import base64
import hashlib
import json
from datetime import datetime, timezone, timedelta

import requests
from actions_toolkit import core
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class MaoTai:

    def __init__(self, aes_key, aes_iv, text):
        self.aes_key = aes_key
        self.aes_iv = aes_iv
        self.text = text

    def signature(self, content, cur_time):
        text = self.text + content + str(cur_time)
        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
        return md5

    def aes_encrypt(self, params):
        aes_key = self.aes_key
        aes_iv = self.aes_iv

        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_params = padder.update(params.encode('utf-8')) + padder.finalize()

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
        encryptor = cipher.encryptor()

        encrypted_data = encryptor.update(padded_params) + encryptor.finalize()
        encrypted_base64 = base64.b64encode(encrypted_data).decode('utf-8')

        return encrypted_base64

    def get_session_id(self):
        url = "https://static.moutai519.com.cn/mt-backend/xhr/front/mall/index/session/get/"
        tz = timezone(timedelta(hours=8))
        now = datetime.now(tz)
        today_begin = datetime(now.year, now.month, now.day, tzinfo=tz)
        ts = int(today_begin.timestamp() * 1000)

        rep = requests.get(url + str(ts))
        return rep.json()['data']['sessionId']

    def reservation(self, i_user, item_id, shop_id):
        url = "https://app.moutai519.com.cn/xhr/front/mall/reservation/add"

        item_info = [{"count": 1, "itemId": item_id}]
        data = {
            "itemInfoList": item_info,
            "sessionId": self.get_session_id(),
            "userId": str(i_user["userId"]),
            "shopId": shop_id
        }
        data['actParam'] = self.aes_encrypt(json.dumps(data))

        headers = {
            "MT-Lat": i_user["lat"],
            "MT-Lng": i_user["lng"],
            "MT-Token": i_user["token"],
            "MT-Info": "028e7f96f6369cafe1d105579c5b9377",
            "MT-Device-ID": i_user["deviceId"],
            "MT-APP-Version": i_user["mt_version"],
            "User-Agent": "iOS;16.3;Apple;?unrecognized?",
            "Content-Type": "application/json",
            "userId": str(i_user["userId"])
        }

        rep = requests.post(url, headers=headers, data=json.dumps(data))
        print(rep.json())


if __name__ == '__main__':
    user = core.get_input('user')
    item_ids = core.get_input('item_ids')
    shop_id = core.get_input('shop_id')
    aes_key = core.get_input('aes_key')
    aes_iv = core.get_input('aes_iv')
    salt = core.get_input('salt')

    m = MaoTai(bytes(aes_key, 'utf-8'), bytes(aes_iv, 'utf-8'), salt)
    for item_id in item_ids.split(","):
        m.reservation(json.loads(user), item_id, shop_id)
