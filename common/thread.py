# -*- coding: utf-8 -*-
# @Time: 2023/12/31
# @Author: Administrator
# @File: thread.py
import os
import re
from copy import deepcopy
from pathlib import Path

import requests
import urllib3
import vdf
from PyQt5.QtCore import QThread, pyqtSignal, QRunnable

from common import logger
from common.config import l4d2Config, vpkConfig
from common.module.modules import TableModel
from common.read_vpk import read_addons_txt, remove_slash
from common.conf import DATA, MAP_KEY, VERSION
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
                    handle_data = self.vdf_handle_data(res_data.pop('content'), file_path)
                    yield_data.update(handle_data)
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
        os.system(cmd)
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
            is_dev = 'dev' in VERSION
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
