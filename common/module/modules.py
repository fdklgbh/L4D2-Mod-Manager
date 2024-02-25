# -*- coding: utf-8 -*-
# @Time: 2023/12/31
# @Author: Administrator
# @File: tableModules.py
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal

from common import logger
from common.Bus import signalBus
from common.config.main_config import vpkConfig
from common.conf import NEED_DATA, ModType


class TableModel(QAbstractTableModel):
    vpkInfoHideSignal = pyqtSignal()

    def __init__(self, headers):
        super().__init__()
        self._headers = headers
        self._search_result = []
        self._data = []
        self.customData = {}
        # {file_title: {check_type: "", father_type: ""}}
        for i in ModType.keys():
            setattr(self, f'_{i}', [])
        for i in ModType.child_keys():
            setattr(self, f'_{i}', [])
        self.search_type = ''
        self.father_type = ''
        signalBus.fileTypeChanged.connect(self.changeCustomData)

    def rowCount(self, parent=QModelIndex()):
        return len(self._search_result)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def headerData(self, section, orientation, role=...):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._headers[section])
        return ''

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        # logger.debug(f"{type(index.data(Qt.UserRole + 1))} {index.data(Qt.UserRole + 1)}")
        if not index.isValid():
            return None
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(self._search_result[row][col])
        if role == Qt.UserRole + 1:
            title = self._search_result[row][0]
            return self.customData.get(title)
        if role == Qt.UserRole + 2:
            return self._search_result[row]
        return None

    def changeCustomData(self, data_info, check_type: str, father_type: str):
        title = data_info[0]
        if not self.customData.get(title):
            return
        print('设置customData')
        old_custom = self.customData.get(title)
        logger.debug(f'old_custom: {old_custom}')
        self.customData[title] = {
            'check_type': check_type,
            'father_type': father_type
        }
        logger.debug(f'new customData: {self.customData[title]}')
        if old_custom["father_type"]:
            old_father_type: list = getattr(self, f'_{old_custom["father_type"]}')
            print('old_father_type', old_father_type)
            old_father_type.remove(data_info)
        if father_type:
            new_father_type: list = getattr(self, f'_{father_type}')
            new_father_type.append(data_info)
            new_father_type.sort(key=lambda x: x[0])
        old_check_type: list = getattr(self, f'_{old_custom["check_type"]}')
        old_check_type.remove(data_info)
        new_check_type: list = getattr(self, f'_{check_type}')
        new_check_type.append(data_info)
        new_check_type.sort(key=lambda x: x[0])
        if not self.search_type and not self.father_type:
            vpkConfig.update_config(title, self.customData[title])
            return
        row = self._search_result.index(data_info)
        self.beginRemoveRows(QModelIndex(), row, row)

        index = self._find_index(self._search_result, title)
        self._search_result.pop(index)
        self.endRemoveRows()
        self.vpkInfoHideSignal.emit()
        vpkConfig.update_config(title, self.customData[title])

    def sortData(self):
        # todo 排序后无效果
        key = ModType.keys()[:]
        key.extend(ModType.child_keys())
        for i in key:
            setattr(self, f'_{i}', sorted(getattr(self, f'_{i}'), key=lambda x: x[0]))

    def setSearchText(self, text):
        search_text = text.strip().lower()
        search_data = self._data[:]
        if self.search_type:
            search_data = getattr(self, f'_{self.search_type}')[:]
        self.beginResetModel()
        if search_text:
            self._search_result = []
            for row in search_data:
                for data in row:
                    data: str
                    if search_text in data.lower():
                        self._search_result.append(row)
                        break
        else:
            self._search_result = search_data

        self.endResetModel()

    def resetModel(self):
        self.beginResetModel()
        self._search_result = self._data[:]
        self.beginResetModel()

    def addRow(self, data: dict):
        title = data.get('filePath').stem
        add_data = [title]
        for i in NEED_DATA:
            add_data.append(data.get(i, ''))
        date_len = len(self._data)
        self.beginInsertRows(QModelIndex(), date_len, date_len)
        self._data.append(add_data)
        father_type = data.get('father_type')
        check_type = data.get('check_type', 'other')
        self.customData[title] = {'check_type': check_type, 'father_type': father_type}
        _list = getattr(self, f'_{check_type}')
        _list.append(add_data)
        if father_type:
            _list = getattr(self, f'_{father_type}')
            _list.append(add_data)
        self._search_result.append(add_data)

        self.endInsertRows()

    def get_row_title(self, row):
        return self.get_row_data(row)[0]

    def get_row_data(self, row):
        return self._search_result[row]

    def sort(self, column, order=...):
        if self._search_result:
            self.layoutAboutToBeChanged.emit()
            self._search_result.sort(key=lambda x: x[column], reverse=(order == Qt.AscendingOrder))
            self.layoutChanged.emit()

    def get_header_title(self, index: int):
        return self._headers[index]

    def refresh(self):
        self._data = []
        self._search_result = []
        self.search_type = ''
        self.father_type = None
        # self._map = []
        for i in ModType.keys():
            setattr(self, f'_{i}', [])
        for i in ModType.child_keys():
            setattr(self, f'_{i}', [])

    def changeType(self, type_data):
        self.beginResetModel()
        if type_data:
            self._search_result = getattr(self, f'_{type_data}')[:]
        else:
            self._search_result = self._data[:]
        self.endResetModel()

    def removeRow(self, row, filename, parent=QModelIndex()):
        logger.debug(f'删除数据行：{row} {filename}')
        _ = self.get_row_title(row)
        logger.debug(f'row:{row}, filename:{filename}')
        self.beginRemoveRows(parent, row, row)

        index = self._find_index(self._search_result, filename)
        self._search_result.pop(index)
        self._data.pop(self._find_index(self._data, filename))
        self._remove_file_type(filename)
        self.endRemoveRows()

    def _remove_file_type(self, filename: str):
        """
        删除customData 数据 以及对应类型中的数据
        :param filename:
        :return:
        """
        file_type: dict = self.customData.pop(filename)
        if file_type:
            _list: list = getattr(self, f'_{file_type.get("check_type")}')
            for i, value in enumerate(_list[:]):
                if value[0] == filename:
                    _list.pop(i)
                    break
            father_type = file_type.get("father_type")
            if father_type:
                _list: list = getattr(self, f'_{father_type}')
                for i, value in enumerate(_list[:]):
                    if value[0] == filename:
                        _list.pop(i)
                        break

    def _insert_file_type(self, filename: str, file_type: dict):
        pass

    def insertRow(self, info: dict, parent=QModelIndex()):
        data = info.get('data')
        file_type: dict = info.get('file_type')
        check_type = file_type.get('check_type', 'other')
        father_type = file_type.get('father_type')
        self.beginInsertRows(parent, len(self._data), len(self._data))
        self._data = self._insertData(self._data, data)

        if father_type:
            setattr(self, f'_{father_type}',
                    self._insertData(getattr(self, f'_{father_type}'), data))
        if check_type:
            setattr(self, f'_{check_type}',
                    self._insertData(getattr(self, f'_{check_type}'), data))
        if self.search_type == check_type:
            self._search_result = getattr(self, f'_{check_type}')
        elif self.search_type == father_type:
            self._search_result = getattr(self, f'_{father_type}')
        else:
            self._search_result = self._data[:]
        self.customData[data[0]] = file_type
        logger.debug(f'data: {data}')
        self.endInsertRows()

    def _insertData(self, data: list, insert_data: list):
        index = -1
        for i, value in enumerate(data):
            if value[0] == insert_data[0]:
                index = i
        if index >= 0:
            # data.pop(index)
            # data.insert(index, insert_data)
            data[index] = insert_data
        else:
            data.append(insert_data)
            data.sort(key=lambda x: x[0])
        return data

    @staticmethod
    def _find_index(data, remove_file_name):
        for index, file_data in enumerate(data):
            if remove_file_name == file_data[0]:
                return index
