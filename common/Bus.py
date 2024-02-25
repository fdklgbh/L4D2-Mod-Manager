# -*- coding: utf-8 -*-
# @Time: 2023/12/26
# @Author: Administrator
# @File: Bus.py
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QTableWidgetItem
from pathlib import WindowsPath


class SignalBus(QObject):
    tableItemChanged = pyqtSignal(str, str)
    windowSizeChanged = pyqtSignal(QResizeEvent)
    # 移动文件
    modulePathChanged = pyqtSignal(WindowsPath, list, dict)

    fileTypeChanged = pyqtSignal(list, str, str)


signalBus = SignalBus()

__all__ = ['signalBus']
