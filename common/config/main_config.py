# -*- coding: utf-8 -*-
# @Time: 2023/12/25
# @Author: Administrator
# @File: main_config.py

from pathlib import Path
import vdf
from common.config.setting_config import setting_cfg


class L4d2Config:
    debug = False

    @property
    def l4d2_path(self):
        return self._path(setting_cfg.l4d2_Path)

    @l4d2_path.setter
    def l4d2_path(self, value):
        setting_cfg.set(setting_cfg.l4d2_Path, value)

    @property
    def disable_mod_path(self):
        return self._path(setting_cfg.disable_mod_path)

    @property
    def l4d2_vpk_path(self):
        return Path(self.l4d2_path) / 'bin' / 'vpk.exe'

    @property
    def vpk_application_is_exists(self):
        return self.l4d2_vpk_path.exists()

    @property
    def auto_update(self):
        return setting_cfg.auto_update.value

    @staticmethod
    def set_auto_update(value):
        setting_cfg.set(setting_cfg.auto_update, value)

    @disable_mod_path.setter
    def disable_mod_path(self, value):
        Path(value).mkdir(exist_ok=True)
        setting_cfg.set(setting_cfg.disable_mod_path, value)

    @property
    def gcfspace_path(self):
        return self._path(setting_cfg.gcfspace_path)

    @gcfspace_path.setter
    def gcfspace_path(self, value):
        setting_cfg.set(setting_cfg.gcfspace_path, value)

    @staticmethod
    def _path(item):
        value = setting_cfg.get(item)
        if value:
            return Path(value).resolve()
        return ''

    @property
    def addons_path(self):
        return (self.l4d2_path / 'left4dead2' / 'addons').resolve()

    @property
    def workshop_path(self):
        return (self.addons_path / 'workshop').resolve()

    def is_addons(self, path):
        if isinstance(path, Path):
            path = path.resolve()
        else:
            path = Path(path).resolve()
        return self.addons_path == path

    def is_workshop(self, path):
        if isinstance(path, Path):
            path = path.resolve()
        else:
            path = Path(path).resolve()
        return self.workshop_path == path

    def is_disable_mod_path(self, path):
        if isinstance(path, Path):
            path = path.resolve()
        else:
            path = Path(path).resolve()
        return self.disable_mod_path == path

    @property
    def addonlist_file(self):
        return self.l4d2_path / 'left4dead2' / 'addonlist.txt'

    def read_addonlist(self, used=True):
        """
        读取addonlist文件
        :param used:
        :return:
        """
        if not (self.addonlist_file.exists() and self.addonlist_file.exists()):
            return None
        try:
            with open(self.addonlist_file, encoding='gbk') as f:
                data = vdf.load(f)
        except UnicodeError:
            with open(self.addonlist_file, encoding='utf8') as f:
                data = vdf.load(f)
        data: dict = data.get('AddonList', {})
        result = []
        for key, value in data.items():
            key: str
            if not key.endswith('.vpk'):
                continue
            key = key.replace('.vpk', '')
            if used and value == '1':
                result.append(key)
            elif used is None:
                result.append(key)
        return result


__all__ = ['L4d2Config']

if __name__ == '__main__':
    print(L4d2Config().read_addonlist())
