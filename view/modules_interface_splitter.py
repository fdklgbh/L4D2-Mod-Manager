# -*- coding: utf-8 -*-
# @Time: 2023/12/26
# @Author: Administrator
# @File: modules_interface.py
import os
from pathlib import Path
from typing import List
from PyQt5.QtCore import Qt, QModelIndex, QByteArray, QThreadPool, QPoint
from PyQt5.QtGui import QPixmap, QImage, QKeyEvent
from PyQt5.QtWidgets import QHeaderView, QApplication, QWidget
from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition, StateToolTip, ToolTipFilter, \
    ToolTipPosition, Dialog, MessageBox, Action, RoundMenu

from common import logger
from common.Bus import signalBus
from common.config import l4d2Config
from common.module.modules import TableModel
from common.read_vpk import read_addons_txt, get_vpk_addon_image_data
from common.thread import PrePareDataThread, OpenGCFScape
from glob import glob
from qfluentPackage.widget import CSegmentedWidget

from common.conf import ModType
from ui.modules_page_splitter import Ui_Frame


# todo
#  移动文件的时候 加一个进度条在当前窗口顶部
#  切换到类型后,数据没有排序


class ModuleStacked(QWidget, Ui_Frame):
    def __init__(self, folder_path: Path, parent=None):
        super().__init__(parent=parent)
        self.hide_addons_info = False
        self.setupUi(self)
        self.progress_num = 0
        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.folder_path = folder_path
        self.mode_total = self.get_path_vpk_file_number(self.folder_path)
        self.stateTooltip: StateToolTip = None
        self.mode = TableModel(['文件名', '标题', '作者', '描述', '标语'])
        self.per_data_thread = PrePareDataThread(self.mode, self.folder_path)
        self.onThreadSignalToSlot()
        self.set_table_view()
        self.refresh_btn.setToolTip(self.tr('重新加载VPK文件'))
        self.refresh_btn.installEventFilter(ToolTipFilter(self.refresh_btn, 300, ToolTipPosition.BOTTOM))
        self.connectSignalToSlot()
        self.file_pic.setScaledContents(True)
        self.pix: QPixmap = None
        self.original_pix: QPixmap = None
        # self.tableView.horizontalHeader().setSortIndicatorShown(False)
        self.thread_pool = QThreadPool.globalInstance()
        self.splitter.setStyleSheet("QSplitter::handle { background: transparent;}")
        self.hide_vkp_info()

        # self.splitter.setStretchFactor(0, 7)
        # self.splitter.setStretchFactor(1, 3)

    def hide_vkp_info(self):
        self.resize_splitter()

    def show_addon_info(self, current: QModelIndex, previous: QModelIndex):
        self.vkp_info.show()
        self.file_pic.clear()
        if current.row() < 0:
            return
        last_row = current.row()
        file_title = self.mode.get_row_title(last_row)
        pic = self.folder_path / f'{file_title}.jpg'
        layout_width = int(self.width() * 0.3)
        pic_success = False
        if pic.exists():
            self.original_pix = QPixmap(pic.__str__())
            if not self.original_pix.isNull():
                self.pix = self.original_pix
                pic_success = True
        else:
            content = get_vpk_addon_image_data(self.folder_path / f'{file_title}.vpk')
            if isinstance(content, dict):
                w = MessageBox(
                    content['title'], content['content'], parent=self.window()
                )
                w.cancelButton.setText('退出程序')
                w.yesButton.setText('确定')
                w.show()
                if not w.exec_():
                    self.window().close()
                self.tableView.clearSelection()
                self.mode.removeRow(last_row, file_title)
                logger.debug('删除数据行')
                return
            if content:
                try:
                    qbytearray = QByteArray(content)
                    image = QImage.fromData(qbytearray)
                    if not image.isNull():
                        self.original_pix = QPixmap.fromImage(image)
                        pic_success = True
                except Exception as e:
                    logger.error(e)
        addons_txt = read_addons_txt(self.folder_path / f'{file_title}.vpk')
        has_content = bool(addons_txt.get('content'))
        if not has_content and pic_success is False:
            self.hide_vkp_info()
            self.pix = None
            self.original_pix = None
            return
        else:
            self.resize_splitter(layout_width)
        if pic_success:
            self.pix = self.original_pix.scaledToWidth(layout_width, mode=Qt.SmoothTransformation)
            # self.pix = self.pix.scaled(layout_width, layout_width, aspectRatioMode=Qt.KeepAspectRatio,
            #                            transformMode=Qt.SmoothTransformation)
            self.pix.setDevicePixelRatio(2)
            self.file_pic.setPixmap(self.pix)
        else:
            self.pix = None
            self.original_pix = None
        self.file_pic.setVisible(pic_success)
        if has_content:
            self.addons_info.setPlainText(addons_txt['content'])
            self.addons_info.show()
        else:
            self.addons_info.setVisible(False)
        self.vkp_info.setMaximumWidth(layout_width)

    def resize_splitter(self, vpk_info_size=0):
        sizes = self.splitter.sizes()
        sizes[1] = vpk_info_size
        handle_width = 6
        if vpk_info_size == 0:
            handle_width = 0
        self.splitter.setHandleWidth(handle_width)
        self.splitter.setSizes(sizes)

    def on_splitter_moved(self, *args):
        sizes = self.splitter.sizes()
        if sizes[1] == 0:
            self.splitter.setHandleWidth(0)
        else:
            self.splitter.setHandleWidth(6)

    def show_type_menu(self, *args):
        type_key = ModType.type_key()
        menu = RoundMenu(self)
        menu.addAction(Action(text=f'全部({self.mode.all_data_num})'))
        for i in type_key:
            if isinstance(i, dict):
                for key, value in i.items():
                    num_str = f"({self.mode.get_type_num(key)})"
                    key_action = RoundMenu(f"{key}{num_str}", parent=menu)
                    menu.addMenu(key_action)
                    key_action.addAction(Action(text=f'全部{num_str}', parent=key_action))
                    for j in value:
                        j: str
                        key_action.addAction(
                            Action(text=f"{j.title()}({len(getattr(self.mode, f'_{j}'))})", parent=key_action))
            else:
                menu.addAction(Action(f"{i}({self.mode.get_type_num(i)})"))
        position = self.sender().mapToGlobal(QPoint(-10, 30))
        menu.popup(position)
        menu.triggered.connect(self.type_menu_selection)

    def type_menu_selection(self, action: Action):
        # action.text()拆分数据
        search_type = btn_text = action.text().lower().split('(')[0]
        father_menu = ''
        if action.parentWidget():
            father_title = action.parentWidget().title().split('(')[0]
            logger.debug(f'father_title: {father_title}')
            father_menu = father_title
            if btn_text == '全部':
                search_type = ModType.value_to_key(father_title)
                btn_text = father_title
        else:
            search_type = ModType.value_to_key(btn_text)
        self.type_btn.setText(btn_text.title())
        self.mode.search_type = search_type
        self.mode.father_type = father_menu
        logger.debug(f'search type: {search_type}, father_type: {father_menu}')
        self.mode.changeType(search_type)
        self.restartPage(True)

    def set_table_view(self):
        # 边框可见
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        # 自动换行
        self.tableView.setWordWrap(True)
        self.tableView.setModel(self.mode)
        self.per_data_thread.start()
        # 表头隐藏
        self.tableView.verticalHeader().hide()
        # 按照内容自适应宽度大小
        self.tableView.resizeColumnsToContents()
        # 水平表头设置为自动拉伸
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 排序
        self.tableView.setSortingEnabled(True)

    def copy_data(self, copy_data, content=None):
        clipboard = QApplication.clipboard()
        clipboard.setText(copy_data)
        if content is None:
            content = f"{copy_data} 已经复制到剪贴板"
        else:
            content += ' 已经复制到剪贴板'
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title='复制成功',
            content=content,
            orient=Qt.Vertical,  # vertical layout
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self
        )
        w.show()

    def connectSignalToSlot(self):
        self.tableView.horizontalHeader().sectionClicked.connect(self.table_sort_changed)
        # signalBus.tableItemChanged.connect(self.item_text_changed)
        self.tableView.selectionModel().currentRowChanged.connect(self.show_addon_info)
        self.tableView.openGCFSpaceSignal.connect(self.show_gcfspace)
        self.tableView.openFolderSignal.connect(self.show_vpk_file)
        self.tableView.doubleClickedSignal.connect(self.onDoubleClicked)
        self.refresh_btn.clicked.connect(lambda x: self.refresh())
        self.tableView.modeEnableSignal.connect(self.move_file)
        signalBus.windowSizeChanged.connect(self.mainWindowResize)
        signalBus.modulePathChanged.connect(self.insertMod)
        signalBus.pressKey.connect(self.pressKey)
        self.mode.vpkInfoHideSignal.connect(self.hide_vkp_info)

    def pressKey(self, a0: QKeyEvent):
        if self.isVisible():
            if a0.modifiers() == Qt.ControlModifier and a0.key() == Qt.Key_F:
                self.search_edit.setFocus()

    def insertMod(self, folder_path: Path, data: list, file_type):
        # 移动文件后,对应表格插入数据
        if folder_path == self.folder_path:
            self.search_edit.setText('')
            info = {
                'data': data,
                'file_type': file_type,
                'need_insert': self.mode.need_insert(**file_type)
            }
            self.mode.insertRow(info)
            self.hide_vkp_info()
            self.tableView.setCurrentIndex(QModelIndex())

    def move_file(self, target_path: Path, row, filename: str):
        data = self.mode.get_row_data(row)
        if not l4d2Config.debug:
            self.move_module(filename, target_path, data, row)
        else:
            # debug
            file_type = self.mode.customData[filename]
            logger.debug(f'move_file: {file_type}')
            signalBus.modulePathChanged.emit(target_path, data, file_type)
            self.mode.removeRow(row, filename)
            self.restartPage()
        self.tableView.setCurrentIndex(QModelIndex())

    def move_module(self, filename, target_path: Path, data: list, row):
        """
        移动mod
        :param filename: 文件名称
        :param target_path: 目标位置
        :param data: 数据
        :param row: 行数
        :return:
        """
        cover = True
        target_exists = False
        full_file_name = filename + '.vpk'
        original_file = self.folder_path / full_file_name
        target_file = target_path / full_file_name
        if target_file.exists():
            w = Dialog('警告', f'文件夹中已存在{filename},是否覆盖', self)
            w.yesButton.setText('覆盖')
            w.cancelButton.setText('取消')
            w.setTitleBarVisible(False)
            if not w.exec():
                cover = False
            logger.warning('文件已存在了')
            target_exists = True
        if not original_file.exists():
            self.file_not_exists_bar()
            return
        if cover:
            try:
                if target_exists:
                    original_file.replace(target_file)
                else:
                    original_file.rename(target_file)
                pic_name = filename + '.jpg'
                pic_path = self.folder_path / pic_name
                target_pic = target_path / pic_name
                if pic_path.exists():
                    if target_pic.exists():
                        pic_path.replace(target_pic)
                    else:
                        pic_path.rename(target_pic)
            except PermissionError as e:
                if '另一个程序正在使用此文件，进程无法访问。' in str(e):
                    logger.warning('当前文件被占用')
                    InfoBar.error(
                        title='',
                        content='当前文件被占用',
                        orient=Qt.Horizontal,
                        isClosable=False,
                        position=InfoBarPosition.TOP,
                        parent=self.window()
                    )
                    return
                logger.debug(e)
                self.file_not_exists_bar()
                return
            else:
                signalBus.modulePathChanged.emit(target_path, data, self.mode.customData[filename])
            self.mode.removeRow(row, filename)
            self.restartPage(clear_search_text=False if self.mode.rowCount() else True)

    def restartPage(self, restart_sort=False, clear_search_text=True):
        if restart_sort:
            self.tableView.horizontalHeader().setSortIndicator(0, Qt.DescendingOrder)
            self.tableView.horizontalHeader().setSortIndicator(-1, Qt.DescendingOrder)
        if clear_search_text:
            self.search_edit.clear()
        self.table_sort_changed()

    def file_not_exists_bar(self):
        InfoBar.error(
            title='',
            content='文件不存在，请检查',
            orient=Qt.Horizontal,
            isClosable=False,
            position=InfoBarPosition.TOP,
            parent=self.window()
        )

    def refresh(self):
        self.mode_total = self.get_path_vpk_file_number(self.folder_path)
        self.tableView.finished = False
        self.type_btn.setText('全部')
        self.restartPage(True)
        self.mode.beginResetModel()
        self.mode.refresh()
        self.per_data_thread.start()
        self.mode.endResetModel()

    def show_gcfspace(self, filename):
        file_path = self.folder_path / f'{filename}.vpk'
        thread = OpenGCFScape()
        thread.vpk_file = file_path
        self.thread_pool.start(thread)

    def show_vpk_file(self, filename):
        file_path = self.folder_path / f'{filename}.vpk'
        os.system(f'explorer /select,"{file_path}"')

    def onThreadSignalToSlot(self):
        self.per_data_thread.started.connect(self.mod_load_started)
        self.per_data_thread.finished.connect(self.mod_load_finished)
        self.per_data_thread.progressSignal.connect(self.mod_load_progress)
        self.per_data_thread.addRowSignal.connect(self.mode.addRow)

    def mod_load_started(self):
        self.setDisabled(True)
        self.stateTooltip = StateToolTip('正在加载vpk信息',
                                         f'{self.progress_num}/{self.mode_total}', self)
        self.stateTooltip.move(self.width() - self.stateTooltip.width(), 10)
        self.stateTooltip.show()

    def mod_load_progress(self, file_name: str):
        self.progress_num += 1
        self.stateTooltip.setContent(f'{self.progress_num}/{self.mode_total} {file_name}')

    def mod_load_finished(self):
        self.stateTooltip.setContent('全部加载完成了')
        self.stateTooltip.setState(True)
        self.stateTooltip = None
        self.progress_num = 0
        self.tableView.finished = True
        # self.setEnabled(True)
        self.setDisabled(False)
        self.mode.sortData()

    def table_sort_changed(self, *args):
        logger.debug('隐藏vpk')
        self.tableView.clearSelection()
        self.hide_vkp_info()

    def onDoubleClicked(self, e: QModelIndex):
        col = e.column()
        if col == 0:
            self.copy_data(e.data())
        else:
            title = self.mode.get_header_title(col)
            file_name = self.mode.get_row_title(e.row())
            self.copy_data(e.data(), f'{file_name} {title}')

    @staticmethod
    def get_path_vpk_file_number(path: Path):
        vpk_file = path / '*.vpk'
        res = glob(vpk_file.__str__())
        num = 0
        for i in res:
            if Path(i).is_file():
                num += 1
        logger.debug(f'get_path_vpk_file_number: {num}')
        return num

    def mainWindowResize(self, a0):
        new_size = a0.size()
        # new_width = int(new_size.width() * 0.3)
        new_width = int(self.width() * 0.3)
        if self.stateTooltip:
            try:
                self.stateTooltip.move(self.width() - self.stateTooltip.width(), 10)
            except Exception as e:
                logger.warning(e)
        if self.addons_info.isVisible() or self.file_pic.isEnabled():
            if self.file_pic.isEnabled() and self.original_pix:
                self.file_pic.clear()
                self.pix = self.original_pix.scaledToWidth(new_width, mode=Qt.SmoothTransformation)
                self.file_pic.setPixmap(self.pix)
        self.vkp_info.setMaximumWidth(new_width)

    def perform_search(self, text: str = ''):
        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        # 恢复表列头的初始升序/降序状态
        self.tableView.clearSelection()
        self.mode.setSearchText(text)
        self.hide_vkp_info()


class ModulesInterfaceSplitter(CSegmentedWidget):
    def __init__(self, folder_path: List[Path], parent=None):
        super().__init__(parent=parent)
        if folder_path:
            for path in folder_path:
                self.module_interface = ModuleStacked(path)
                text = path.name.title()
                self.addSubInterface(self.module_interface, text, path)
                if l4d2Config.is_addons(path):
                    self.setDefaultCurrent(self.module_interface)
        if self.getItemsNum() <= 1:
            self.pivot.setVisible(False)
