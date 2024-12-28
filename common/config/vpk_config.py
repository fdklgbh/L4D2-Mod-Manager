# -*- coding: utf-8 -*-
# @Time: 2024/2/19
# @Author: Administrator
# @File: vpk_config.py
from typing import Union

from PyQt5.QtCore import QMutex, QMutexLocker
from common.conf import CachePath
from common.crypto import md5, encrypt_data, decrypt_data

mutex = QMutex()
cache_path = CachePath


class VPKConfig:
    def get_file_config(self, file_name):
        """
        获取mod 文件配置
        :param file_name:
        :return:
        """
        return self._read(file_name)

    def change_file_config(self, file_name, new_config: dict):
        """
        更新文件所有配置
        :param file_name:
        :param new_config:
        :return:
        """
        self._save(file_name, new_config)

    def change_file_single_config(self, file_name, key, value: Union[dict, str]):
        data = self._read(file_name)
        data[key] = value
        self._save(file_name, data)

    def update_config(self, file_name, new_config: dict, pop_key: list = None):
        data = self._read(file_name)
        if new_config.get('father_type') and 'check_type' in data.keys():
            data.pop('check_type', '')
        data.update(new_config)
        if pop_key:
            for key in pop_key:
                del data[key]
        self._save(file_name, data)

    @staticmethod
    def _save(filename, data):
        with QMutexLocker(mutex):
            filename = md5(filename)
            path = cache_path / f"{filename}.cache"
            encrypt_data(path, data)

    @staticmethod
    def _read(filename):
        filename = md5(filename)
        path = cache_path / f"{filename}.cache"
        if not path.exists():
            return {}
        with QMutexLocker(mutex):
            return decrypt_data(path)


__all__ = ['VPKConfig']
