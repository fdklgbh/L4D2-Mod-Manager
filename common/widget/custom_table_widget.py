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
from common.config import l4d2Config
from common.messagebox import ChangeTypeMessageBox
from common.module.modules import TableModel
from qfluentwidgets import FluentIcon as FIF

from common.myIcon import MyIcon
from common.conf import IS_DEV, WORKSPACE


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
                parent=self.window()
            )
            return
        # 当前选中的
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
        if item.column() == 1:
            edit = Action(FIF.EDIT, self.tr('编辑'))
            menu.addAction(edit)
            edit.triggered.connect(lambda: self.edit(item))
        open_file = Action(FIF.FOLDER, self.tr('打开文件所在文件夹'))
        open_gcf = Action(MyIcon.GCF, self.tr('打开GCFSpace'))
        if not l4d2Config.gcfspace_path:
            open_gcf.setVisible(False)
        else:
            open_gcf.setVisible(True)
        # 选中mod的分类数据 {'child_type': 'other', 'father_type': None}
        userData: dict = item.data(Qt.UserRole + 1)
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
        select_rows = set()
        for i in self.selectionModel().selectedRows():
            logger.debug(f'{i.row()} ===> {i.data()}')
            select_rows.add(i)
        is_more = len(select_rows) > 1
        logger.debug(f"{filename}: {userData}")
        type_ = userData['child_type'] if userData['child_type'] else userData["father_type"]
        type_action = Action(FIF.FLAG, f"类型： {type_}" if not is_more else "修改分类", self)
        menu.addActions([open_file, open_gcf, type_action])
        menu.addSeparator()
        if is_more:
            more_text = '多个'
        else:
            more_text = ''

        if l4d2Config.is_workshop(parent_folder_path):
            move_to_addons = Action(FIF.MOVE, self.tr(f'移动{more_text}到Addons'))
            menu.addAction(move_to_addons)
            move_to_addons.triggered.connect(lambda x: self.move_mod(l4d2Config.addons_path, select_rows))
        move_more = Action(icon, self.tr(f'{text}{more_text}mod'))
        menu.addAction(move_more)

        if filename.isdigit():
            open_url_action = Action(FIF.LINK, self.tr('打开steam链接'))
            menu.addAction(open_url_action)
            open_url_action.triggered.connect(lambda x: QDesktopServices.openUrl(QUrl(
                f'https://steamcommunity.com/sharedfiles/filedetails/?id={filename}')))
        if IS_DEV:
            dev_action = Action(text='导出文件结构到dev文件下')
            menu.addAction(dev_action)
            dev_action.triggered.connect(lambda x: self.dev_action(parent_folder_path, select_rows))

        open_file.triggered.connect(lambda x: self.openFolderSignal.emit(filename))
        open_gcf.triggered.connect(lambda x: self.openGCFSpaceSignal.emit(filename))
        # userData: {'child_type': '声音', 'father_type': '杂项'}
        logger.debug(f'userData: {userData}')
        # 当多选的时候修改类型,批量修改
        select_data = [data.data(Qt.UserRole + 2) for data in select_rows]
        type_action.triggered.connect(lambda x: self.show_change_type(select_data, **userData, more=is_more))
        move_more.triggered.connect(lambda x: self.move_mod(target_path, select_rows))
        menu.closedSignal.connect(menu.deleteLater)
        menu.exec(a0.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def dev_action(self, folder_path, select_rows: Set[QModelIndex]):
        from common.read_vpk import open_vpk
        print(f'[DEV]目录:{folder_path}')
        print('[DEV]select_titles: ', *[i.data(Qt.UserRole + 2)[0] for i in select_rows])
        dev_folder = WORKSPACE / 'dev'
        dev_folder.mkdir(parents=True, exist_ok=True)
        for i in select_rows:
            title = i.data(Qt.UserRole + 2)[0]
            vpk_file = folder_path / f'{title}.vpk'
            vpk = open_vpk(vpk_file)
            if not vpk:
                logger.debug(f'[DEV]{vpk_file}文件打开失败,无法导出vpk结构')
                continue
            txt_file = dev_folder / f'{title}.txt'
            try:
                with open(txt_file, 'w', encoding='utf8') as f:
                    for vpk_file_path in vpk:
                        f.write(vpk_file_path + '\n')
                        f.flush()
            except Exception as e:
                logger.warn('[DEV]出现错误')
                logger.exception(e)
            else:
                logger.debug(f'[DEV]文件结构导出成功->{txt_file}')

    def move_mod(self, target_path, data_set: Set[QModelIndex]):
        list_rows = list(data_set)
        list_rows.sort(key=lambda x: x.row())
        for i in list_rows[::-1]:
            self.modeEnableSignal.emit(target_path, i.row(), i.data())

    def show_change_type(self, data, child_type, father_type, more=False):
        """
        显示切换类型窗口
        :param more:
        :param data:
        :param child_type:
        :param father_type:
        :return:
        """
        logger.debug(data)
        w = ChangeTypeMessageBox(self.window(), [data, child_type, father_type], more=more)
        w.exec_()
        self.clearSelection()

    def mouseDoubleClickEvent(self, e):
        module_index = self.indexAt(e.pos())
        self.doubleClickedSignal.emit(module_index)
