# -*- coding: utf-8 -*-
# @Time: 2024/12/26
# @Author: Administrator
# @File: handle_addon_info.py
import re

import vdf

from common import logger
from common.conf import DATA
from common.read_vpk import remove_slash

__all__ = ['HandleAddonInfo']
class HandleAddonInfo:

    def run(self, text, file_path):
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
            res = self._hand_movement_data(text)
        except Exception as e:
            logger.error(f'文件{file_path} ===》出现其他错误：{e}')
            return {}
        return res

    @staticmethod
    def _strip_quotes(data: str):
        return data.strip().strip("\"'")

    def _hand_movement_data(self, text):
        res = text.splitlines()
        res = list(filter(None, res))
        data = DATA[:]
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
                    key = self._strip_quotes(key)
                    if key in DATA:
                        value = remove_slash(value)
                        yield_data[key] = self._strip_quotes(value)
                    find_key = key
                    break
        del data, find_key
        return yield_data
