# -*- coding: utf-8 -*-
# @Time: 2024/2/23
# @Author: Administrator
# @File: custom_tree_widget.py
from typing import Union

from PyQt5.QtCore import pyqtSignal, QModelIndex
from PyQt5.QtWidgets import QFrame, QTreeWidgetItem, QHBoxLayout
from qfluentwidgets import TreeWidget

from common.conf import ModType


class CustomTreeWidget(QFrame):
    selectedSignal = pyqtSignal(str, str, bool)

    def __init__(self, parent, data: list):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)
        self.setObjectName('frame')
        self.tree = TreeWidget(self)
        self.tree.setBorderVisible(True)
        child_type, father_type = data
        self.hBoxLayout.addWidget(self.tree)
        for key in ModType.type_menu_info():
            if isinstance(key, dict):
                for key_, value in key.items():
                    # 判断后续是否需要展开
                    is_father_item = bool(child_type) and key_ == father_type
                    selected_child = None
                    item = QTreeWidgetItem([key_])
                    for i in value:
                        child = QTreeWidgetItem(item, [i.title()])
                        if is_father_item and i == child_type:
                            selected_child = child
                    self.tree.addTopLevelItem(item)
                    if is_father_item:
                        item.setExpanded(True)
                    if selected_child:
                        selected_child.setSelected(True)
            else:
                item = QTreeWidgetItem([key])
                self.tree.addTopLevelItem(item)
                if father_type == key:
                    item.setSelected(True)

        self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self.itemSelectionChanged)
        self.tree.itemClicked.connect(self.trigger_item)
        self.setFixedSize(300, 380)

    @staticmethod
    def trigger_item(item: QTreeWidgetItem):
        if item.childCount():
            item.setExpanded(not item.isExpanded())

    def itemSelectionChanged(self):
        item = self.tree.currentItem()
        if not item.isSelected() or item.childCount():
            self.selectedSignal.emit('', '', False)
            return
        child = item.text(0)
        parent = item.parent()
        if parent:
            father = parent.text(0)
        else:
            father = child
            child = ''
        self.selectedSignal.emit(child, father, not bool(parent))
