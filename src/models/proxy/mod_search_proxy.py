# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: mod_search_proxy.py
from PyQt5.QtCore import QSortFilterProxyModel, Qt

from schemas import ModCategory


class ProxyModSearch(QSortFilterProxyModel):
    def __init__(self, parent):
        super().__init__(parent)
        self._filter_category: ModCategory = ModCategory(category='全部', subCategory='')

    def setCategoryFilter(self, category, subCategory):
        self._filter_category = ModCategory(category=category, subCategory=subCategory)
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        if not super().filterAcceptsRow(source_row, source_parent):
            return False

        if self._filter_category.category == '全部':
            return True

        index = self.sourceModel().index(source_row, 1, source_parent)
        category: ModCategory = self.sourceModel().data(index, Qt.UserRole + 1)
        if category.category != self._filter_category.category:
            return False
        if self._filter_category.subCategory == '全部':
            return True
        if self._filter_category.subCategory == category.subCategory:
            return True
        return False

__all__ = ['ProxyModSearch']