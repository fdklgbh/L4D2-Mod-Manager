# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: main_view.py
from PySide6.QtGui import QIcon
from qfluentPackage.windows import CFluentWindow
from qfluentwidgets import NavigationItemPosition, FluentIcon as FIF

from features.logs.page import LogView
from features.mod_browser.page import ModShowView
from features.settings.page import SettingView
from shared.app import appConstants
from shared.config import l4d2Config
from shared.persistence import dispose
from shared.runtime import LogBase, signalBus
from shared.ui import Icon


class MainWindow(CFluentWindow, LogBase):
    TAG = "MainWindow"

    def __init__(self):
        super().__init__()
        self.initWindow()
        self.setWindowIcon(QIcon(Icon.L4D2.path()))
        self.settings_view = SettingView(self)
        self.log_view = LogView(self)
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
            self.log_view,
            FIF.FILTER,
            self.tr("日志"),
            NavigationItemPosition.BOTTOM,
        )
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

    def resizeEvent(self, e):
        signalBus.resizeSignal.emit()
        super().resizeEvent(e)
