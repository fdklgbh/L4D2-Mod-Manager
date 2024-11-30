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
    # 是否判断了类型
    had_type = False
    goods = ModType.weapons_goods()
    if not isinstance(pak1, VPK):
        return_data["type"] = pak1
        return return_data

    file_path_dict = {}
    need_continue = False
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

    if return_file_type:
        for filepath in vpk_path_list:
            if filepath.startswith('maps/') or filepath.startswith('missions/') or findall('materials/.*?/maps/.*',
                                                                                           filepath):
                return_data['father_type'] = '地图'
                return_data['child_type'] = ''
                had_type = True
        for filepath in vpk_path_list:
            filepath: str
            if had_type:
                break
            if filepath.startswith('materials/skybox') and Path(filepath).stem.startswith('sky_'):
                return_data['child_type'] = '天空盒'
                return_data['father_type'] = '杂项'
                need_continue = True
            elif filepath.startswith('models/xdreanims'):
                return_data['father_type'] = '其他'
                return_data['child_type'] = ''
                need_continue = True
            if need_continue:
                had_type = True
                file_path_dict = {}
                continue
            if _check_file_name(filepath, 'mdl'):
                file_path_dict.setdefault('mdl', [])
                file_path_dict['mdl'].append(filepath)
            elif _check_file_name(filepath, 'vtf'):
                file_path_dict.setdefault('vtf', [])
                file_path_dict['vtf'].append(filepath)
            elif _check_file_name(filepath, 'vmt'):
                file_path_dict.setdefault('vmt', [])
                file_path_dict['vmt'].append(filepath)
            if not any([filepath.startswith('map'), filepath.endswith('.txt'), filepath.endswith('.vtx'),
                        filepath.endswith('.vvd'), filepath.endswith('.phy'), filepath.endswith('.jpg')]):
                file_path_dict.setdefault('path', [])

                file_path_dict['path'].append(filepath)
        if not had_type:
            # 特感
            update = _check_infected(file_path_dict, path.stem)
            if update:
                return_data.update(update)
                had_type = True
        if not had_type:
            # 角色
            return_data, had_type = _check_survivors(file_path_dict, return_data)
        if not had_type:
            return_data, had_type = _check_weapon(file_path_dict, goods, return_data)

        if not had_type:
            return_data["father_type"] = '其他'
            return_data['child_type'] = ''
        vpkConfig.change_file_config(path.stem, return_data)
    return return_data.copy()


def _check_survivors(file_path_dict: dict, return_data):
    mdl_path = file_path_dict.get('mdl', [])
    survivors_dict = ModType.SURVIVORS.data()
    for mdl in mdl_path:
        result = findall(r'models/survivors/survivor_(.+)\.mdl', mdl)
        if result:
            for key, survivor in survivors_dict.items():
                if key == '语音':
                    continue
                if result[0].lower() == survivor:
                    return_data.update({'child_type': key, 'father_type': ModType.SURVIVORS.value})
                    return return_data, True
    path = file_path_dict.get('path', [])
    for path in path:
        if findall(r'^sound/player/survivor/voice/(?:coach|gambler|mechanic|producer|biker|teengirl|namvet|manager).*?\.wav$',
                   path):
            return_data.update({'child_type': '语音', 'father_type': ModType.SURVIVORS.value})
            return return_data, True
    return return_data, False


def _check_file_name(file_path: str, check_suffix: str = None):
    """
    vmt 材质信息 以及路径
    vtf 贴图文件
    :param file_path:
    :return:
    """
    if check_suffix:
        return file_path.endswith('.' + check_suffix)

    if file_path.endswith('.mdl') or file_path.endswith('.vtf') or file_path.endswith('.vmt'):
        return True
    return False


def _check_weapon(file_path_dict: dict, goods: dict, return_data) -> tuple:
    """
    检查其他类型
    :param file_path_dict: vpk文件数据
    :param goods: 分类信息(排除人物 特感)
    :param return_data: 返回数据 检查出类型后,需要update进去,
    :return: return_data, True/False
    """

    def return_info(child_type, faster_type):
        return_data.update({'child_type': child_type, 'father_type': faster_type})
        return return_data, True

    def check_mdl_vmt_vtf(file_path, data_list: list):
        if not data_list:
            return False
        if Path(file_path).stem in data_list:
            return True
        return False

    def check_path(file_path: List[str], need_path: List[str], regex=False):
        if not need_path:
            return False
        for need in need_path:
            for file in file_path:
                if regex:
                    if findall(need, file):
                        return True
                if file.startswith(need):
                    return True
        return False

    def check_type(data_list, file_suffix):
        if not data_list:
            return False
        for data in data_list:
            for k, v in goods.items():
                v: dict
                if k == '语音':
                    continue
                if k in ['武器', '近战', '医疗品', '投掷'] and not findall(
                        r'^(?:materials/)?models(?:/[vw]_models)?.*$', data):
                    continue
                # 只有顶级分类
                if v.get('no_child'):
                    v_data = v.get(file_suffix, [])
                    if check_mdl_vmt_vtf(data, v_data):
                        return return_info('', k)
                    continue
                # 二级分类
                for key, value in v.items():
                    value_mdl: list = value.get(file_suffix, [])
                    if not value_mdl:
                        continue
                    if check_mdl_vmt_vtf(data, value_mdl):
                        return return_info(key, k)

    # 检查mdl文件
    res = check_type(file_path_dict.get('mdl', []), 'mdl')
    if res:
        return res
    # 检查vtf文件
    res = check_type(file_path_dict.get('vtf', []), 'vtf')
    if res:
        return res
    # 检查vmt
    res = check_type(file_path_dict.get('vmt', []), 'vmt')
    if res:
        return res
    # 目录
    filepath_list: list = file_path_dict.get('path', [])
    for father, child in goods.items():
        child: dict
        if child.get('no_child'):
            if check_path(filepath_list, child.get('path'), child.get('regex', False)):
                return return_info(father, '')
            continue
        for chile_key, chile_value in child.items():
            if check_path(filepath_list, chile_value.get('path', []), chile_value.get('regex', False)):
                return return_info(chile_key, father)
    return return_data, False


def _check_infected(file_info: dict, tmp) -> dict:
    """
    特感类型
    :param file_info: mod文件中数据信息
    :return:
    """
    infected = ModType.INFECTED.data()
    mdl_data: List[str] = file_info.get('mdl', [])
    # infected_mdl = infected['mdl']
    for file_path in mdl_data:
        if not file_path.startswith('models/infected/'):
            continue
        name = Path(file_path).stem
        for i in infected.keys():
            if name in infected[i].get('mdl', []):
                return {'child_type': i, 'father_type': ModType.INFECTED.value}
    folder_list = []
    for file_path in file_info.get('vtf', []) + file_info.get('vmt', []):
        if not file_path.startswith('materials/models/infected'):
            continue
        folder = file_path.replace('materials/models/infected/', '').split('/')[0]
        if folder not in folder_list:
            folder_list.append(folder)
    sound_regex = infected.get('语音').get('path', [])
    for file in file_info.get('path', []):
        for regex in sound_regex:
            if findall(regex, file):
                return {'child_type': '语音', 'father_type': ModType.INFECTED.value}
    if not folder_list:
        return {}
    if len(folder_list) > 1:
        return {'child_type': '多种特感', 'father_type': ModType.INFECTED.value}
    else:
        for i in infected.keys():
            if folder_list[0] == infected[i]['folder']:
                print('3' * 10)
                return {'child_type': i, 'father_type': ModType.INFECTED.value}


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
