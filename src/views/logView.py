# -*- coding: utf-8 -*-
# @Time: 2025/12/27
# @Author: Administrator
# @File: logView.py
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import ScrollArea, PlainTextEdit

from shared.runtime import signalBus


class LogView(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LogInterface")
        layout = QVBoxLayout(self)
        self.textEdit = PlainTextEdit(self)
        self.textEdit.setReadOnly(True)
        signalBus.loggerSignal.connect(self.onLog)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)

    def onLog(self, msg: str):
        self.textEdit.appendPlainText(msg.strip())
        cursor = self.textEdit.textCursor()
        self.textEdit.moveCursor(cursor.MoveOperation.End)


__all__ = ["LogView"]
