# -*- coding: utf-8 -*-
# @Time: 2024/2/19
# @Author: Administrator
# @File: setting_config.py
from qfluentwidgets import ConfigItem

from common.validator import GamePathValidator, FolderValidator, GCFApplicationPathValidator
from qfluentPackage.common.CQConfig import CustomConfig


class Config(CustomConfig):
    l4d2_Path = ConfigItem(
        'L4D2', 'game_path', '', GamePathValidator()
    )

    disable_mod_path = ConfigItem(
        'L4D2', 'disable_mod_path', '', FolderValidator(True)
    )

    gcfspace_path = ConfigItem(
        'L4D2', 'gcfspace_path', '', GCFApplicationPathValidator()
    )


json_path = 'config/l4d2_config.json'
setting_cfg = Config(json_path)
setting_cfg.load(config=setting_cfg)

__all__ = ['setting_cfg']