# -*- coding: utf-8 -*-
# @Time: 2024/12/21
# @Author: Administrator
# @File: check_version_thread.py
import requests
import urllib3
from PyQt5.QtCore import QThread, pyqtSignal
from packaging import version

from common import logger
from common.conf import VERSION, IS_DEV


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
            local_version = version.parse(VERSION.split(' ')[0])
            remote_version = version.parse(json_data['version'])
            update = False
            if local_version < remote_version:
                update = True
                return_data['url'] = json_data['package']
                return_data['version'] = json_data['version']
            elif local_version == remote_version:
                if IS_DEV:
                    update = True
                    return_data['url'] = json_data['package']
                    return_data['version'] = json_data['version']
            return_data['update'] = update
            logger.info('return_data %s', return_data)
            return return_data
