# -*- coding: utf-8 -*-
# @Time: 2024/2/13
# @Author: Administrator
# @File: style_sheet.py
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme


class StyleSheet(StyleSheetBase, Enum):
    SETTING_INTERFACE = "setting_interface"
    MAIN_WINDOW = "main_window"

    def path(self, theme=Theme.AUTO):
        return f':/qss/{self.value}'


__all__ = ['StyleSheet']
