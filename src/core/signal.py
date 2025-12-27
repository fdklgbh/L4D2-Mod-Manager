# -*- coding: utf-8 -*-
# @Time: 2025/12/27
# @Author: Administrator
# @File: signal.py
from PySide6.QtCore import QObject, Signal


class SignalBus(QObject):
    resizeSignal = Signal()
    modMoveSignal = Signal()
    loggerSignal = Signal(str)


signalBus = SignalBus()

__all__ = ["signalBus"]
