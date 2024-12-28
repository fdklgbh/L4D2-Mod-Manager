# -*- coding: utf-8 -*-
# @Time: 2023/12/31
# @Author: Administrator
# @File: tableModules.py
from typing import Union, List
from pathlib import Path
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal, QThreadPool
from PyQt5.QtWidgets import QWidget
from qfluentwidgets import InfoBar, InfoBarPosition

from common import logger
from common.Bus import signalBus
from common.config import vpkConfig, l4d2Config
from common.conf import NEED_DATA, ModType
from common.messagebox import ReWriteMessageBox
from common.read_vpk import open_vpk


class TableModel(QAbstractTableModel):
    vpkInfoHideSignal = pyqtSignal()

    def __init__(self, parent: QWidget, headers, folder_path: Path):
        super().__init__()
        self._headers = headers
        self._search_result = []
        self.folder_path = folder_path
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
        self._parent: QWidget = parent

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
        def change_customTitle(change_data=''):
            self._search_result[row][-1] = change_data
            vpkConfig.update_config(title, {"customTitle": change_data})

        logger.info(f'修改为:{[value]}, {index.isValid()}')
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            column = index.column()
            if column != 1:
                return False
            data = self._search_result[row]
            title = data[0]
            customTitle = compare = data[-1]
            originalTitle = data[column]
            if not compare:
                # 原始标题
                compare = data[column]
            if compare != value or value == customTitle:
                if not l4d2Config.vpk_application_is_exsits:
                    # 没有vpk.exe
                    if not value:
                        if customTitle:
                            change_customTitle()
                            self.dataChanged.emit(index, index, [Qt.DisplayRole])
                            logger.info(f'清除 {title} 自定义标题')
                            return True
                        logger.info('不做任何修改')
                        return False
                    else:
                        if customTitle:
                            if value == originalTitle:
                                logger.info(f'{title} 和原本标题一致, 删除自定义标题')
                                change_customTitle()
                                self.dataChanged.emit(index, index, [Qt.DisplayRole])
                                return True
                            if value == customTitle:
                                logger.info(f'{title} 修改的标题和自定义标题一样,不做任何修改')
                                return False
                        change_customTitle(value)
                        logger.info(f'mod: {title} 设置自定义标题<{value}>')
                        self.dataChanged.emit(index, index, [Qt.DisplayRole])
                        return True
                logger.info('尝试是否能正常打开vpk')
                file_path = self.folder_path / f'{title}.vpk'
                res = open_vpk(file_path)
                if res in [None, False]:
                    InfoBar.warning(
                        title='',
                        content=f'mod文件打开失败,不写入文件,存入自定义标题',
                        orient=Qt.Horizontal,
                        isClosable=False,
                        position=InfoBarPosition.TOP,
                        parent=self._parent.window()
                    )
                    self._search_result[row][-1] = value
                    title = self.get_row_title(row)
                    logger.info(f'文件:{title}标题修改为 <{value}>,原始标题为 <{self._search_result[row][column]}> ')
                    vpkConfig.update_config(title, {"customTitle": value})
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    return True
                del res
                new_title = value
                if not value:
                    # 输入内容为空
                    if customTitle:
                        # 能打开,有自定义标题,则保存到vpk的addoninfo中
                        logger.info(f'mod:{title} 自定义标题尝试存储到vpk中')
                        new_title = customTitle
                        change_customTitle()
                    else:
                        # 能打开,没有自定义标题
                        logger.info(f'mod:{title} 修改为空,无自定义标题,显示原始标题')
                        return False
                else:
                    if value == originalTitle:
                        logger.info(f'mod:{title} 取消自定义标题')
                        change_customTitle()
                        self.dataChanged.emit(index, index, [Qt.DisplayRole])
                        return True
                    elif value == customTitle:
                        logger.info(f'mod:{title} 自定义标题尝试存储到vpk中')
                        change_customTitle()
                    else:
                        logger.info(f'mod:{title} 修改标题为<{value}>并存储到vpk中')
                        if customTitle:
                            change_customTitle()
                box = ReWriteMessageBox(self._parent.window(), file_path, new_title)
                if not box.exec_():
                    show = f'mod:{title} 标题修改失败,存储为自定义标题'
                    logger.error(show)
                    InfoBar.warning(
                        title='',
                        content=show,
                        orient=Qt.Horizontal,
                        isClosable=False,
                        position=InfoBarPosition.TOP,
                        parent=self._parent.window()
                    )
                    change_customTitle(new_title)
                    self.dataChanged.emit(index, index, [Qt.DisplayRole])
                    return True
                logger.info(f'{title} vpk文件写入成功, 标题修改为<{new_title}>')
                self._search_result[row][1] = new_title
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

    @staticmethod
    def generate_row_data(data: dict, title=None) -> list:
        if title is None:
            title = data.get('filePath').stem
        add_data = [title]
        for i in NEED_DATA:
            add_data.append(data.get('file_info', {}).get(i, ''))
        # 自定义标题
        add_data.append(data.get('customTitle', ''))
        return add_data

    def addRow(self, data: dict):
        title = data.get('filePath').stem
        add_data = self.generate_row_data(data, title)
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

    def refresh_row(self, data_info: dict, title: str = None):
        """
        刷新单行数据
        :param data_info: 刷新数据 read_addons_txt 返回数据
        :param title:
        :return:
        """
        data: list = self.generate_row_data(data_info, title)
        if title is None:
            title = data[0]
        _data_index = self._find_index(self._data, title)
        if _data_index:
            self._data[_data_index] = data
        data_type = self.customData[title]
        father_type = data_type.get('father_type', "其他")
        child_type = data_type.get('child_type', "")
        father_type_index = self._find_index(self.get_type_data(father_type=father_type), title)
        if father_type_index:
            self.get_type_data(father_type=father_type)[father_type_index] = data
        if child_type:
            child_type_index = self._find_index(self.get_type_data(child_type, father_type), title)
            if child_type_index:
                self.get_type_data(child_type, father_type)[child_type_index] = data
        _search_index = self._find_index(self._search_result, title)
        self._search_result[_search_index] = data
        left = self.index(_search_index, 0)
        right = self.index(_search_index, self.columnCount() - 1)
        self.dataChanged.emit(left, right)

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
    def _find_index(data, file_name):
        """
        数据列表找到标题对应的下标
        :param data:
        :param file_name:
        :return:
        """
        for index, file_data in enumerate(data):
            if file_name == file_data[0]:
                return index

    def findSearchIndex(self, filename):
        return self._find_index(self._search_result, filename)

    def flags(self, index: QModelIndex):
        if index.column() == 1:
            return Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled
