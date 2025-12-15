# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: constants.py
import sys
from functools import lru_cache
from pathlib import Path


class AppConstants:
    version = '2.0.0'

    @property
    @lru_cache()
    def DEBUG(self):
        if hasattr(sys, 'frozen'):
            return False
        return True

    @property
    @lru_cache()
    def workSpace(self):
        return Path(__file__).absolute().parent.parent

    @property
    @lru_cache()
    def dataFolder(self):
        return self.__mkdir(Path.home() / '.l4d2ModManager')

    @property
    @lru_cache()
    def CONFIG(self):
        return self.__mkdir(self.dataFolder / 'config')

    @staticmethod
    def __mkdir(path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    @lru_cache()
    def cachePath(self):
        return self.__mkdir(self.dataFolder / 'Cache')

    @property
    @lru_cache()
    def LogPath(self):
        return self.__mkdir(self.dataFolder / 'log')

    @property
    @lru_cache()
    def tempPath(self):
        return self.__mkdir(self.workSpace / 'temp')

    @property
    @lru_cache()
    def dbUrl(self):
        return f'sqlite:///{self.CONFIG / "L4d2ModManager.db"}?charset=utf8'

    @property
    @lru_cache()
    def windowsTitle(self):
        return f'L4D2 Mod管理器 {self.version}{" dev" if self.DEBUG else ""}'


appConstants = AppConstants()

__all__ = ['appConstants']

if __name__ == '__main__':
    print(appConstants.DEBUG)
