# -*- coding: utf-8 -*-
# @Time: 2023/12/12 23:13
# @Author: Administrator
# @File: read_vpk.py
import struct
from pathlib import Path
from re import findall
from typing import List

import chardet

from common.conf import ModType
from common import vpk_change as vpk, logger
from common.config import vpkConfig
from common.vpk_change import VPK


def open_vpk(path: Path):
    try:
        pak1 = vpk.open(path)
    except UnicodeError:
        pak1 = vpk.open(path, path_enc='ansi')
    except TypeError:
        logger.warning(f'{path}文件打开失败')
        return None
    except struct.error:
        logger.error(f'{path}文件不是vpk文件')
        return False
    except FileNotFoundError as e:
        raise FileNotFoundError(e)
    except Exception as e:
        logger.error(f'{path}文件打开过程中出现错误, 错误信息:{e}')
        return None
    return pak1


def read_addons_txt(path: Path, return_file_list=False):
    config = vpkConfig.get_file_config(path.stem)
    if config and config.get('cache'):
        return config
    return_data = {
        "type": True,
        "content": ""
    }
    if config.get('customTitle'):
        return_data["customTitle"] = config['customTitle']
    pak1 = open_vpk(path)

    if not isinstance(pak1, VPK):
        return_data["type"] = pak1
        return return_data
    try:
        vpk_path_list = [i for i in pak1]
    except Exception as e:
        logger.warning(f'打开vpk文件后,读取文件路径出现错误, 错误文件:{path}')
        logger.exception(e)
        return_data["type"] = False
        return return_data

    for filepath in vpk_path_list:
        if filepath == 'addoninfo.txt':
            with pak1.get_file(filepath) as f_obj:
                content = f_obj.read()
            try:
                try:
                    content = content.decode('utf8')
                except UnicodeError:
                    content = content.decode('gbk')
            except UnicodeError:
                try:
                    res = chardet.detect(content)
                    encoding = res['encoding']
                    if encoding == 'ISO-8859-1':
                        encoding = 'ansi'
                    try:
                        content = content.decode(encoding)
                    except UnicodeError:
                        encoding = 'ISO-8859-1'
                        content = content.decode(encoding)
                except UnicodeError:
                    logger.warning(path)
                    return_data["type"] = False
                else:
                    return_data["type"] = True
            return_data['content'] = content
    if return_file_list:
        return_data['file_list'] = vpk_path_list
    return return_data.copy()


def get_vpk_addon_image_data(path: Path):
    try:
        pak = open_vpk(path)
    except FileNotFoundError:
        return {'title': '打开vpk文件失败', 'content': f'文件 {path.name} 不存在'}
    if not pak:
        return False
    for filepath in pak:
        if filepath != 'addonimage.jpg':
            continue
        with pak.get_file(filepath) as f_obj:
            content = f_obj.read()
            return content


def remove_slash(data):
    if '//' in data:
        count = data.count('//')
        if "http://" in data:
            if count > 1:
                data = data.rsplit('//', maxsplit=1)[0].strip()
        elif count == 1:
            data = data.split('//')[0]
    return data
