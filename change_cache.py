# -*- coding: utf-8 -*-
# @Time: 2024/11/28
# @Author: Administrator
# @File: change_cache.py
from pathlib import Path
from Crypto.Util.Padding import pad, unpad

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def generate_key_and_iv():
    key = get_random_bytes(16)  # 128-bit 密钥
    iv = get_random_bytes(16)  # 128-bit IV
    return key, iv


KEY, IV = generate_key_and_iv()
BLOCK_SIZE = 1024 * 1024


def encrypt_data(file, data: dict):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    with open(file, 'wb') as f:
        f.write(KEY)
        f.write(IV)
        encrypted_chunk = cipher.encrypt(pad(str(data).encode('utf8'), AES.block_size))
        f.write(encrypted_chunk)


def decrypt_data(file):
    with open(file, 'rb') as f:
        key = f.read(16)
        iv = f.read(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypt = unpad(cipher.decrypt(f.read()), AES.block_size)
        return eval(decrypt)


FATHER_MENUS = {
    "survivors": '幸存者',
    "infected": "特感",
    "weapons": "武器",
    "jinzhan": '近战',
    'drug': '医疗品',
    "throw": "投掷",
    "items": "杂项",
    "ammo": "弹药",
    'map': '地图',
    'other': '其他'
}

path = Path(r'F:\pythonData\left4dead2\Cache')
for i in path.glob('*.cache'):
    res: dict = decrypt_data(i)
    print(i.stem)
    old_father_type = res.get('father_type')
    old_child_type = res.pop('check_type', None)
    new_father_type = ''
    new_child_type = ''
    print(f'\t原版:{old_child_type}\t{old_father_type}')
    if old_father_type is None or old_father_type == '':
        if old_child_type:
            new_father_type = FATHER_MENUS[old_child_type]
        else:
            new_father_type = '其他'
            new_child_type = ''
    else:
        new_father_type = FATHER_MENUS.get(old_father_type)
        new_child_type = old_child_type
    print(f'\t新版:{new_child_type}\t{new_father_type}')
    res['father_type'] = new_father_type
    res['child_type'] = new_child_type
    encrypt_data(i, res)