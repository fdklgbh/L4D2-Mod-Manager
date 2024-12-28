# -*- coding: utf-8 -*-
# @Time: 2024/2/24
# @Author: Administrator
# @File: myIcon.py


from enum import Enum

from qfluentwidgets import getIconColor, Theme, FluentIconBase


class MyIcon(FluentIconBase, Enum):
    """ Custom icons """

    M = 'm'
    GCF = 'gcf'
    L4D2 = 'l4d2'
    refresh = 'refresh'

    def path(self, theme=Theme.AUTO):
        # getIconColor() 根据主题返回字符串 "white" 或者 "black"
        # return f':/icons/{self.value}_{getIconColor(theme)}'
        return f':/icons/{self.value}'


__all__ = ['MyIcon']
