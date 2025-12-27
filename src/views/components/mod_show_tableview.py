# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: mod_show_tableview.py
from pathlib import Path

from PySide6.QtCore import QModelIndex, Signal
from qfluentwidgets import TableView


class ModShowTableView(TableView):
    openFolderSignal = Signal(str)
    openGCFSpaceSignal = Signal(str)
    modeEnableSignal = Signal(Path, int, str)
    doubleClickedSignal = Signal(QModelIndex)
    refreshCacheSignal = Signal(list)

    def __init__(self, parent):
        super().__init__(parent)
