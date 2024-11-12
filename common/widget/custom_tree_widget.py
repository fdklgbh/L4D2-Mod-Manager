# -*- coding: utf-8 -*-
# @Time: 2024/2/23
# @Author: Administrator
# @File: custom_tree_widget.py
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QTreeWidgetItem, QHBoxLayout
from qfluentwidgets import TreeWidget

from common.conf import ModType


class CustomTreeWidget(QFrame):
    selectedSignal = pyqtSignal(str, str)

    def __init__(self, parent, data: list):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)
        self.setObjectName('frame')
        self.tree = TreeWidget(self)
        self.tree.setBorderVisible(True)
        check_type, father_type = data
        self.hBoxLayout.addWidget(self.tree)
        for key in ModType.type_key():
            if isinstance(key, dict):
                for key_, value in key.items():
                    is_father_item = father_type and key_ == ModType.key_to_value(father_type)
                    selected_child = None
                    item = QTreeWidgetItem([key_])
                    for i in value:
                        child = QTreeWidgetItem(item, [i.title()])
                        if is_father_item and i == check_type:
                            selected_child = child
                    self.tree.addTopLevelItem(item)
                    if is_father_item:
                        item.setExpanded(True)
                    if selected_child:
                        selected_child.setSelected(True)
            else:
                item = QTreeWidgetItem([key])
                self.tree.addTopLevelItem(item)
                if not father_type:
                    if key == ModType.key_to_value(check_type):
                        item.setSelected(True)

        self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self.itemSelectionChanged)
        self.setFixedSize(300, 380)

    def itemSelectionChanged(self):
        item = self.tree.currentItem()
        if not item.isSelected() or item.childCount():
            self.selectedSignal.emit('', '')
            return
        father = ''
        check = item.text(0)
        parent = item.parent()
        if parent:
            father = ModType.value_to_key(parent.text(0))
        self.selectedSignal.emit(check, father)
