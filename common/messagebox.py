# -*- coding: utf-8 -*-
# @Time: 2024/2/23
# @Author: Administrator
# @File: messagebox.py
from qfluentwidgets import MessageBoxBase

from common.Bus import signalBus
from common.widget.custom_tree_widget import CustomTreeWidget
from common.conf import ModType


class ChangeTypeMessageBox(MessageBoxBase):
    def __init__(self, parent, data: list):
        super().__init__(parent)
        self.new_check_type = ''
        self.new_father_type = ''
        self.setWindowTitle('修改Mod分类')
        self.tableWidget = CustomTreeWidget(self, data[1:])
        data_info, self.check_type, self.father_type = data
        # add widget to view layout
        self.viewLayout.addWidget(self.tableWidget)
        # change the text of button
        self.yesButton.setText(self.tr('确定'))
        self.cancelButton.setText(self.tr('取消'))

        self.widget.setMinimumWidth(360)
        self.yesButton.setDisabled(True)
        self.tableWidget.selectedSignal.connect(self.check)
        self.yesButton.clicked.connect(
            lambda: signalBus.fileTypeChanged.emit(data_info,
                                                   self.new_check_type.lower() if self.new_father_type else ModType.value_to_key(
                                                       self.new_check_type), self.new_father_type))

    def check(self, check_type: str, father_type):
        print(f'选中的数据：{check_type}, father_type: {father_type}')
        print(f'self.check_type: {self.check_type}, self.father_type: {self.father_type}')
        if check_type.lower() != self.check_type:
            self.yesButton.setDisabled(False)
            self.new_check_type = check_type
            self.new_father_type = father_type
        else:
            self.yesButton.setDisabled(True)
