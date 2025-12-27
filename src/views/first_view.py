# -*- coding: utf-8 -*-
# @Time: 2025/12/20
# @Author: Administrator
# @File: first_view.py
import sys
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWidget

from core import GamePathValidator, l4d2Config, Icon
from views.ui import Ui_firstUse


class FirstView(FluentWidget, Ui_firstUse):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(Icon.L4D2.path()))
        self.setFixedSize(420, 200)
        self.quitBtn.clicked.connect(self.quit)
        self.sureBtn.clicked.connect(self.setPath)
        self.verticalLayout.setContentsMargins(10, self.titleBar.height() + 10, 10, 10)

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
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = FirstView()
    w.show()
    app.exec()
