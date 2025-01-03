# -*- coding: utf-8 -*-
# @Time: 2023/12/25
# @Author: Administrator
# @File: main_config.py

from pathlib import Path

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
    def vpk_application_is_exsits(self):
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


__all__ = ['L4d2Config']
