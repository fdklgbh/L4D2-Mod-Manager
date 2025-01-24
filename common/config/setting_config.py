# -*- coding: utf-8 -*-
# @Time: 2024/2/19
# @Author: Administrator
# @File: setting_config.py
from qfluentwidgets import ConfigItem, BoolValidator, qconfig, QConfig

from common.conf import CONFIG
from common.validator import GamePathValidator, FolderValidator, GCFApplicationPathValidator


class Config(QConfig):
    l4d2_Path = ConfigItem(
        'L4D2', 'game_path', '', GamePathValidator()
    )

    disable_mod_path = ConfigItem(
        'L4D2', 'disable_mod_path', '', FolderValidator(True)
    )

    gcfspace_path = ConfigItem(
        'L4D2', 'gcfspace_path', '', GCFApplicationPathValidator()
    )

    auto_update = ConfigItem(
        'update', 'autoUpdate', False, BoolValidator()
    )


json_path = CONFIG / 'l4d2_config.json'

setting_cfg = Config()
qconfig.load(file=json_path, config=setting_cfg)

__all__ = ['setting_cfg']
