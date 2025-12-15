# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: mod_show_tableview.py
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, QModelIndex
from qfluentwidgets import TableView


class ModShowTableView(TableView):
    openFolderSignal = pyqtSignal(str)
    openGCFSpaceSignal = pyqtSignal(str)
    modeEnableSignal = pyqtSignal(Path, int, str)
    doubleClickedSignal = pyqtSignal(QModelIndex)
    refreshCacheSignal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
