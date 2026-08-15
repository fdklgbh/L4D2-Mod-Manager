# -*- coding: utf-8 -*-
# @Time: 2026/1/13
# @Author: Administrator
# @File: change_category.py
from qfluentwidgets import MessageBoxBase

from shared.mods import ModInfo
from shared.runtime import LogBase, signalBus
from .category_tree_widget import CategoryTreeWidget

__all__ = ["ChangeCategoryMessageBox"]


class ChangeCategoryMessageBox(MessageBoxBase, LogBase):
    TAG = "ChangeCategoryMessageBox"

    def __init__(self, parent, data: list[ModInfo]):
        super().__init__(parent)
        self.new_check_type = ""
        self.new_father_type = ""
        self.setWindowTitle("修改Mod分类")
        self.category = category = data[0].modCategory
        if len(data) > 1:
            category = None
        self.tableWidget = CategoryTreeWidget(self, category)

        self.viewLayout.addWidget(self.tableWidget)
        self.yesButton.setText(self.tr("确定"))
        self.cancelButton.setText(self.tr("取消"))

        self.widget.setMinimumWidth(360)
        self.yesButton.setDisabled(True)
        self.tableWidget.selectedSignal.connect(self.check)
        self.yesButton.clicked.connect(self.yesButton_clicked)

    def yesButton_clicked(self, *args):
        child_type = self.new_check_type
        father_type = self.new_father_type
        self.logger.debug("yesButton_clicked %s %s", child_type, father_type)
        for data in self.data_info:
            signalBus.fileTypeChanged.emit(
                data, father_type, child_type, self.father_type, self.child_type
            )

    def check(self, category, subcategory):
        """
        确定按钮显示与否
        :param category: 一级
        :param subcategory: 二级
        :return:
        """

        def change_disable_status(status):
            self.yesButton.setDisabled(status)
            if status is False:
                self.new_check_type = subcategory
                self.new_father_type = category

        if self.category is None:
            change_disable_status(False)
            return

        if category == self:
            if child_type and child_type != self.child_type:
                change_disable_status(False)
                return
            change_disable_status(True)
            return
        # 一级目录不一样的时候
        if no_child:
            change_disable_status(False)
        elif child_type:
            change_disable_status(False)
        else:
            change_disable_status(True)
