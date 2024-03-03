# -*- coding: utf-8 -*-
# @Time: 2023/12/12 23:13
# @Author: Administrator
# @File: read_vpk.py
import struct
from pathlib import Path
from re import findall

import chardet

from common.conf import ModType
from . import vpk_change as vpk, logger
from .config.main_config import vpkConfig
from .vpk_change import VPK


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
    return pak1


def read_addons_txt(path: Path, return_file_type=False):
    config = vpkConfig.get_file_config(path.stem)
    if config:
        return config
    return_data = {
        "type": True,
        "content": ""
    }
    pak1 = open_vpk(path)
    # 是否需要跳过
    need_break = False
    # 是否判断了类型
    had_type = False
    goods = {}
    if not isinstance(pak1, VPK):
        return_data["type"] = pak1
        return return_data
    if return_file_type:
        for father_key, father_value in ModType.weapons_goods().items():
            goods[father_key] = {}
            for child_key, child_value in father_value.items():
                child_value: list
                if not child_value:
                    child_value.append(child_key)
                new_value = []
                for i in child_value[:]:
                    i: str
                    new_value.append(i)
                    if ' ' in i:
                        new_value.append(i.replace(" ", ''))
                        new_value.append(i.replace(' ', '_'))
                goods[father_key][child_key] = new_value
        try:
            filepath_list = [i for i in pak1]
        except Exception as e:
            logger.warning(f'打开vpk文件后,读取文件路径出现错误, 错误文件:{path}')
            logger.exception(e)
            return_data["type"] = False
            return return_data
        for i in filepath_list:
            if i.startswith('maps/') or findall('materials/.*?/maps/.*', i):
                return_data['check_type'] = 'map'
                had_type = True
                break
            if i.startswith('models/xdreanims'):
                return_data['check_type'] = 'other'
                need_break = True
                break
    for filepath in pak1:
        filepath: str
        if filepath == 'addoninfo.txt':
            with pak1.get_file(filepath) as f_obj:
                content = f_obj.read()
            try:
                content = content.decode()
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
        else:
            if not return_file_type or had_type or need_break or not _check_file_name(filepath):
                continue
            if filepath.startswith('models/infected/'):
                update, had_type = _check_infected(filepath)
                if had_type:
                    return_data.update(update)
            # 枪械 近战
            if findall(r'^(?:materials/)?models(?:/[vw]_models)?/(weapons).*$', filepath):
                update, had_type = _check_type(filepath, path.stem, goods)
                if had_type:
                    return_data.update(update)
            # 角色
            survivors = findall(r'models/survivors/survivor_(.+)\.mdl', filepath)
            if survivors:
                update, had_type = _check_survivors(survivors)
                if had_type:
                    return_data.update(update)

    if return_file_type:
        if not had_type:
            return_data["check_type"] = 'other'
        vpkConfig.change_file_config(path.stem, return_data)
    return return_data.copy()


def _check_survivors(survivors: list):
    survivors_dict = ModType.SURVIVORS.data()
    for key, survivor_list in survivors_dict.items():
        for survivor in survivor_list:
            if survivor in survivors:
                return {'check_type': key, 'father_type': ModType.SURVIVORS.value}, True
    return {}, False


def _check_file_name(file_path: str):
    if file_path.endswith('.mdl') or file_path.endswith('.vtf') or file_path.endswith('.vmt'):
        return True
    return False


def _check_type(file_path, file_name, goods: dict) -> tuple:
    path = file_path.split('/weapons/')[1]
    # logger.debug(f"{file_name} {file_path}, path: {path}, goods: {goods}")
    for k, v in goods.items():
        for key, value in v.items():
            for good_name in value:
                pattern = fr'(?<![a-zA-Z]){good_name}(?![a-zA-Z])'
                if findall(pattern, path):
                    return {'check_type': key, 'father_type': k}, True

    return {}, False


def _check_infected(file_path) -> tuple:
    infected = ModType.INFECTED.data()
    for i in infected.keys():
        for j in infected[i]:
            pattern = fr'(?<![a-zA-Z]){j}(?![a-zA-Z])'
            if findall(pattern, file_path):
                return {'check_type': i, 'father_type': ModType.INFECTED.value}, True
    return {}, False


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
