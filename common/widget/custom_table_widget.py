# -*- coding: utf-8 -*-
# @Time: 2023/12/29
# @Author: Administrator
# @File: custom_table_widget.py
from pathlib import Path

from PyQt5.QtCore import QModelIndex, pyqtSignal, Qt, QUrl
from PyQt5.QtGui import QContextMenuEvent, QDesktopServices
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
        edit = Action(FIF.EDIT, self.tr('编辑'))
        edit.setVisible(False)
        open_file = Action(FIF.FOLDER, self.tr('打开文件所在文件夹'))
        open_gcf = Action(MyIcon.GCF, text=self.tr('打开GCFSpace'))
        if not l4d2Config.gcfspace_path:
            open_gcf.setVisible(False)
        else:
            open_gcf.setVisible(True)
        if item.column() != 0:
            menu.addAction(edit)
        menu.addActions([open_file, open_gcf])
        menu.addSeparator()
        # key_menu = RoundMenu('分类', menu)
        # group = QActionGroup(self)
        # group.setExclusive(True)
        # father_type: str = userData.get('father_type')
        # check_type = userData.get('check_type')
        # logger.debug(userData)
        # for i in ModType.type_key():
        #     if isinstance(i, dict):
        #         for key, value in i.items():
        #             key_action = RoundMenu(key, self)
        #             key_menu.addMenu(key_action)
        #             for j in value:
        #                 if father_type and key == ModType.key_to_value(father_type) and j == check_type:
        #                     tmp_action = Action(FIF.ACCEPT_MEDIUM, j.title())
        #                 else:
        #                     tmp_action = Action(j.title())
        #                 group.addAction(tmp_action)
        #                 key_action.addAction(tmp_action)
        #     else:
        #         tmp_action = Action(i)
        #         if father_type is None:
        #             if ModType.key_to_value(check_type) == i:
        #                 tmp_action.setIcon(FIF.ACCEPT_MEDIUM)
        #         group.addAction(tmp_action)
        #         key_menu.addAction(tmp_action)
        #
        # menu.addMenu(key_menu)
        userData: dict = item.data(Qt.UserRole + 1)
        logger.debug(userData)
        type_ = userData['check_type'] if userData['father_type'] else ModType.key_to_value(userData['check_type'])
        type_action = Action(FIF.FLAG, f"类型： {type_.title()}", self)
        menu.addAction(type_action)
        # change_type = Action(FIF.EDIT, '修改Mod分类', self)
        # menu.addAction(change_type)
        parent_folder_path = self.parent_obj.folder_path
        if not l4d2Config.is_disable_mod_path(parent_folder_path):
            move = Action(FIF.CANCEL_MEDIUM, self.tr('禁用mode'))
            target_path = l4d2Config.disable_mod_path
        else:
            move = Action(FIF.ACCEPT_MEDIUM, self.tr('启用mode'))
            target_path = l4d2Config.addons_path
        menu.addAction(move)
        if l4d2Config.is_workshop(parent_folder_path):
            move_to_addons = Action(FIF.MOVE, self.tr('移动到Addons'))
            menu.addAction(move_to_addons)
            move_to_addons.triggered.connect(
                lambda x: self.modeEnableSignal.emit(l4d2Config.addons_path, row, filename))
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

    def show_change_type(self, data, check_type, father_type):
        logger.debug(data)
        # self.parent().parent().parent().parent().parent().parent()
        w = ChangeTypeMessageBox(self.parent().parent().parent().parent().parent().parent(),
                                 [data, check_type, father_type])

        print(w.exec_())

    def mouseDoubleClickEvent(self, e):
        module_index = self.indexAt(e.pos())
        # print(module_index.flags() & Qt.ItemIsEditable == Qt.ItemIsEditable)
        self.doubleClickedSignal.emit(module_index)


