# -*- coding: utf-8 -*-
# @Time: 2024/2/19
# @Author: Administrator
# @File: vpk_config.py

from pathlib import Path
from json import load, dump
from copy import deepcopy
from common import logger
from PyQt5.QtCore import QMutex, QMutexLocker

from common.crypto import md5, encrypt_data, decrypt_data

mutex = QMutex()
cache_path = Path('Cache')
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
            # with open(path, 'w', encoding='utf8') as f_:
            #     dump(data, f_, ensure_ascii=False, indent=4)

    @staticmethod
    def _read(filename):
        filename = md5(filename)
        path = cache_path / f"{filename}.cache"
        if not path.exists():
            return {}
        with QMutexLocker(mutex):
            return decrypt_data(path)
            # with open(cache_path / f"{filename}.json", 'r', encoding='utf8') as f_json:
            #     data = load(f_json)
            #     return data


__all__ = ['VPKConfig']
