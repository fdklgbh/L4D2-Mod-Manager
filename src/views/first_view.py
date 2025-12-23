# -*- coding: utf-8 -*-
# @Time: 2025/12/20
# @Author: Administrator
# @File: first_view.py
import sys
from pathlib import Path

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog

from core import GamePathValidator, l4d2Config
from views.ui import Ui_firstUse


class FirstView(QDialog, Ui_firstUse):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(420, 180)
        # self.setWindowFlags(Qt.FramelessWindowHint)  # 隐藏标题栏
        self.setStyleSheet(
            """
               FirstView {
                   background-color: white;
                   border-radius: 10px;
               }
               * {
                   border: none;
               }
           """
        )
        self.quitBtn.clicked.connect(self.reject)
        self.sureBtn.clicked.connect(self.setPath)

    def quit(self):
        print("quit")
        QApplication.instance().quit()
        self.close()
        sys.exit(0)

    def verify(self, text):
        print(text)
        sender = self.sender()
        if sender == self.gamePathEdit:
            if not text:
                self.updateStyle(False)
            else:
                self.updateStyle(not GamePathValidator().correct(text))
        self.check_sure_btn()

    def check_sure_btn(self):
        l4d2_path = self.gamePathEdit.text()
        disable_path = self.disablePathEdit.text()
        if (
            not GamePathValidator().correct(l4d2_path)
            or not Path(disable_path).is_absolute()
        ):
            self.sureBtn.setEnabled(False)
            return
        self.sureBtn.setEnabled(True)

    def updateStyle(self, error=True):
        self.gamePathEdit.setProperty("type", "error" if error else None)
        self.gamePathEdit.style().unpolish(self.gamePathEdit)
        self.gamePathEdit.style().polish(self.gamePathEdit)
        self.gamePathEdit.update()

    def setPath(self):
        l4d2Config.l4d2_path = self.gamePathEdit.text()
        l4d2Config.disable_mod_path = self.disablePathEdit.text()
        self.finished.emit()
        self.accept()
        self.close()

    def reject(self):
        print("reject")
        super().reject()
        self.quit()
