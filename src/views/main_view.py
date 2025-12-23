# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: main_view.py
from qfluentPackage.windows import CFluentWindow
from qfluentwidgets import NavigationItemPosition, FluentIcon as FIF

from core import appConstants, l4d2Config, Icon, LogBase, dispose
from views import SettingView, ModShowView


class MainWindow(CFluentWindow, LogBase):
    TAG = "MainWindow"

    def __init__(self):
        super().__init__()
        self.initWindow()
        self.settings_view = SettingView(self)
        self.mod_view = ModShowView(
            [
                l4d2Config.addons_path,
                l4d2Config.workshop_path,
                l4d2Config.disable_mod_path,
            ],
            self,
        )
        self.initNavigation()
        self.connectSignalToSlot()
        self.logger.info("MainWindow success")

    def initNavigation(self):
        self.addSubInterface(self.mod_view, Icon.M, self.tr("Mod"))
        self.addSubInterface(
            self.settings_view,
            FIF.SETTING,
            self.tr("设置"),
            NavigationItemPosition.BOTTOM,
        )

    def connectSignalToSlot(self):
        pass

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setMinimumHeight(580)
        self.setWindowTitle(appConstants.windowsTitle)
        super(MainWindow, self).initWindow()

    def closeEvent(self, a0):
        dispose()
        self.logger.info("数据库断开链接")
        super().closeEvent(a0)
