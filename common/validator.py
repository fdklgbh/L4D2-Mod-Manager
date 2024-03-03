# -*- coding: utf-8 -*-
# @Time: 2024/2/3
# @Author: Administrator
# @File: validator.py
from pathlib import Path

from qfluentwidgets import ConfigValidator
import os
from common.conf import WORKSPACE


class GamePathValidator(ConfigValidator):
    def validate(self, value):
        return Path(value).exists()

    def correct(self, value):
        path = Path(value)
        addons_path = path / 'left4dead2' / 'addons'
        if not addons_path.exists() or not (addons_path / 'workshop').exists():
            return ''
        return str(path.absolute()).replace("\\", "/")


class FolderValidator(ConfigValidator):
    """ Folder validator """
    def __init__(self, mkdir=False):
        self.mkdir = mkdir

    def validate(self, value):
        path = Path(value)
        if path == WORKSPACE:
            return False
        return Path(value).exists()

    def correct(self, value):
        if not value:
            return ''
        path = Path(value).absolute()
        if path == WORKSPACE:
            return ''
        if not path.exists():
            if self.mkdir:
                path.mkdir(exist_ok=True)
            else:
                return ''
        return str(path.absolute()).replace("\\", "/")


class ApplicationPathValidator(ConfigValidator):
    def _is_exe(self, path):
        if not isinstance(path, Path):
            path = Path(path).resolve()
        return path.exists() and path.is_file() and path.suffix == '.exe' and os.access(path, os.X_OK)

    def validate(self, value):
        if not value:
            return False
        return self._is_exe(value)

    def correct(self, value):
        if self._is_exe(value):
            return value
        return ''


class GCFApplicationPathValidator(ApplicationPathValidator):
    def _is_exe(self, path):
        if not str(path).endswith('GCFScape.exe'):
            return False
        return super()._is_exe(path)