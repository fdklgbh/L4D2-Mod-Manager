# -*- coding: utf-8 -*-
# @Time: 2024/3/3
# @Author: Administrator
# @File: entrust.py
"""
    tableView委托
"""
from PyQt5.QtCore import pyqtSignal, QModelIndex
from qfluentwidgets import LineEdit, TableItemDelegate


class EditDelegate(TableItemDelegate):
    editFinishedSignal = pyqtSignal(QModelIndex, str)

    def createEditor(self, parent, option, index):
        editor = LineEdit(parent)
        return editor

    def setModelData(self, editor, model, index):
        super().setModelData(editor, model, index)
        if model.data(index) == editor.text():
            self.editFinishedSignal.emit(index)
