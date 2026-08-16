# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: constants.py
import sys
from functools import lru_cache
from pathlib import Path
from typing import Final


class AppConstants:
    VERSION: Final = "2.0.0"
    AUTHOR: Final = "fdklgbh"
    YEAR: Final = 2024

    @property
    @lru_cache()
    def DEBUG(self):
        if hasattr(sys, "frozen") or globals().get("__compiled__"):
            return False
        return True

    @property
    @lru_cache()
    def workSpace(self):
        return Path(__file__).absolute().parent.parent

    @property
    @lru_cache()
    def dataFolder(self):
        folder_name = self._data_folder_name(self.DEBUG)
        user_folder = Path.home() / ".config" / folder_name
        program_folder = self._program_folder() / folder_name
        return self._select_data_folder(user_folder, program_folder)

    @staticmethod
    def _data_folder_name(debug: bool) -> str:
        return f"l4d2ModManager{'-dev' if debug else ''}"

    def _program_folder(self) -> Path:
        if self.DEBUG:
            return self.workSpace.parent
        return Path(sys.executable).resolve().parent

    @staticmethod
    def _select_data_folder(user_folder: Path, program_folder: Path) -> Path:
        for folder in (user_folder, program_folder):
            if (folder / "config" / "config.json").is_file():
                return folder
        return user_folder

    @property
    @lru_cache()
    def configFolder(self):
        return self.__mkdir(self.dataFolder / "config")

    @staticmethod
    def __mkdir(path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    @lru_cache()
    def cachePath(self):
        return self.__mkdir(self.dataFolder / "Cache")

    @property
    @lru_cache()
    def LogPath(self):
        return self.__mkdir(self.dataFolder / "log")

    @property
    @lru_cache()
    def tempPath(self):
        return self.__mkdir(self.workSpace / "temp")

    @property
    @lru_cache()
    def dbUrl(self):
        filename = f"L4d2ModManager{'-dev' if self.DEBUG else ''}.db"
        return f"sqlite:///{self.configFolder / filename}?charset=utf8"

    @property
    @lru_cache()
    def windowsTitle(self):
        return f"L4D2 Mod管理器 {self.VERSION}{' dev' if self.DEBUG else ''}"

    @property
    def modKey(self):
        return [
            "addontitle",
            "addonauthor",
            "addondescription",
            "addonversion",
            "addoncontent_campaign",
            "addonsteamappid",
            "addontagline",
            "addonauthorsteamid",
            "addonsteamgroupname",
            "addonurl0",
            "addoncontent_survival",
            "addoncontent_versus",
            "addoncontent_scavenge",
            "addoncontent_prefab",
            "addoncontent_spray",
            "addoncontent_backgroundmovie",
            "content_weapon",
            "content_weaponmodel",
            "addondescription_locale",
            "addoncontent_map",
            "addoncontent_skin",
            "addoncontent_weapon",
            "addoncontent_bossinfected",
            "addoncontent_commoninfected",
            "addoncontent_survivor",
            "addoncontent_sound",
            "addoncontent_music",
            "addoncontent_script",
            "addoncontent_prop",
        ]

    @property
    def mapKey(self):
        return ["addoncontent_campaign", "addoncontent_map"]

    @property
    def showDataKey(self):
        return ["addontitle", "addonauthor", "addondescription", "addontagline"]


appConstants = AppConstants()

__all__ = ["appConstants"]
