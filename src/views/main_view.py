# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: main_view.py
from qfluentPackage.windows import CFluentWindow
from core import appConstants

class MainWindow(CFluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

    def initNavigation(self):
        pass

    def connectSignalToSlot(self):
        pass

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setMinimumHeight(580)
        self.setWindowTitle(appConstants.windowsTitle)
        super(MainWindow, self).initWindow()

