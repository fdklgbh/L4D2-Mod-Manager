# -*- coding: utf-8 -*-
# @Time: 2025/12/19
# @Author: Administrator
# @File: l4d2cfg.py
import platform
from pathlib import Path

from qfluentwidgets import ConfigItem

from .settings import setting_cfg
from functools import lru_cache


class L4d2Config:
    @property
    def l4d2_path(self):
        return self._path(setting_cfg.l4d2_Path)

    @l4d2_path.setter
    def l4d2_path(self, value):
        setting_cfg.set(setting_cfg.l4d2_Path, value)

    @property
    def disable_mod_path(self):
        return self._path(setting_cfg.disable_mod_path)

    @disable_mod_path.setter
    def disable_mod_path(self, value):
        Path(value).mkdir(exist_ok=True)
        setting_cfg.set(setting_cfg.disable_mod_path, value)

    @property
    def l4d2_vpk_path(self):
        name = "vpk.exe" if self.is_win else "vpk"
        return Path(self.l4d2_path) / "bin" / name

    @property
    def vpk_application_is_exists(self):
        return self.l4d2_vpk_path.exists()

    @property
    def auto_update(self):
        return setting_cfg.auto_update.value

    @property
    def auto_update_item(self) -> ConfigItem:
        return setting_cfg.auto_update

    @auto_update.setter
    def auto_update(self, value):
        setting_cfg.set(setting_cfg.auto_update, value)

    @property
    def gcfspace_path(self):
        return self._path(setting_cfg.gcfspace_path)

    @gcfspace_path.setter
    def gcfspace_path(self, value):
        setting_cfg.set(setting_cfg.gcfspace_path, value)

    @property
    def addons_path(self):
        return (self.l4d2_path / "left4dead2" / "addons").resolve()

    @property
    def workshop_path(self):
        return (self.addons_path / "workshop").resolve()

    def is_addons(self, path):
        return self.addons_path == Path(path).resolve()

    def is_workshop(self, path):
        return self.workshop_path == Path(path).resolve()

    def is_disable_mod_path(self, path):
        return self.disable_mod_path == Path(path).resolve()

    @staticmethod
    def _path(item):
        if value := setting_cfg.get(item):
            return Path(value).resolve()
        return ""

    @property
    def addonlist_file(self):
        return self.l4d2_path / "left4dead2" / "addonlist.txt"

    @property
    @lru_cache()
    def is_win(self):
        return platform.system() == "Windows"


l4d2Config = L4d2Config()

__all__ = ["l4d2Config"]
