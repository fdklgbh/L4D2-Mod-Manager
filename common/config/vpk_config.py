# -*- coding: utf-8 -*-
# @Time: 2024/2/19
# @Author: Administrator
# @File: vpk_config.py

from PyQt5.QtCore import QMutex, QMutexLocker
from common.conf import CachePath
from common.crypto import md5, encrypt_data, decrypt_data

mutex = QMutex()
cache_path = CachePath
cache_path.mkdir(exist_ok=True)


class VPKConfig:
    def get_file_config(self, file_name):
        return self._read(file_name)

    def change_file_config(self, file_name, new_config: dict):
        self._save(file_name, new_config)

    def change_file_single_config(self, file_name, key, value):
        data = self._read(file_name)
        data[key] = value
        self._save(file_name, data)

    def update_config(self, file_name, new_config, pop_key: list = None):
        data = self._read(file_name)
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
