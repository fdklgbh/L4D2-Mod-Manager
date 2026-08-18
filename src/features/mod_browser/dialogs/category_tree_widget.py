# -*- coding: utf-8 -*-
# @Time: 2026/1/16
# @Author: Administrator
# @File: category_tree_widget.py
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QTreeWidgetItem
from qfluentwidgets_pro import TreeWidget

from shared.mods import Menu, ModCategory


class CategoryTreeWidget(QFrame):
    selectedSignal = Signal(str, str, bool)

    def __init__(self, parent, data: ModCategory | None):
        super().__init__(parent=parent)
        self.data = data
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)
        self.setObjectName("frame")
        self.tree = TreeWidget(self)
        self.tree.setBorderVisible(True)
        self.hBoxLayout.addWidget(self.tree)
        for key in Menu.category:
            if Menu.has_child(key):
                item = QTreeWidgetItem(self.tree, [key])
                is_category = data is not None and data.category == key
                for subcategory in Menu.find_subcategory(key) or []:
                    sub = QTreeWidgetItem(item, [subcategory])
                    if is_category and data.subCategory == subcategory:
                        sub.setSelected(True)
                        item.setExpanded(True)
            else:
                item = QTreeWidgetItem(self.tree, [key])
                if data is not None and data.category == key:
                    item.setSelected(True)

        self.tree.setHeaderHidden(True)
        self.tree.itemSelectionChanged.connect(self.itemSelectionChanged)
        self.tree.itemClicked.connect(self.trigger_item)
        self.setFixedSize(300, 380)

    @staticmethod
    def trigger_item(item: QTreeWidgetItem, *args):
        if item.childCount():
            item.setExpanded(not item.isExpanded())

    def itemSelectionChanged(self):
        item = self.tree.currentItem()
        if item is None or not item.isSelected() or item.childCount():
            self.selectedSignal.emit("", "", False)
            return
        subcategory = item.text(0)
        parent = item.parent()
        if parent is not None:
            category = parent.text(0)
        else:
            category = subcategory
            subcategory = ""
        self.selectedSignal.emit(category, subcategory, True)
