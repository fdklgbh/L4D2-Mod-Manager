# -*- coding: utf-8 -*-
# @Time: 2025/12/27
# @Author: Administrator
# @File: signal.py
from pathlib import Path

from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    resizeSignal = Signal()
    modMoveSignal = Signal(Path)  # 参数为目标目录路径, 用于通知对应目录刷新
    loggerSignal = Signal(str)


signalBus = SignalBus()

__all__ = ["signalBus"]
