# -*- coding: utf-8 -*-
# @Time: 2023/12/31
# @Author: Administrator
# @File: thread.py
import os
import re
from copy import deepcopy
from pathlib import Path
from typing import List, Union

import requests
import urllib3
import vdf
from PyQt5.QtCore import QThread, pyqtSignal, QRunnable

from common import logger
from common.config import l4d2Config, vpkConfig
from common.module.modules import TableModel
from common.read_vpk import read_addons_txt, remove_slash
from common.conf import DATA, MAP_KEY, IS_DEV, ModType, VERSION
from packaging import version


class PrePareDataThread(QThread):
    progressSignal = pyqtSignal(str)
    addRowSignal = pyqtSignal(dict)

    def __init__(self, mode: TableModel, folder_path: Path):
        super().__init__()
        self.mode = mode
        self.folder_path = folder_path

    def run(self):
        for index, data in enumerate(self.read_data()):
            file_path = data.get('filePath')
            file_name = file_path.stem
            self.progressSignal.emit(file_name)
            self.addRowSignal.emit(data)

    def read_data(self):
        file_data = self.folder_path.iterdir()
        for file_path in file_data:
            if file_path.is_file() and file_path.suffix == '.vpk':
                res_data = read_addons_txt(file_path, True)
                yield_data = {
                    'filePath': file_path
                }
                if res_data.get('cache'):
                    yield_data.update(res_data)
                    yield yield_data
                    continue
                res = res_data.pop('type')
                if res:
                    handle_data = self.vdf_handle_data(res_data.get('content'), file_path)
                    res_data.update(handle_data)
                    res_data = self.check_type(res_data.pop('file_list'), res_data, file_path)
                elif res is False:
                    logger.error(file_path)
                    continue
                elif res is None:
                    pass
                else:
                    pass
                yield_data.update(res_data)
                if yield_data.get('father_type') == '其他':
                    # 类型为other时,先根据地图的两个字段来判断地图,
                    #              不是再根据文件名称和文件标题来判断一下类型
                    # 地图 根据addons字段内容来
                    for key in MAP_KEY:
                        value = yield_data.get(key)
                        if value and value == '1':
                            yield_data['father_type'] = '地图'
                            break
                logger.debug(f'解析类别后返回数据:{yield_data}')
                data: dict = yield_data.copy()
                del data['filePath']
                data['cache'] = True
                vpkConfig.update_config(file_path.stem, data)
                yield yield_data

    def vdf_handle_data(self, text, file_path):
        try:
            res = vdf.loads(text)
            key = None
            for i in res.keys():
                if i.lower() == 'addoninfo':
                    key = i
                    break
            if key is None:
                raise SyntaxError(f'不存在addoninfo字段，字段有{res.keys()}')
            res = res.get(key)
            res = {key.lower(): value for key, value in res.items()}
        except SyntaxError as e:
            logger.warning(f'文件 {file_path} 解析失败，开始手动解析, 错误信息{e}')
            res = self.hand_movement_data(text)
        except Exception as e:
            logger.error(f'文件{file_path} ===》出现其他错误：{e}')
            return {}
        return res

    def hand_movement_data(self, text):
        res = text.splitlines()
        res = list(filter(None, res))
        data = deepcopy(DATA)
        find_key = ''
        yield_data = {}
        for i in res:
            if find_key in data:
                data.remove(find_key)
            i = i.strip().lstrip('\t')
            temp = re.split(r'\s+', i, maxsplit=1)
            if i == '{' or i == '"AddonInfo"' or i == '}' or i == '':
                continue
            if temp[-1] == "''" or temp[-1] == '""':
                continue
            if len(temp) == 1:
                continue
            key, value = temp[0].lower(), temp[1]
            for j in data:
                if j in key:
                    if 'addondescription_fr' in key:
                        continue
                    key = self.strip_quotes(key)
                    if key in DATA:
                        value = remove_slash(value)
                        yield_data[key] = self.strip_quotes(value)
                    find_key = key
                    break
        del data, find_key
        return yield_data

    def check_type(self, vpk_path_list, return_data, path: Path):
        # 是否需要跳过
        # 是否判断了类型
        had_type = False
        goods = ModType.weapons_goods()
        file_path_dict = {}
        need_continue = False
        for filepath in vpk_path_list:
            # if (filepath.startswith('maps/') or filepath.startswith('missions/')
            # or re.findall('materials/.*?/maps/.*', filepath)):
            if filepath.startswith('maps/') or filepath.startswith('missions/'):
                return_data['father_type'] = '地图'
                return_data['child_type'] = ''
                had_type = True
        for key in MAP_KEY:
            value = return_data.get(key)
            if value and value == '1':
                return_data['father_type'] = '地图'
                return_data['child_type'] = ''
                had_type = True
                break

        for filepath in vpk_path_list:
            filepath: str
            if had_type:
                break
            if filepath.startswith('materials/skybox') and Path(filepath).stem.startswith('sky_'):
                return_data['child_type'] = '天空盒'
                return_data['father_type'] = '杂项'
                need_continue = True
            if need_continue:
                had_type = True
                file_path_dict = {}
                continue
            if self._check_file_name(filepath, 'mdl'):
                file_path_dict.setdefault('mdl', [])
                file_path_dict['mdl'].append(filepath)
            elif self._check_file_name(filepath, 'vtf'):
                file_path_dict.setdefault('vtf', [])
                file_path_dict['vtf'].append(filepath)
            elif self._check_file_name(filepath, 'vmt'):
                file_path_dict.setdefault('vmt', [])
                file_path_dict['vmt'].append(filepath)
            if not any([filepath.startswith('map'), filepath.endswith('.vtx'),
                        filepath.endswith('.vvd'), filepath.endswith('.phy'), filepath.endswith('.jpg')]):
                file_path_dict.setdefault('path', [])

                file_path_dict['path'].append(filepath)
        if not had_type:
            # 特感
            update = self._check_infected(file_path_dict, path.stem)
            if update:
                return_data.update(update)
                had_type = True
        if not had_type:
            # 角色
            return_data, had_type = self._check_survivors(file_path_dict, return_data)
        if not had_type:
            return_data, had_type = self._check_weapon(file_path_dict, goods, return_data)
        if not had_type:
            return_data["father_type"] = '其他'
            return_data['child_type'] = ''
        vpkConfig.change_file_config(path.stem, return_data)
        return return_data

    @staticmethod
    def _check_survivors(file_path_dict: dict, return_data):
        mdl_path = file_path_dict.get('mdl', [])
        survivors_dict = ModType.SURVIVORS.data()
        for mdl in mdl_path:
            result = re.findall(r'models/survivors/survivor_(.+)\.mdl', mdl)
            if result:
                for key, survivor in survivors_dict.items():
                    if key == '语音':
                        continue
                    if result[0] == survivor:
                        return_data.update({'child_type': key, 'father_type': ModType.SURVIVORS.value})
                        return return_data, True
        path = file_path_dict.get('path', [])
        for path in path:
            if re.findall(
                    r'^sound/player/survivor/voice/(?:coach|gambler|mechanic|producer|biker|teengirl|namvet|manager).*?\.wav$',
                    path):
                return_data.update({'child_type': '语音', 'father_type': ModType.SURVIVORS.value})
                return return_data, True
        return return_data, False

    @staticmethod
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

    @staticmethod
    def _check_weapon(file_path_dict: dict, goods: dict, return_data) -> tuple:
        """
        检查其他类型
        :param file_path_dict: vpk文件数据
        :param goods: 分类信息(排除人物 特感)
        :param return_data: 返回数据 检查出类型后,需要update进去,
        :return: return_data, True/False
        """
        def return_info(child_type, father_type):
            return_data.update({'child_type': child_type, 'father_type': father_type})
            return return_data, True

        def check_mdl_vmt_vtf(file_path, data_list: list):
            if not data_list:
                return False
            if Path(file_path).stem in data_list:
                return True
            return False

        def check_path(file_path: Union[List[str], str], need_path: List[str], regex=False):
            """

            :param file_path: 结构数据 即 文件路径 要么是列表要么是文本
            :param need_path: 需要匹配的文件路径
            :param regex: 是否是正则 True 则正则匹配路径 否则判断是否以路径开头
            :return:
            """
            if not need_path:
                return False
            for need in need_path:
                if isinstance(file_path, list):
                    for file in file_path:
                        if regex:
                            if re.findall(need, file):
                                return True
                        if file.startswith(need):
                            return True
                else:
                    if regex:
                        if re.findall(need, file_path):
                            return True
                    if file_path.startswith(need):
                        return True
            return False

        def check_type(data_list, file_suffix, regex: List[str] = None):
            if not data_list:
                return False
            for data in data_list:
                # data 文件列表
                for k, v in goods.items():
                    v: dict
                    if k == '语音':
                        continue
                    if k in ['武器', '近战', '医疗品', '投掷'] and not re.findall(
                            r'^(?:materials/)?models/.*?(?=[vw]_models|weapons).*$', data):
                        # r'^(?:materials/)?models(?:/[vw]_models)?.*$'
                        continue

                    if regex:
                        if not check_path(data, regex, True):
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
        res = check_type(file_path_dict.get('mdl', []), 'mdl', file_path_dict.get('mdl_path_regex'))
        if res:
            return res
        # 检查vmt
        res = check_type(file_path_dict.get('vmt', []), 'vmt', file_path_dict.get('vmt_path_regex'))
        if res:
            return res
        # 检查vtf文件
        res = check_type(file_path_dict.get('vtf', []), 'vtf', file_path_dict.get('vtf_path_regex'))
        if res:
            return res
        # 目录
        filepath_list: list = file_path_dict.get('path', [])
        for father, child in goods.items():
            child: dict
            if child.get('no_child'):
                if check_path(filepath_list, child.get('path'), child.get('regex', False)):
                    return return_info('', father)
                continue
            for chile_key, chile_value in child.items():
                if check_path(filepath_list, chile_value.get('path', []), chile_value.get('regex', False)):
                    return return_info(chile_key, father)
        return return_data, False

    @staticmethod
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
                if re.findall(regex, file):
                    return {'child_type': '语音', 'father_type': ModType.INFECTED.value}
        if not folder_list:
            return {}
        if len(folder_list) > 1:
            return {'child_type': '多种特感', 'father_type': ModType.INFECTED.value}
        else:
            for i in infected.keys():
                if folder_list[0] == infected[i]['folder']:
                    return {'child_type': i, 'father_type': ModType.INFECTED.value}

    @staticmethod
    def strip_quotes(data: str):
        return data.strip().strip("\"'")


