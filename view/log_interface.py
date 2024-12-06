# -*- coding: utf-8 -*-
# @Time: 2024/11/13
# @Author: Administrator
# @File: log_interface.py
from qfluentwidgets import ScrollArea, PlainTextEdit
from PyQt5.QtWidgets import QVBoxLayout

from common.Bus import signalBus


class LogInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('LogInterface')
        layout = QVBoxLayout(self)
        self.textEdit = PlainTextEdit(self)
        self.textEdit.setReadOnly(True)
        signalBus.loggerSignal.connect(self.onLog)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)

    def onLog(self, msg):
        self.textEdit.appendPlainText(msg)
        cursor = self.textEdit.textCursor()
        self.textEdit.moveCursor(cursor.End)
