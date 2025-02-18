# -*- coding: utf-8 -*-
# @Time: 2025/1/18
# @Author: Administrator
# @File: item.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidgetItem
from typing import Literal

__all__ = ['Item']


class Item:
    @staticmethod
    def get_item_title(item: QListWidgetItem) -> str:
        return item.data(Qt.UserRole + 1)

    def set_item_title(self, item: QListWidgetItem, name: str):
        item.setData(Qt.UserRole + 1, name)
        self.set_text(item)

    @staticmethod
    def get_item_fileName(item: QListWidgetItem) -> str:
        return item.data(Qt.UserRole)

    @staticmethod
    def get_item_id(item: QListWidgetItem) -> int:
        return item.data(Qt.UserRole + 4)

    @staticmethod
    def get_item_father_type(item: QListWidgetItem) -> str:
        return item.data(Qt.UserRole + 2)

    @staticmethod
    def get_item_child_type(item: QListWidgetItem) -> str:
        return item.data(Qt.UserRole + 3)

    @staticmethod
    def get_item_enable_status(item: QListWidgetItem) -> Literal[0, 1]:
        return item.data(Qt.UserRole + 5)

    def setItems(self, data: dict):
        """
        {文件名称: {title: 解析标题, father_type: 一级分类, child_type: 二级分类}}
        :param data:
        :return:
        """
        for fileName, value in data.items():
            yield self.setOnceItem(fileName, value)

    @staticmethod
    def setOnceItem(fileName, data: dict):
        fatherType = data['fatherType']
        childType = data['childType']
        title = data['title']
        item = QListWidgetItem(f'{fileName} - {title}')
        item.setData(Qt.UserRole, fileName)
        item.setData(Qt.UserRole + 1, title)
        item.setData(Qt.UserRole + 2, fatherType)
        item.setData(Qt.UserRole + 3, childType)
        item.setData(Qt.UserRole + 4, data['id'])
        item.setData(Qt.UserRole + 5, data.get('enabled', 1))
        return item

    @staticmethod
    def get_text(item: QListWidgetItem) -> str:
        return item.text()

    def set_text(self, item: QListWidgetItem):
        item.setText(f'{self.get_item_fileName(item)} - {self.get_item_title(item)}')
