# -*- coding: utf-8 -*-
# @Time: 2024/11/28
# @Author: Administrator
# @File: change_cache.py
import traceback
from pathlib import Path
from Crypto.Util.Padding import pad, unpad

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import sys


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

CHILD_MENU = {
    'mac-10': "MAC-10",
    "mp5": "MP5",
    "ak": 'AK',
    'm4': 'M4',
    "sg552": 'SG552',
    'ellis': 'Ellis',
    'coach': 'Coach',
    'nick': 'Nick',
    'rochelle': 'Rochelle'
}


def run(path: Path, refresh_cache=False):
    for i in path.glob('*.cache'):
        res: dict = decrypt_data(i)
        print(i.stem)
        old_father_type = res.get('father_type')
        old_child_type = res.pop('check_type', None)
        cache = res.get('cache')
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

        if old_child_type in CHILD_MENU:
            new_child_type = CHILD_MENU[old_child_type]
        if cache and refresh_cache:
            res['cache'] = False
        print(f'\t新版:{new_child_type}\t{new_father_type}')
        res['father_type'] = new_father_type
        res['child_type'] = new_child_type
        encrypt_data(i, res)


def main():
    folder_path = input('输入旧版本缓存文件夹(可选中文件夹拖动到这里):')
    folder_path = folder_path.replace('"', '')
    path = Path(folder_path)
    print('选择的缓存文件路径为:', path)
    if not path.exists() or not path.is_dir() or not path.is_absolute():
        print('文件路径不存在或者不为文件夹或者不为绝对路径')
        return
    false = False
    while True:
        show = '是否重新解析文件类型,保留自定义标题,n则只修改旧版本缓存文件类型,q则退出\n'
        if false:
            show = '输入错误,'
        refresh_cache = input(f'{show}请选择y或者n或者q:')
        if refresh_cache not in ['n', 'y', 'q']:
            false = True
            continue
        if refresh_cache == 'y':
            refresh_cache = True
        elif refresh_cache == 'n':
            refresh_cache = False
        else:
            print('程序退出')
            sys.exit()
        break
    run(path.absolute(), refresh_cache)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('手动退出, 程序结束...')
        sys.exit()
    except Exception:
        print('出现错误')
        traceback.print_exc()
    else:
        print('替换完成')
    finally:
        try:
            input('回车退出')
        except KeyboardInterrupt:
            pass
