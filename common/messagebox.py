# -*- coding: utf-8 -*-
# @Time: 2024/2/23
# @Author: Administrator
# @File: messagebox.py
from qfluentwidgets import MessageBoxBase

from common.Bus import signalBus
from common.widget.custom_tree_widget import CustomTreeWidget
from common.conf import ModType


class ChangeTypeMessageBox(MessageBoxBase):
    def __init__(self, parent, data: list, more=False):
        super().__init__(parent)
        self.new_check_type = ''
        self.new_father_type = ''
        self.setWindowTitle('修改Mod分类')
        self._more = more
        self.data_info, self.check_type, self.father_type = data
        if more:
            self.check_type = None
            self.father_type = None
        self.tableWidget = CustomTreeWidget(self, [self.check_type, self.father_type])

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
        check_type = self.new_check_type.lower() if self.new_father_type else ModType.value_to_key(self.new_check_type)
        father_type = self.new_father_type
        if not self._more:
            signalBus.fileTypeChanged.emit(self.data_info, check_type, father_type)
        else:
            for data in self.data_info:
                signalBus.fileTypeChanged.emit(data, check_type, father_type)


    def check(self, check_type: str, father_type):
        """
        确定按钮显示与否
        :param check_type:
        :param father_type:
        :return:
        """
        if not check_type and not father_type:
            self.yesButton.setDisabled(True)
        elif check_type.lower() != self.check_type:
            self.yesButton.setDisabled(False)
            self.new_check_type = check_type
            self.new_father_type = father_type
        else:
            self.yesButton.setDisabled(True)
