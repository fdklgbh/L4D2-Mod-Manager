# -*- coding: utf-8 -*-
# @Time: 2026/1/13
# @Author: Administrator
# @File: change_category.py
from PySide6.QtCore import Signal
from qfluentwidgets_pro import MessageBoxBase

from shared.mods import ModCategory, ModInfo
from shared.runtime import LogBase
from .category_tree_widget import CategoryTreeWidget

__all__ = ["ChangeCategoryMessageBox"]


class ChangeCategoryMessageBox(MessageBoxBase, LogBase):
    TAG = "ChangeCategoryMessageBox"
    categoryChanged = Signal(list, ModCategory)

    def __init__(self, parent, data: list[ModInfo]):
        super().__init__(parent)
        self.data_info = data
        self.setWindowTitle("修改Mod分类")
        self.category = data[0].modCategory if len(data) == 1 else None
        self.selected_category: ModCategory | None = None
        self.tableWidget = CategoryTreeWidget(self, self.category)

        self.viewLayout.addWidget(self.tableWidget)
        self.yesButton.setText(self.tr("确定"))
        self.cancelButton.setText(self.tr("取消"))

        self.widget.setMinimumWidth(360)
        self.yesButton.setDisabled(True)
        self.tableWidget.selectedSignal.connect(self.check)
        self.yesButton.clicked.connect(self.yesButton_clicked)

    def yesButton_clicked(self, *args):
        self.categoryChanged.emit(self.data_info, self.selected_category)

    def check(self, category: str, subcategory: str, valid_leaf: bool):
        """
        确定按钮是否显示

        :param category: 一级分类
        :param subcategory: 二级分类
        :param valid_leaf: 是否选中了可保存的叶节点
        """
        self.selected_category = (
            ModCategory(category=category, subCategory=subcategory)
            if valid_leaf
            else None
        )
        unchanged = self.category == self.selected_category
        self.yesButton.setDisabled(not valid_leaf or unchanged)
