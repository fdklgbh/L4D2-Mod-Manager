# -*- coding: utf-8 -*-
# @Time: 2024/2/23
# @Author: Administrator
# @File: messagebox.py
from qfluentwidgets import MessageBoxBase

from common import logger
from common.Bus import signalBus
from common.widget.custom_tree_widget import CustomTreeWidget
from common.conf import ModType


class ChangeTypeMessageBox(MessageBoxBase):
    def __init__(self, parent, data: list, more=False):
        super().__init__(parent)
        self.new_check_type = ''
        self.new_father_type = ''
        self.setWindowTitle('修改Mod分类')
        self.data_info, self.child_type, self.father_type = data
        self._more = len(self.data_info) > 1
        if more:
            self.child_type = ''
            self.father_type = ''
        self.tableWidget = CustomTreeWidget(self, [self.child_type, self.father_type])

        # add widget to view layout
        self.viewLayout.addWidget(self.tableWidget)
        # change the text of button
        self.yesButton.setText(self.tr('确定'))
        self.cancelButton.setText(self.tr('取消'))

        self.widget.setMinimumWidth(360)
        self.yesButton.setDisabled(True)
        self.tableWidget.selectedSignal.connect(self.check)
        self.yesButton.clicked.connect(self.yesButton_clicked)

    def yesButton_clicked(self, *args):
        child_type = self.new_check_type
        father_type = self.new_father_type
        logger.debug('yesButton_clicked %s %s', child_type, father_type)
        for data in self.data_info:
            signalBus.fileTypeChanged.emit(data, child_type, father_type)

    def check(self, child_type: str, father_type: str, no_child: bool):
        """
        确定按钮显示与否
        :param no_child: 是否无二级分类
        :param child_type:
        :param father_type:
        :return:
        """

        def change_disable_status(status):
            self.yesButton.setDisabled(status)
            if status is False:
                self.new_check_type = child_type
                self.new_father_type = father_type

        if father_type == self.father_type:
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




