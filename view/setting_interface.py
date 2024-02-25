# -*- coding: utf-8 -*-
# @Time: 2024/2/12
# @Author: Administrator
# @File: setting_interface.py
from pathlib import Path

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QLabel, QWidget, QFileDialog
from qfluentwidgets import ScrollArea, SettingCardGroup, ExpandLayout, PushSettingCard, MessageBox,HyperlinkCard
from qfluentwidgets import FluentIcon as FIF

from common.conf import VERSION
from common.config.main_config import l4d2Config
from common.style_sheet import StyleSheet
from common.validator import GCFApplicationPathValidator


class SettingInterface(ScrollArea):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        self.settingLabel = QLabel(self.tr("设置"), self)

        self.pathGroup = SettingCardGroup(
            '配置目录', self.scrollWidget
        )
        self.gamePathCard = PushSettingCard(
            '游戏目录', FIF.FOLDER, "L4D2目录", str(l4d2Config.l4d2_path), self.pathGroup
        )

        self.disableModeCard = PushSettingCard(
            '禁用目录', FIF.FOLDER, '禁用mod文件夹', str(l4d2Config.disable_mod_path), self.pathGroup
        )

        self.gcfPathCard = PushSettingCard(
            '选择GCFScape程序', FIF.FOLDER, "GCFScape文件", str(l4d2Config.gcfspace_path), self.pathGroup
        )

        self.aboutGroup = SettingCardGroup(self.tr('关于'), self.scrollWidget)
        self.feedbackCard = HyperlinkCard(
            'https://github.com/fdklgbh/L4D2-Mod-Manager/issues',
            self.tr('提供反馈'),
            FIF.FEEDBACK,
            self.tr('打开帮助页面'),
            self.tr('提供反馈用于改进项目'),
            self.aboutGroup
        )
        self.feedbackCard.linkButton.setIcon(FIF.LINK)
        self.aboutCard = HyperlinkCard(
            'https://github.com/fdklgbh/L4D2-Mod-Manager',
            '打开github项目', FIF.INFO,
            self.tr('About'),
            '开源项目 ' + self.tr('版本') + f" {VERSION}",
            self.aboutGroup
        )
        self.aboutCard.linkButton.setIcon(FIF.GITHUB)

        self.__initWidgets()

    def __initLayout(self):
        self.settingLabel.move(36, 30)
        self.pathGroup.addSettingCards(
            [self.gamePathCard, self.disableModeCard, self.gcfPathCard]
        )
        self.aboutGroup.addSettingCards(
            [self.feedbackCard, self.aboutCard]
        )
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.pathGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __connectSignalToSlot(self):
        self.gamePathCard.clicked.connect(lambda: self.open_folder(l4d2Config.l4d2_path))
        self.disableModeCard.clicked.connect(lambda: self.open_folder(l4d2Config.disable_mod_path))
        self.gcfPathCard.clicked.connect(self.choice_exe)

    def choice_exe(self):
        path = l4d2Config.gcfspace_path
        if path:
            path = Path(path).parent
        else:
            path = Path.home()
        exe_path, _ = QFileDialog.getOpenFileName(self, '选择GCF程序', str(path), '应用程序(*.exe)',
                                                  options=QFileDialog.ShowDirsOnly)
        if exe_path:
            if GCFApplicationPathValidator().validate(exe_path):
                l4d2Config.gcfspace_path = exe_path
                self.gcfPathCard.setContent(exe_path)
            else:
                w = MessageBox('程序选择错误', '是否重选', self.parent().parent().parent())
                w.yesButton.setText(self.tr('重选'))
                if w.exec_():
                    self.choice_exe()

    @staticmethod
    def open_folder(path):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def __initWidgets(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        # FluentStyleSheet.SETTING_CARD.apply(self)

        self.__initLayout()
        self.__connectSignalToSlot()
        StyleSheet.SETTING_INTERFACE.apply(self)
