# -*- coding: utf-8 -*-
# @Time: 2024/2/12
# @Author: Administrator
# @File: setting_interface.py
from pathlib import Path

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QLabel, QWidget, QFileDialog
from qfluentwidgets import ScrollArea, SettingCardGroup, ExpandLayout, PushSettingCard, MessageBox, HyperlinkCard, \
    SwitchSettingCard
from qfluentwidgets import FluentIcon as FIF

from common.check_version import show_version_dialog
from common.conf import VERSION, YEAR, AUTHOR, CachePath
from common.config import l4d2Config
from common.config.setting_config import setting_cfg
from common.crypto import md5
from common.style_sheet import StyleSheet
from common.thread import CheckVersion
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

        self.cacheGroup = SettingCardGroup(
            "缓存", self.scrollWidget
        )
        self.cleanCacheCard = PushSettingCard(
            '清理', FIF.BROOM, '清理缓存', '清除已删除vpk的缓存文件', self.cacheGroup
        )

        self.updateGroup = SettingCardGroup(
            '更新', self.scrollWidget
        )
        self.autoUpdateCard = SwitchSettingCard(
            FIF.SYNC, '启动检查', '启动程序检查更新',
            configItem=setting_cfg.auto_update,
            parent=self.updateGroup
        )

        self.checkUpdateCard = PushSettingCard(
            '检查更新', FIF.UPDATE, '检查更新', '', self.updateGroup
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
            '© ' + f"版权所有 {YEAR}, {AUTHOR}. 当前版本 {VERSION}",
            self.aboutGroup
        )
        self.aboutCard.linkButton.setIcon(FIF.GITHUB)

        self.__initWidgets()

    def __initLayout(self):
        self.settingLabel.move(36, 30)
        self.pathGroup.addSettingCards(
            [self.gamePathCard, self.disableModeCard, self.gcfPathCard]
        )
        self.cacheGroup.addSettingCards(
            [self.cleanCacheCard]
        )

        self.updateGroup.addSettingCards(
            [self.autoUpdateCard, self.checkUpdateCard]
        )

        self.aboutGroup.addSettingCards(
            [self.feedbackCard, self.aboutCard]
        )

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.pathGroup)
        self.expandLayout.addWidget(self.cacheGroup)
        self.expandLayout.addWidget(self.updateGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __connectSignalToSlot(self):
        self.gamePathCard.clicked.connect(lambda: self.open_folder(l4d2Config.l4d2_path))
        self.disableModeCard.clicked.connect(lambda: self.open_folder(l4d2Config.disable_mod_path))
        self.gcfPathCard.clicked.connect(self.choice_exe)
        self.cleanCacheCard.clicked.connect(self.cleanVPKCache)
        self.autoUpdateCard.checkedChanged.connect(l4d2Config.set_auto_update)
        self.checkUpdateCard.clicked.connect(self.checkUpdate)

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
                w = MessageBox('程序选择错误', '是否重选', self.window())
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

    def cleanVPKCache(self):
        """
        删除不存在的vpk文件缓存
        :return:
        """
        md5_titles = set()
        for path in [l4d2Config.addons_path, l4d2Config.workshop_path, l4d2Config.disable_mod_path]:
            for i in path.glob('*.vpk'):
                if i.is_file():
                    stem = md5(i.stem)
                    if stem not in md5_titles:
                        md5_titles.add(stem)
        cache_set = set(i.stem for i in CachePath.glob('*.cache') if i.is_file())
        for i in cache_set - md5_titles:
            file = CachePath / f'{i}.cache'
            if file.exists():
                file.unlink()

    def checkUpdate(self):
        thread = CheckVersion()
        thread.resultSignal.connect(self.showDialog)
        thread.start()
        thread.wait()

    def showDialog(self, data: dict):
        show_version_dialog(data, self)
