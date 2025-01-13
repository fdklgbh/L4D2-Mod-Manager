# -*- coding: utf-8 -*-
# @Time: 2025/1/13
# @Author: Administrator
# @File: mod_switch_interface.py
from __future__ import annotations

from PyQt5.QtCore import QPoint, QModelIndex
from PyQt5.QtWidgets import QWidget, QListWidgetItem
from qfluentwidgets.components.widgets.flyout import IconWidget

from common.myIcon import MyIcon
from ui.mod_switch import Ui_ModSwitchInterface
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, FluentIcon


class ModSwitchInterface(QWidget, Ui_ModSwitchInterface):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.connectSignals()
        for i in range(10):
            self.addType(f'全部-{str(i) * 10}')
        self.switch_type_info.setCurrentRow(0)

    def addType(self, title):
        item = QListWidgetItem(title)
        self.switch_type_info.addItem(item)

    def addShow(self, title_list: list[str]):
        self.switch_type_show.addItems(title_list)

    def connectSignals(self):
        self.switch_type_info.customContextMenuRequested.connect(self.infoContextMenuEvent)
        self.switch_type_info.currentItemChanged.connect(self.currentItemChanged)

    def currentItemChanged(self, now: QListWidgetItem | None, before: QListWidgetItem | None):
        print('now', now, now.text() if now else '')
        import random
        if now:
            self.switch_type_show.clear()
            self.addShow([f'mod-{now.text()}-{str(i) * 20}' for i in range(random.randint(10, 300))])

    def infoContextMenuEvent(self, a0: QPoint):
        if not self.switch_type_info.rect().contains(a0):
            return
        item = self.switch_type_info.itemAt(a0)
        # if not item:
        #     self.switch_type_info.setCurrentIndex(QModelIndex())
        if item and not item.isSelected():
            self.switch_type_info.setCurrentItem(item)

        menu = RoundMenu()
        if item:
            use = Action(MyIcon.switch,'切换')
            menu.addAction(use)
        add = Action(FluentIcon.ADD, '添加')
        menu.addAction(add)
        if item:
            edit = Action(FluentIcon.EDIT, '修改')
            menu.addAction(edit)
            trash = Action(FluentIcon.DELETE, '删除')
            trash.triggered.connect(lambda x: self.removeInfoItem(item))
            menu.addAction(trash)
        menu.closedSignal.connect(menu.deleteLater)
        menu.exec(self.switch_type_info.mapToGlobal(a0), aniType=MenuAnimationType.DROP_DOWN)

    def removeInfoItem(self, item: QListWidgetItem):
        row = self.switch_type_info.row(item)
        self.switch_type_info.takeItem(row)
