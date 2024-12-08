# -*- coding: utf-8 -*-
# @Time: 2023/12/31
# @Author: Administrator
# @File: tableModules.py
from typing import Union, List

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal

from common import logger
from common.Bus import signalBus
from common.config import vpkConfig
from common.conf import NEED_DATA, ModType


class TableModel(QAbstractTableModel):
    vpkInfoHideSignal = pyqtSignal()

    def __init__(self, headers):
        super().__init__()
        self._headers = headers
        self._search_result = []
        self._data = []
        # 当前目录下所有mod的分类信息 一级,二级分类
        self.customData = {}
        # {file_title: {check_type: "", father_type: ""}}
        for i in ModType.father_type_keys():
            setattr(self, f'_{i}', [])
            for j in ModType.child_keys(i):
                setattr(self, f'_{i}_{j}', [])
        # 当前分类的类型
        self.search_type = ''
        # 当前分类的父类 当前分类类型为父类,则为父类的翻译,即中文
        self.father_type = ''
        # 搜索文本
        self.search_text = ''
        signalBus.fileTypeChanged.connect(self.changeCustomData)

    def set_default_father_type(self):
        """
        设置一级分类为默认值
        :return:
        """
        for i in ModType.father_type_keys():
            setattr(self, f'_{i}', [])

    def set_default_child_type(self):
        """
        设置二级分类为默认值
        :return:
        """
        for i in ModType.father_type_keys():
            for j in ModType.child_keys(i):
                setattr(self, f'_{i}_{j}', [])

    @staticmethod
    def get_type_key(child_type=None, father_type=None):
        key = ''
        if father_type:
            key += f'_{father_type}'
        if child_type:
            key += f'_{child_type}'
        return key

    def get_type_data(self, child_type=None, father_type=None, key=None) -> List[list]:
        """
        获取数据有修改,也会修改key的值
        :param child_type:
        :param father_type:
        :param key:
        :return:
        """
        if key:
            return getattr(self, key)
        try:
            return getattr(self, self.get_type_key(child_type, father_type))
        except AttributeError as e:
            logger.error(f'get_type_data 二级分类:{child_type}, 一级分类{father_type}')
            raise e

    def set_type_data(self, data, child_type=None, father_type=None):
        setattr(self, self.get_type_key(child_type, father_type), data)

    def debug_search_result(self):
        pass

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
            if col == 1:
                data = str(self._search_result[row][-1])
                if data:
                    return data
            return str(self._search_result[row][col])
        if role == Qt.UserRole + 1:
            title = self._search_result[row][0]
            return self.customData.get(title)
        # 整行数据
        if role == Qt.UserRole + 2:
            return self._search_result[row]
        if role == Qt.UserRole + 3:
            # 自定义标题
            return self._search_result[row][-1]
        return None

    def changeCustomData(self, data_info, child_type: str, father_type: str):
        """
        文件类型修改
        :param data_info:
        :param child_type:
        :param father_type:
        :return:
        """
        title = data_info[0]
        if not self.customData.get(title):
            return
        old_custom = self.customData.get(title)
        logger.debug(f'old_custom: {old_custom}')
        logger.debug(f'search_type: {self.search_type}, father_type: {self.father_type}')
        self.customData[title] = {
            'child_type': child_type,
            'father_type': father_type
        }
        logger.debug(f'new customData: {self.customData[title]}')
        # 一级分类
        if father_type != old_custom['father_type']:
            old_father_type: list = self.get_type_data(father_type=old_custom["father_type"])
            old_father_type.remove(data_info)
            new_father_type: list = self.get_type_data(father_type=father_type)
            new_father_type.append(data_info)
            new_father_type.sort(key=lambda x: x[0])
        # 二级分类
        if old_custom["child_type"]:
            # 删除二级分类下数据
            old_child_type: list = self.get_type_data(old_custom["child_type"], old_custom["father_type"])
            old_child_type.remove(data_info)
        if child_type:
            # 添加数据到新的二级分类下
            new_child_type: list = self.get_type_data(child_type, father_type)
            new_child_type.append(data_info)
            new_child_type.sort(key=lambda x: x[0])
        if not self.search_type and not self.father_type:
            # 全部数据都展示
            vpkConfig.update_config(title, self.customData[title])
            return
        # 有筛选分类
        if self.father_type == father_type:
            if self.search_type == child_type or not self.search_type:
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
        for i in ModType.father_type_keys():
            self.set_type_data(sorted(self.get_type_data(father_type=i), key=lambda x: x[0]), father_type=i)
            for j in ModType.child_keys(i):
                self.set_type_data(sorted(self.get_type_data(j, i), key=lambda x: x[0]), j, i)

    def setSearchText(self, text):
        self.search_text = search_text = text.strip().lower()
        search_data = self._data[:]
        logger.debug('setSearchText: %s, %s', self.search_type, self.father_type)
        if self.father_type:
            if self.search_type:
                search_data = self.get_type_data(self.search_type, self.father_type)[:]
            else:
                search_data = self.get_type_data(father_type=self.father_type)[:]
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

    def setData(self, index, value, role=...):
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            column = index.column()
            if column != 1:
                return
            compare = self._search_result[row][-1]
            if not compare:
                compare = self._search_result[row][column]
            if compare != value:
                self._search_result[row][-1] = value
                title = self.get_row_title(row)
                logger.info(f'文件:{title}标题修改为 <{value}>,原始标题为 <{self._search_result[row][column]}> ')
                vpkConfig.update_config(title, {"customTitle": value})
                self.dataChanged.emit(index, index, [Qt.DisplayRole])
                return True
        return False

    def resetModel(self):
        self.beginResetModel()
        self._search_result = self._data[:]
        self.beginResetModel()

    @property
    def all_data_num(self):
        return len(self._data)

    def get_type_num(self, child_type=None, father_type=None):
        return len(self.get_type_data(child_type, father_type))

    def addRow(self, data: dict):
        title = data.get('filePath').stem

        add_data = [title]
        for i in NEED_DATA:
            add_data.append(data.get(i, ''))
        # 自定义标题
        add_data.append(data.get('customTitle', ''))
        date_len = len(self._data)
        self.beginInsertRows(QModelIndex(), date_len, date_len)
        self._data.append(add_data)
        father_type = data.get('father_type', '其他')
        child_type = data.get('child_type', '')
        self.customData[title] = {'child_type': child_type, 'father_type': father_type}
        if child_type:
            self.get_type_data(child_type, father_type).append(add_data)
        self.get_type_data(father_type=father_type).append(add_data)
        self._search_result.append(add_data)

        self.endInsertRows()

    def get_row_title(self, row):
        return self.get_row_data(row)[0]

    def get_row_data(self, row):
        return self._search_result[row]

    def sort(self, column, order=...):
        if self._search_result:
            self.layoutAboutToBeChanged.emit()
            if column != 1:
                key = lambda x: x[column]
            else:
                key = lambda x: x[column] if not x[-1] else x[-1]
            self._search_result.sort(key=key, reverse=(order == Qt.AscendingOrder))
            self.layoutChanged.emit()

    def get_header_title(self, index: int):
        return self._headers[index]

    def refresh(self):
        self._data = []
        self._search_result = []
        self.search_type = ''
        self.father_type = None
        # self._map = []
        self.set_default_father_type()
        self.set_default_child_type()

    def changeType(self, type_data: str, father_type: str):
        self.beginResetModel()
        logger.debug(f'type_data: {type_data}, father_type: {father_type}')
        if type_data or father_type:
            self._search_result = self.get_type_data(type_data, father_type)[:]
        else:
            self._search_result = self._data[:]
        self.endResetModel()

    def removeRow(self, row, filename, parent=QModelIndex()):
        logger.debug(f'删除数据行：{row} {filename}')
        _ = self.get_row_title(row)
        logger.debug(f'row:{row}, filename:{filename}')
        index = self._find_index(self._search_result, filename)
        self._search_result.pop(index)
        self._data.pop(self._find_index(self._data, filename))
        self._remove_file_type(filename)
        self.beginRemoveRows(parent, row, row)
        self.endRemoveRows()
        logger.debug('end')

    def _remove_file_type(self, filename: str):
        """
        删除customData 数据 以及对应类型中的数据
        :param filename:
        :return:
        """
        file_type: dict = self.customData.pop(filename)
        if file_type:
            logger.debug(f'_remove_file_type ===> {file_type}')
            child_type = file_type.get('child_type')
            father_type = file_type.get("father_type")
            _list: list = self.get_type_data(child_type, father_type)
            for i, value in enumerate(_list[:]):
                if value[0] == filename:
                    _list.pop(i)
                    break
            father_type = file_type.get("father_type")
            if father_type:
                _list: list = self.get_type_data(father_type=father_type)
                for i, value in enumerate(_list[:]):
                    if value[0] == filename:
                        _list.pop(i)
                        break

    def insertRow(self, info: dict, parent=QModelIndex()):
        data = info.get('data')
        file_type: dict = info.get('file_type')
        child_type = file_type.get('child_type')
        father_type = file_type.get('father_type')
        need_insert = self.need_insert(child_type, father_type)
        logger.debug(f'insertRow ===>{need_insert}')
        tmp = self._insertData(self.get_type_data(father_type=father_type), data)
        print(self.get_type_data(father_type=father_type))
        self.set_type_data(tmp, father_type=father_type)
        if child_type:
            tmp1 = self._insertData(self.get_type_data(child_type, father_type), data)
            self.set_type_data(tmp1, child_type, father_type)
        self._data = self._insertData(self._data, data)
        self.customData[data[0]] = file_type
        logger.debug(f'self.search_type: {self.search_type}, self.father_type: {self.father_type}'
                     f'child_type: {child_type}, father_type: {father_type}')
        if need_insert:
            # 一级二级都没有
            # 一级分类相等
            # 二级分类要么没有要么相等
            self.beginInsertRows(parent, self.rowCount(), self.rowCount())
            if not self.search_type and not self.father_type:
                self._search_result = self._data[:]
            elif self.search_type == '':
                self._search_result = self.get_type_data(father_type=father_type)[:]
            elif child_type == self.search_type:
                self._search_result = self.get_type_data(child_type, father_type)[:]
            else:
                raise TypeError(
                    f'出现意外情况, 插入目标分类{father_type}->{child_type}, 当前类型:{self.father_type} -> {self.search_type}')
            self.endInsertRows()

    def need_insert(self, child_type, father_type) -> bool:
        # 一级二级都没有 直接插入
        if not self.father_type and not self.search_type:
            return True
        # 一级目录必定有
        # 一级不相等 不插入
        if self.father_type != father_type:
            return False
        # 二级目录不存在 或者 二级目录和目标的二级目录相等
        if not self.search_type or self.search_type == child_type:
            return True
        return False

    def _insertData(self, data: list, insert_data: list):
        index = -1
        data = data[:]
        for i, value in enumerate(data):
            if value[0] == insert_data[0]:
                index = i
                break
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

    def flags(self, index: QModelIndex):
        if index.column() == 1:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
