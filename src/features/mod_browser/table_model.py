# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: modShowModel.py
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QWidget

from shared.mods import ModCategory, ModInfo
from shared.runtime import LogBase


class ModShowModel(QAbstractTableModel, LogBase):
    TAG = "ModShowModel"

    def __init__(self, parent: QWidget, headers: list[str], folder_path: Path):
        super().__init__(parent=parent)
        self._headers = headers
        self._folder_path = folder_path
        self._data: dict[str, ModInfo] = {}
        self._filenames: list[str] = []
        self._menu_info: dict[str, int] = {}

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            self.logger.debug("not valid")
            return None
        if (row := index.row()) > len(self._filenames):
            return None
        key = self._filenames[row]
        modeInfo = self._data[key]
        header = self._headers[index.column()]
        if role in (Qt.DisplayRole, Qt.EditRole):
            key = self.__find_key(header)
            value = getattr(modeInfo, key)
            if header == "标题":
                key = self.__find_key("自定义标题")
                new = getattr(modeInfo, key)
                if new:
                    value = new
            return value
        elif role == Qt.UserRole:
            # 行源数据信息
            return modeInfo
        elif role == Qt.UserRole + 1:
            # 行分类信息
            return modeInfo.modCategory
        return None

    @property
    def get_menu_infos(self):
        return self._menu_info

    @lru_cache()
    def __find_key(self, header):
        return next(
            (k for k, v in ModInfo.model_fields.items() if v.description == header),
            None,
        )

    def headerData(self, section, orientation, role=...):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def flags(self, index):
        if index.column() in [1, 3]:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def addModInfo(self, modInfo: ModInfo):
        """
        添加解析后的模组信息。

        Args:
            modInfo：模组信息。
        """
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._add_once_data(modInfo)
        self.endInsertRows()

    def upsertModInfo(self, modInfo: ModInfo):
        if modInfo.filename not in self._data:
            self.addModInfo(modInfo)
            return

        row = self._filenames.index(modInfo.filename)
        self._remove_menu_info(self._data[modInfo.filename])
        self._data[modInfo.filename] = modInfo
        self._add_menu_info(modInfo)
        self.dataChanged.emit(
            self.index(row, 0), self.index(row, self.columnCount() - 1)
        )

    def _add_once_data(self, modInfo: ModInfo):
        self._data[modInfo.filename] = modInfo
        self._filenames.append(modInfo.filename)
        self._add_menu_info(modInfo)

    def addModInfos(self, modInfos: list[ModInfo]):
        """
        添加解析后的模组信息列表。

        Args:
            modInfos：模组信息列表。
        """
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row + len(modInfos) - 1)
        try:
            for i, modInfo in enumerate(modInfos):
                self._add_once_data(modInfo)
        except Exception as e:
            self.logger.exception(f"插入异常, {e}")
            raise
        finally:
            self.endInsertRows()

    def removeModInfo(self, row: int):
        """
        删除指定行。

        Args:
            row：行索引。
        """
        if 0 <= row < len(self._data):
            self.beginRemoveRows(QModelIndex(), row, row)
            # 删除数据
            self._remove_menu_info(self._data[self._filenames[row]])
            del self._data[self._filenames[row]]
            self._menu_info["all"] -= 1
            self._filenames.pop(row)
            self.endRemoveRows()

    def _add_menu_info(self, modInfo: ModInfo):
        key, subkey = self._menu_key(modInfo)
        self._menu_info.setdefault(key, 0)
        self._menu_info[key] += 1
        self._menu_info.setdefault(subkey, 0)
        self._menu_info[subkey] += 1
        self._menu_info.setdefault("all", 0)
        self._menu_info["all"] += 1

    @staticmethod
    def _menu_key(modInfo: ModInfo):
        key = modInfo.modCategory.category
        subkey = f"{key}-{modInfo.modCategory.subCategory}"
        return key, subkey

    def _remove_menu_info(self, modInfo: ModInfo):
        key, subkey = self._menu_key(modInfo)
        self._menu_info[key] -= 1
        self._menu_info[subkey] -= 1

    def changeCategory(self, infos: dict[str, ModCategory]):
        """
        修改模组分类。
        """
        for filename, category in infos.items():
            if filename not in self._data:
                continue
            current = self._data[filename].modCategory
            if current == category:
                continue
            self._remove_menu_info(self._data[filename])
            self._data[filename].modCategory = category
            self._add_menu_info(self._data[filename])
            self._menu_info["all"] -= 1
            row = self._filenames.index(filename)
            self.dataChanged.emit(
                self.index(row, 0),
                self.index(row, self.columnCount() - 1),
                [Qt.DisplayRole, Qt.UserRole, Qt.UserRole + 1],
            )

    def clearAll(self):
        """清空所有数据"""
        if not self._data:
            return
        self.beginRemoveRows(QModelIndex(), 0, len(self._data) - 1)
        self._data.clear()
        self._filenames.clear()
        self._menu_info.clear()
        self.endRemoveRows()

    def getHeader(self, column):
        return self._headers[column]
