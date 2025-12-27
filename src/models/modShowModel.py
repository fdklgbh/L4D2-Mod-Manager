# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: modShowModel.py
import bisect
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QWidget

from core import LogBase
from schemas import *


class ModShowModel(QAbstractTableModel, LogBase):
    TAG = "ModShowModel"

    def __init__(self, parent: QWidget, headers: list[str], folder_path: Path):
        print("ModShowModel")
        super().__init__(parent=parent)
        self._headers = headers
        self._folder_path = folder_path
        # self._timer = QTimer(self)
        self._data: list[ModInfo] = []
        self._pending: list[ModInfo] = []
        self._filename_to_index: dict[str, int] = {}  # 文件名 -> 索引映射
        self._index_to_filename: dict[int, str] = {}  # 索引 -> 文件名映射
        # self._timer.timeout.connect(self._flush)
        # self._timer.start(50)

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            self.logger.debug("not valid")
            return None
        modeInfo = self._data[index.row()]
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
        解析后添加
        Args:
            modInfo:

        Returns:

        """
        # self._pending.append(modInfo)
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.append(modInfo)
        self._filename_to_index[modInfo.filename] = row
        self._index_to_filename[row] = modInfo.filename
        self.endInsertRows()

    def _flush(self):
        if not self._pending:
            return
        row = len(self._data)
        pending = self._pending[:]
        self.logger.debug(f"{row}, {len(pending)=}, {self._folder_path}")
        self.beginInsertRows(QModelIndex(), row, row + len(pending) - 1)
        self._data.extend(pending)
        for i, modInfo in enumerate(pending):
            self._filename_to_index[modInfo.filename] = row + i
            self._index_to_filename[row + i] = modInfo.filename
        del self._pending[: len(pending)]
        self.endInsertRows()

    def addModInfos(self, modInfo: list[ModInfo]):
        """
        解析后添加
        Args:
            modInfo:

        Returns:

        """
        # row = len(self._data)
        # self.beginInsertRows(QModelIndex(), row, row)
        # try:
        #     self._data.append(modInfo)
        #     self._filename_to_index[modInfo.filename] = row
        #     self._index_to_filename[row] = modInfo.filename
        # except Exception as e:
        #     self.logger.exception(f'插入异常, {e}')
        #     raise
        # finally:
        #     self.endInsertRows()
        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row + len(modInfo) - 1)
        try:
            self._data.extend(modInfo)
            for i in modInfo:
                self._filename_to_index[i.filename] = row
                self._index_to_filename[row] = i.filename
        except Exception as e:
            self.logger.exception(f"插入异常, {e}")
            raise
        finally:
            self.endInsertRows()

    def removeModInfo(self, row: int):
        """
        删除
        Args:
            row:

        Returns:

        """
        if 0 <= row < len(self._data):
            name = self._data[row].name
            self.beginRemoveRows(QModelIndex(), row, row)
            # 删除数据
            del self._data[row]
            # 更新映射关系
            del self._filename_to_index[name]
            del self._index_to_filename[row]

            # 调整后续索引映射
            self._adjust_indices_after_removal(row)
            self.endRemoveRows()

    def insertModInfo(self, modInfos: list[ModInfo] | ModInfo):
        """
        移动mod
        Args:
            modInfos:

        Returns:

        """
        if not isinstance(modInfos, list):
            modInfos = [modInfos]

        for mod_info in modInfos:
            filenames = [item.filename for item in self._data]
            pos = bisect.bisect_left(filenames, mod_info.filename)

            if pos < len(self._data) and self._data[pos].filename == mod_info.filename:
                self._data[pos] = mod_info
                top_left = self.index(pos, 0)
                bottom_right = self.index(pos, len(self._headers) - 1)
                self.dataChanged.emit(top_left, bottom_right)
            else:
                self.beginInsertRows(QModelIndex(), pos, pos)
                self._data.insert(pos, mod_info)
                self.endInsertRows()

    def changeCategory(self, infos: dict[str, ModCategory]):
        """
        todo proxy中处理修改后展示内容
        :return:
        """
        for filename, category in infos.items():
            if not (index := self._filename_to_index.get(filename)):
                continue
            self._data[index].modCategory = category

    def _adjust_indices_after_removal(self, removed_index: int):
        """
        删除元素后调整索引映射
        Args:
            removed_index:

        Returns:

        """
        # 创建新的映射字典
        adjusted_index_to_filename = {}
        adjusted_filename_to_index = {}

        # 重新构建映射关系
        for index, name in self._index_to_filename.items():
            if index > removed_index:
                # 后续索引减1
                new_index = index - 1
                adjusted_index_to_filename[new_index] = name
                adjusted_filename_to_index[name] = new_index
            else:
                # 前面的索引不变
                adjusted_index_to_filename[index] = name
                adjusted_filename_to_index[name] = index

        # 更新映射字典
        self._index_to_filename = adjusted_index_to_filename
        self._filename_to_index = adjusted_filename_to_index

    def clearAll(self):
        """清空所有数据"""
        if not self._data:
            return
        self.beginRemoveRows(QModelIndex(), 0, len(self._data) - 1)
        self._data.clear()
        self._filename_to_index.clear()
        self._index_to_filename.clear()
        self.endRemoveRows()

    def getHeader(self, column):
        return self._headers[column]
