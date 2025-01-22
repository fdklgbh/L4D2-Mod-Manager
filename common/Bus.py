# -*- coding: utf-8 -*-
# @Time: 2023/12/26
# @Author: Administrator
# @File: Bus.py
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QResizeEvent, QKeyEvent
from pathlib import WindowsPath


class SignalBus(QObject):
    tableItemChanged = pyqtSignal(str, str)
    windowSizeChanged = pyqtSignal(QResizeEvent)
    # 移动文件
    modulePathChanged = pyqtSignal(WindowsPath, list, dict)
    #                       data, fatherType, childType, oldFatherType, oldChildType
    fileTypeChanged = pyqtSignal(list, str, str, str, str)

    pressKey = pyqtSignal(QKeyEvent)

    loggerSignal = pyqtSignal(str)
    #                       fileName newName
    vpkNameChanged = pyqtSignal(str, str)
    refreshChangedSignal = pyqtSignal(set, set, set)
    reWriteLogSignal = pyqtSignal(str)
    reWriteResultSignal = pyqtSignal(WindowsPath, str, str)
    switchToByObjectNameSignal = pyqtSignal(str)  # ObjectName名称


signalBus = SignalBus()

__all__ = ['signalBus']
