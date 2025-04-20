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
        # todo 加速地址改为可配置,后续自动下载包
        url = 'https://www.ghproxy.cn/https://raw.githubusercontent.com/fdklgbh/L4D2-Mod-Manager/refs/heads/master/docs/update_version.json'
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            res = requests.get(url, verify=False, timeout=5)
        except Exception:
            return {
                'status': False,
                'msg': '请求失败或者超时,请检查网络状态!'
            }
        else:
            try:
                logger.info(f'请求返回信息:{res.text}')
            except Exception as e:
                logger.warn(f'输出日志失败:{e}')
        if res.status_code != 200:
            try:
                logger.warning(f'返回数据 ===> {res.text}')
            except Exception as e:
                logger.error(f'返回数据文本输出错误,{e}')
            return {
                'status': False,
                'msg': '响应码: ' + str(res.status_code) + ',具体信息看日志'
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
