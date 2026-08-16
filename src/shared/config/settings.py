# -*- coding: utf-8 -*-
# @Time: 2025/12/19
# @Author: Administrator
# @File: settings.py
from qfluentwidgets_pro import QConfig, ConfigItem, BoolValidator, qconfig

from .validators import *
from ..app import appConstants


class Config(QConfig):
    l4d2_Path = ConfigItem("L4D2", "game_path", "", GamePathValidator())

    disable_mod_path = ConfigItem("L4D2", "disable_mod_path", "", FolderValidator(True))

    gcfspace_path = ConfigItem(
        "L4D2", "gcfspace_path", "", GCFApplicationPathValidator()
    )

    auto_update = ConfigItem("update", "autoUpdate", False, BoolValidator())


json_path = appConstants.configFolder / "config.json"

setting_cfg = Config()
qconfig.load(file=json_path, config=setting_cfg)

__all__ = ["setting_cfg"]
