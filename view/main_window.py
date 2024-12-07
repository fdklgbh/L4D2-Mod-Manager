# -*- coding: utf-8 -*-
# @Time: 2023/12/25
# @Author: Administrator
# @File: main_window.py
import os
from pathlib import Path

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentPackage.windows import CFluentWindow

from common import logger
from common.Bus import signalBus
from common.ExceptionHook import ExceptionHook
from common.check_version import show_version_dialog
from common.conf import WINDOWS_TITLE, VERSION
from common.config import l4d2Config
from common.myIcon import MyIcon
from common.style_sheet import StyleSheet
from common.thread import CheckVersion
from common.validator import GamePathValidator
from qfluentwidgets import (FluentIcon as FIF, MessageBoxBase, SubtitleLabel, LineEdit, NavigationItemPosition,
                            MessageBox)

from .log_interface import LogInterface
from .modules_interface_splitter import ModulesInterfaceSplitter
from .setting_interface import SettingInterface
from .update_info_interface import UpdateInfoInterface


class CustomMessageBox(MessageBoxBase):
    """ Custom message box """

    def __init__(self, l4d2_path=None, disable_path=None, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel('设置配置路径', self)
        self.l4d2_path = LineEdit(self)

        self.l4d2_path.setPlaceholderText('游戏路径')
        self.l4d2_path.setClearButtonEnabled(True)
        if l4d2_path:
            self.l4d2_path.setText(l4d2_path)
        self.disable_path = LineEdit(self)

        self.disable_path.setPlaceholderText('禁用mod路径(不存在会自动创建文件)')
        self.disable_path.setClearButtonEnabled(True)
        if disable_path:
            self.disable_path.setText(disable_path)
        # add widget to view layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.l4d2_path)
        self.viewLayout.addWidget(self.disable_path)
        # change the text of button
        self.yesButton.setText('确定')
        self.cancelButton.setText('退出')

        self.widget.setMinimumWidth(350)
        self.yesButton.setDisabled(True)
        self.l4d2_path.textChanged.connect(self._validateUrl)
        self.disable_path.textChanged.connect(self._validateUrl)

    def _validateUrl(self, text):
        l4d2_path = self.l4d2_path.text()
        disable_path = self.disable_path.text()
        if not GamePathValidator().correct(l4d2_path) or not Path(disable_path).is_absolute():
            self.yesButton.setEnabled(False)
            return
        self.yesButton.setEnabled(True)


class MainWindow(CFluentWindow, ExceptionHook):

    def __init__(self):
        CFluentWindow.__init__(self)
        ExceptionHook.__init__(self)
        screen = QApplication.primaryScreen()
        scale = screen.devicePixelRatio()
        self.check_version_thread = CheckVersion()
        self.setWindowIcon(QIcon(MyIcon.L4D2.path()))
        self.log_interface = LogInterface(self)
        logger.info(f'缩放因子:{scale}')
        self.initWindow()
        L4D2_PATH = str(l4d2Config.l4d2_path)
        if not L4D2_PATH or not l4d2Config.disable_mod_path:
            w = CustomMessageBox(L4D2_PATH, str(l4d2Config.disable_mod_path), self)
            if not w.exec_():
                self.closeEvent(None)
            else:
                l4d2Config.l4d2_path = w.l4d2_path.text()
                l4d2Config.disable_mod_path = w.disable_path.text()
        # 更新说明页面
        self.show_update_interface = UpdateInfoInterface(self)
        self.modules_interface_splitter = ModulesInterfaceSplitter(
            [l4d2Config.addons_path, l4d2Config.workshop_path, l4d2Config.disable_mod_path], self)
        self.settings_interface = SettingInterface(self)
        self.initNavigation()
        StyleSheet.MAIN_WINDOW.apply(self)
        self.connectSignalToSlot()

    def showEvent(self, event):
        if hasattr(self, 'check_version_thread'):
            if l4d2Config.auto_update:
                self.check_version_thread.resultSignal.connect(self.updateDisplay)
                self.check_version_thread.start()
            else:
                del self.check_version_thread
        super().showEvent(event)

    def closeEvent(self, a0):
        if a0:
            super().closeEvent(a0)
        os._exit(0)

    def initNavigation(self):
        self.addSubInterface(self.show_update_interface, FIF.HOME, VERSION + self.tr('更新日志'))
        self.addSubInterface(self.modules_interface_splitter, MyIcon.M, self.tr('Mod'))
        self.addSubInterface(self.log_interface, FIF.FILTER, self.tr('日志'), NavigationItemPosition.BOTTOM)
        self.addSubInterface(self.settings_interface, FIF.SETTING, self.tr('设置'), NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setMinimumHeight(580)
        self.setWindowTitle(WINDOWS_TITLE + ' ' + VERSION)
        super(MainWindow, self).initWindow()

    def connectSignalToSlot(self):
        self.exceptionSignal.connect(self.exception)

    def exception(self, msg):
        w = MessageBox('错误', msg, parent=self)
        w.cancelButton.hide()
        w.buttonLayout.insertStretch(0, 1)
        w.show()
        w.exec_()
        QApplication.quit()

    def updateDisplay(self, data: dict):
        logger.debug(f'updateDisplay: {data}')
        show_version_dialog(data, self, True)
        del self.check_version_thread

    def resizeEvent(self, e):
        signalBus.windowSizeChanged.emit(e)
        super(MainWindow, self).resizeEvent(e)

    def keyPressEvent(self, a0):
        signalBus.pressKey.emit(a0)
        super().keyPressEvent(a0)
