# -*- coding: utf-8 -*-
# @Time: 2024/2/24
# @Author: Administrator
# @File: myIcon.py


from enum import Enum

from qfluentwidgets_pro import Theme, FluentIconBase


class Icon(FluentIconBase, Enum):
    """自定义图标。"""

    M = "m"
    GCF = "gcf"
    L4D2 = "l4d2"
    refresh = "refresh"
    switch = "switch"
    trash = "trash"
    add = "add"
    edit = "edit"

    def path(self, theme=Theme.AUTO):
        return f":/icons/{self.value}"


__all__ = ["Icon"]