class OpenGCFScape(QRunnable):
    def __init__(self):
        super().__init__()
        self.exe = l4d2Config.gcfspace_path.__str__()
        self.vpk_file = None

    def run(self):
        cmd = f'{self.exe} "{self.vpk_file}"'
        os.popen(cmd)
        self.vpk_file = None

    def set_vpk_file(self, vpk_file):
        self.vpk_file = vpk_file


class CheckVersion(QThread):
    resultSignal = pyqtSignal(dict)

    def run(self):
        res = self.sendRequest()
        self.resultSignal.emit(res)

    @staticmethod
    def sendRequest():
        url = 'https://fdklgbh.github.io/L4D2-Mod-Manager/update_version.json'
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            res = requests.get(url, verify=False, timeout=3)
        except Exception:
            return {
                'status': False,
                'msg': '请求失败或者超时,请检查网络状态!'
            }
        if res.status_code != 200:
            return {
                'status': False,
                'msg': res.status_code
            }
        else:
            logger.info(f'返回数据 ===> {res.json()}')
            return_data = {
                'status': True
            }
            json_data = res.json()
            is_dev = IS_DEV
            local_version = version.parse(VERSION.split(' ')[0])
            remote_version = version.parse(json_data['version'])
            update = False
            if local_version < remote_version:
                update = True
                return_data['url'] = json_data['package']
                return_data['version'] = json_data['version']
            elif local_version == remote_version:
                if is_dev:
                    update = True
                    return_data['url'] = json_data['package']
                    return_data['version'] = json_data['version']
            return_data['update'] = update
            logger.info('return_data %s', return_data)
            return return_data


__all__ = ['PrePareDataThread', 'OpenGCFScape', 'CheckVersion']
