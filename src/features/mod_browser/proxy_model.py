# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: mod_search_proxy.py
from PySide6.QtCore import QSortFilterProxyModel, Qt

from shared.mods import ModCategory
from shared.runtime import LogBase


class ProxyModSearch(QSortFilterProxyModel, LogBase):
    TAG = "ProxyModSearch"

    def __init__(self, parent):
        super().__init__(parent)
        self._disableFilter = False
        self._filter_category: ModCategory | None = None
        self.setManualSearchModel()
        self.setFilterKeyColumn(-1)

    def setManualSearchModel(self):
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def setCategoryFilter(self, category: ModCategory | None):
        self._filter_category = category
        self.logger.debug(f"{category=}")
        self.invalidate()

    def filterAcceptsRow(self, source_row, source_parent):
        if self._disableFilter:
            return True
        if not super().filterAcceptsRow(source_row, source_parent):
            return False
        if self._filter_category is None:
            return True

        index = self.sourceModel().index(source_row, 1, source_parent)
        category: ModCategory = self.sourceModel().data(index, Qt.UserRole + 1)
        if category.category != self._filter_category.category:
            return False
        if self._filter_category.subCategory == "":
            return True
        if self._filter_category.subCategory == category.subCategory:
            return True
        return False

    def disableFilter(self, status: bool):
        self._disableFilter = status
        if not status:
            self.invalidateFilter()

    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left, Qt.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.DisplayRole)
        return str(left_data) < str(right_data)


__all__ = ["ProxyModSearch"]
