# -*- coding: utf-8 -*-
# @Time: 2023/12/12 23:13
# @Author: Administrator
# @File: read_vpk.py
import struct
from pathlib import Path
from re import findall
from typing import List

import chardet

from common.conf import ModType, DATA
from common import vpk_change as vpk, logger
from common.config import vpkConfig
from common.vpk_change import VPK


def open_vpk(path: Path):
    try:
        pak1 = vpk.open(path)
    except UnicodeError:
        pak1 = vpk.open(path, path_enc='ansi')
    except TypeError:
        logger.error(f'{path}文件打开失败')
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

def _decode_file(content: bytes):
    """
    二进制文件解码返回数据
    :param content:
    :return:
    """
    try:
        try:
            result = content.decode('utf8')
        except UnicodeError:
            result = content.decode('gbk')
    except UnicodeError:
        try:
            res = chardet.detect(content)
            encoding = res['encoding']
            if encoding == 'ISO-8859-1':
                encoding = 'ansi'
            try:
                result = content.decode(encoding)
            except UnicodeError:
                encoding = 'ISO-8859-1'
                result = content.decode(encoding)
        except UnicodeError:
            logger.warning(f'解码失败:{path}')
            return False
    return result

def read_addons_txt(path: Path, return_file_list=False, refresh_file=False):
    config = vpkConfig.get_file_config(path.stem)
    if config:
        # 修改缓存中的信息 把addinfo文件内容存放到file_info中
        if 'file_info' not in config:
            tmp = {}
            for i in ['content', 'father_type', 'child_type', 'customTitle', 'cache']:
                if i not in config:
                    continue
                tmp[i] = config.pop(i)
            for key in DATA:
                if key in config:
                    config[key] = config.pop(key.lower())
            tmp['file_info'] = config.copy()
            config = tmp.copy()
            vpkConfig.change_file_config(path.stem, config)
    if refresh_file is False:
        if config and config.get('cache'):
            if config.get('customTitle'):
                logger.info(f'mod {path.stem} 存在自定义标题:{config["customTitle"]}')
            # 加载缓存
            return config
    else:
        config.pop('file_info')
        if config.get('content'):
            config['content'] = ''
    return_data = {
        "type": True,
        "content": ""
    }
    return_data.update(config)
    if config.get('customTitle'):
        return_data["customTitle"] = config['customTitle']
        logger.info(f'mod {path.stem} 存在自定义标题:{return_data["customTitle"]}')
    pak1 = open_vpk(path)

    if not isinstance(pak1, VPK):
        return_data["type"] = pak1
        # 打开失败 不是vpk,打开过程出现错误
        return return_data
    try:
        with pak1.get_file('addoninfo.txt') as f:
            content = f.read()
        result = _decode_file(content)
        if result is False:
            return_data["type"] = False
        else:
            return_data["content"] = result
    except KeyError:
        # 没有 addoninfo.txt 会抛异常 KeyError
        pass
    if return_file_list:
        try:
            vpk_path_list = [i for i in pak1]
        except Exception as e:
            logger.warning(f'打开vpk文件后,读取文件路径出现错误, 错误文件:{path}')
            logger.exception(e)
            return_data["type"] = False
            return return_data
        return_data['file_list'] = vpk_path_list
    # 无缓存,打开的时候解析
    return return_data.copy()


def get_vpk_addon_image_data(path: Path):
    try:
        pak = open_vpk(path)
    except FileNotFoundError:
        return {'title': '打开vpk文件失败', 'content': f'文件 {path.name} 不存在'}
    if not pak:
        return False
    try:
        with pak.get_file('addonimage.jpg') as f:
            content = f.read()
            return content
    except KeyError:
        return False


def remove_slash(data):
    if '//' in data:
        count = data.count('//')
        if "http://" in data:
            if count > 1:
                data = data.rsplit('//', maxsplit=1)[0].strip()
        elif count == 1:
            data = data.split('//')[0]
    return data


if __name__ == '__main__':
    import vdf
    import json

    path = Path(r'F:\求生之路2\addons\2378181958.vpk')
    res = read_addons_txt(path, refresh_file=True)
    print(json.dumps(res, ensure_ascii=False, indent=4))
    res = vdf.loads(res['content'])
    print(json.dumps(res, ensure_ascii=False, indent=4))
