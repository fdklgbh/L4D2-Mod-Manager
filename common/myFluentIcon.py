# -*- coding: utf-8 -*-
# @Time: 2024/2/13
# @Author: Administrator
# @File: myFluentIcon.py
from enum import Enum

from qfluentwidgets import FluentIconBase, Theme


class MyFluentIcon(FluentIconBase, Enum):
    GCF = 'gcf'

    def path(self, theme=Theme.AUTO) -> str:
        return f':/icons/{self}'
