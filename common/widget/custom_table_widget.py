# -*- coding: utf-8 -*-
# @Time: 2023/12/29
# @Author: Administrator
# @File: custom_table_widget.py
from pathlib import Path
from typing import Set

from PyQt5.QtCore import QModelIndex, pyqtSignal, Qt, QUrl
from PyQt5.QtGui import QContextMenuEvent, QDesktopServices
from PyQt5.QtWidgets import QSplitter
from qfluentwidgets import TableView, RoundMenu, MenuAnimationType, Action, InfoBar, InfoBarPosition

from common import logger
from common.config.main_config import l4d2Config
from common.messagebox import ChangeTypeMessageBox
from common.module.modules import TableModel
from qfluentwidgets import FluentIcon as FIF

from common.myIcon import MyIcon
from common.conf import ModType


class CustomTableView(TableView):
    openFolderSignal = pyqtSignal(str)
    openGCFSpaceSignal = pyqtSignal(str)
    modeEnableSignal = pyqtSignal(Path, int, str)
    doubleClickedSignal = pyqtSignal(QModelIndex)

    def __init__(self, parent=None):
        super(CustomTableView, self).__init__(parent)
        self.parent_obj = parent
        self.finished = False

    def contextMenuEvent(self, a0: QContextMenuEvent):
        if self.finished is False:
            InfoBar.info(
                title='',
                content="请等待mod加载完成",
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP,
                duration=1000,
                parent=self.parent_obj.parent().parent()
            )
            return
        item = self.indexAt(a0.pos())
        if not item.isValid():
            return
        row = item.row()
        logger.debug(item.column())
        election_module = self.selectionModel()
        select_rows = set()
        table_module: TableModel = self.model()
        filename: str = table_module.data(item.sibling(row, 0))
        for index in election_module.selectedRows():
            # selectedRows 返回选中行的第一列 QModelIndex
            # selectedIndexes 返回所有行，所有列选中的 QModelIndex
            index: QModelIndex
            select_rows.add(index.row())
        if row not in select_rows:
            self.selectRow(item.row())
        menu = RoundMenu(parent=self)

        # if item.column() == 1:
        #     edit = Action(FIF.EDIT, self.tr('编辑'))
        #     menu.addAction(edit)
        #     edit.triggered.connect(lambda: self.edit(item))
        open_file = Action(FIF.FOLDER, self.tr('打开文件所在文件夹'))
        open_gcf = Action(MyIcon.GCF, text=self.tr('打开GCFSpace'))
        if not l4d2Config.gcfspace_path:
            open_gcf.setVisible(False)
        else:
            open_gcf.setVisible(True)
        userData: dict = item.data(Qt.UserRole + 1)
        logger.debug(f"{filename}: {userData}")
        type_ = userData['check_type'] if userData['father_type'] else ModType.key_to_value(userData['check_type'])
        type_action = Action(FIF.FLAG, f"类型： {type_.title()}", self)
        menu.addActions([open_file, open_gcf, type_action])
        menu.addSeparator()
        parent = self.parent()
        if isinstance(self.parent_obj, QSplitter):
            parent = self.parent_obj.parent()
        parent_folder_path = parent.folder_path
        is_disable_path = l4d2Config.is_disable_mod_path(parent_folder_path)
        if not is_disable_path:
            target_path = l4d2Config.disable_mod_path
            text = '禁用'
            icon = FIF.CANCEL_MEDIUM
        else:
            target_path = l4d2Config.addons_path
            text = '启用'
            icon = FIF.ACCEPT_MEDIUM
        move = Action(icon, self.tr(f"{text}当前mod"))
        select_rows = set()
        for i in self.selectionModel().selectedRows():
            logger.debug(f'{i.row()} ===> {i.data()}')
            select_rows.add(i)
        menu.addAction(move)
        if len(select_rows) > 1:
            move_more = Action(icon, self.tr(f'{text}多个mod'))
            menu.addAction(move_more)
            move_more.triggered.connect(lambda x: self.move_more_mod(target_path, select_rows))
        if l4d2Config.is_workshop(parent_folder_path):
            move_to_addons = Action(FIF.MOVE, self.tr('移动到Addons'))
            menu.addAction(move_to_addons)
            move_to_addons.triggered.connect(
                lambda x: self.modeEnableSignal.emit(l4d2Config.addons_path, row, filename))
            if len(select_rows) > 1:
                move_more_to_addons = Action(FIF.MOVE, self.tr('移动多个到Addons'))
                menu.addAction(move_more_to_addons)
                move_more_to_addons.triggered.connect(lambda x: self.move_more_mod(l4d2Config.addons_path, select_rows))
        if filename.isdigit():
            open_url_action = Action(FIF.LINK, self.tr('打开steam链接'))
            menu.addAction(open_url_action)
            open_url_action.triggered.connect(lambda x: QDesktopServices.openUrl(QUrl(
                f'https://steamcommunity.com/sharedfiles/filedetails/?id={filename}')))
        open_file.triggered.connect(lambda x: self.openFolderSignal.emit(filename))
        open_gcf.triggered.connect(lambda x: self.openGCFSpaceSignal.emit(filename))
        type_action.triggered.connect(lambda x: self.show_change_type(item.data(Qt.UserRole + 2), **userData))
        move.triggered.connect(lambda x: self.modeEnableSignal.emit(target_path, row, filename))
        menu.closedSignal.connect(menu.deleteLater)
        menu.exec(a0.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def move_more_mod(self, target_path, data_set: Set[QModelIndex]):
        list_rows = list(data_set)
        list_rows.sort(key=lambda x: x.row())
        for i in list_rows[::-1]:
            self.modeEnableSignal.emit(target_path, i.row(), i.data())

    def show_change_type(self, data, check_type, father_type):
        """
        显示切换类型窗口
        :param data:
        :param check_type:
        :param father_type:
        :return:
        """
        logger.debug(data)
        # self.parent().parent().parent().parent().parent().parent()
        w = ChangeTypeMessageBox(self.parent().parent().parent().parent().parent().parent(),
                                 [data, check_type, father_type])

        print(w.exec_())

    def mouseDoubleClickEvent(self, e):
        module_index = self.indexAt(e.pos())
        self.doubleClickedSignal.emit(module_index)
