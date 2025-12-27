# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: mod_view.py
from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QRegularExpression,
    QModelIndex,
)
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget, QAbstractItemView, QApplication, QHeaderView
from qfluentPackage.widget import CSegmentedWidget
from qfluentwidgets import (
    RoundMenu,
    Action,
    InfoBar,
    InfoBarIcon,
    InfoBarPosition,
    StateToolTip,
)

from core import l4d2Config, LogBase
from models import *
from schemas import ModInfo
from services import GenerateModInfo
from .ui import Ui_modShowView


class ModuleStacked(QWidget, Ui_modShowView, LogBase):
    TAG = "ModuleStacked"

    def __init__(self, path: Path):
        super().__init__()
        self.stateTooltip: StateToolTip = None
        self.setupUi(self)
        self.analysisVpkThread = GenerateModInfo(path)
        self.mod_total, self.progress_num = 0, 0
        self._folder = path
        self.refresh_add_menu()
        self.source_model = ModShowModel(
            self, ["文件名", "标题", "作者", "描述", "标语"], path
        )
        self.proxy_model = ProxyModSearch(self)
        self.proxy_model.setSourceModel(self.source_model)
        self.set_tableview()
        self.changePlaceholderText(False)
        self.hide_vkp_info()
        self.connectSignal()
        self.analysisVpkThread.start()

    def set_tableview(self):
        # 边框可见
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)
        self.tableView.setModel(self.proxy_model)
        # 自动换行
        self.tableView.setWordWrap(False)
        # 表头隐藏
        self.tableView.verticalHeader().hide()
        # 按照内容自适应宽度大小
        # self.tableView.resizeColumnsToContents()
        # 水平表头设置为自动拉伸
        self.tableView.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        # self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # 排序
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def refresh_add_menu(self):
        menu = RoundMenu(parent=self.refresh_btn)
        menu.addAction(Action(text="重新读取VPK文件", triggered=self.reloadMod))
        self.refresh_btn.setFlyout(menu)

    def reloadMod(self):
        self.analysisVpkThread.reload()
        self.analysisVpkThread.start()

    def perform_search(self, text: str = ""):
        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        # 恢复表列头的初始升序/降序状态
        self.tableView.clearSelection()
        if self.regexBtn.isChecked():
            self.verify_regex(text)
        else:
            self.proxy_model.setFilterFixedString(text)
        self.hide_vkp_info()

    def onDoubleClicked(self, e: QModelIndex):
        index = self.proxy_model.mapToSource(e)
        col = index.column()

        if col == 0:
            self.copy_data(index.data())
        else:
            modInfo = self.source_model.index(index.row(), 0).data(Qt.UserRole)
            self.copy_data(
                e.data(), f"{modInfo.filename} {self.source_model.getHeader(col)}"
            )

    def copy_data(self, copy_data, content=None):
        clipboard = QApplication.clipboard()
        clipboard.setText(copy_data)
        if content is None:
            content = f"{copy_data} 已经复制到剪贴板"
        else:
            content += " 已经复制到剪贴板"
        w = InfoBar(
            icon=InfoBarIcon.INFORMATION,
            title="复制成功",
            content=content,
            orient=Qt.Vertical,  # vertical layout
            isClosable=True,
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self.window(),
        )
        w.show()

    def hide_vkp_info(self):
        self.vkp_info.hide()

    def verify_regex(self, text=""):
        regex = QRegularExpression(text)
        if regex.isValid():
            self.proxy_model.setFilterRegularExpression(regex)
            self.updateSearchEditStyle(False)
        else:
            self.updateSearchEditStyle(True)

    def updateSearchEditStyle(self, error=False):
        if error:
            self.search_edit.setProperty("type", "error")
        else:
            self.search_edit.setProperty("type", None)
        self.search_edit.style().unpolish(self.search_edit)
        self.search_edit.style().polish(self.search_edit)
        self.search_edit.update()

    def on_splitter_moved(self, *args):
        sizes = self.splitter.sizes()
        if sizes[1] == 0:
            self.splitter.setHandleWidth(0)
        else:
            self.splitter.setHandleWidth(6)

    def changePlaceholderText(self, status):
        if status:
            self.search_edit.setPlaceholderText("正则搜索")
        else:
            self.search_edit.setPlaceholderText("关键词搜索")
            self.updateSearchEditStyle(False)
        self.perform_search(self.search_edit.text())

    def connectSignal(self):
        self.refresh_btn.clicked.connect(self.refresh)
        # todo
        self.analysisVpkThread.started.connect(self.threadStarted)
        self.analysisVpkThread.finished.connect(self.threadFinished)
        self.analysisVpkThread.itemSignal.connect(self.addRow)

        QShortcut(QKeySequence("ctrl+f"), self).activated.connect(
            self.search_edit.setFocus
        )
        QShortcut(QKeySequence("f5"), self).activated.connect(self.refresh)

    def refresh(self):
        print("refresh")
        self.source_model.clearAll()
        # self.tableView.setModel(self.source_model)
        self.analysisVpkThread.start()

    def threadFinished(self):
        self.logger.debug(f"mod文件夹 {self._folder.name} 加载完成")
        if self.stateTooltip:
            self.stateTooltip.setContent("全部加载完成了")
            self.stateTooltip.setState(True)
        self.progress_num = 0
        self.setDisabled(False)
        self.stateTooltip = None
        self.proxy_model.setDynamicSortFilter(True)
        self.proxy_model.disableFilter(False)

    def threadStarted(self):
        self.logger.debug(f"开始加载 {self._folder.name} vpk文件")
        self.setDisabled(True)
        self.mod_total = self.analysisVpkThread.get_total()
        self.proxy_model.disableFilter(True)
        self.proxy_model.setDynamicSortFilter(False)
        self.search_edit.clear()
        self.perform_search()
        self.stateTooltip = StateToolTip(
            "正在加载vpk信息", f"{self.progress_num}/{self.mod_total}", self
        )
        self.stateTooltip.move(self.stateTooltip.getSuitablePos())
        self.stateTooltip.show()

    def cleanup(self):
        self.logger.debug("cleanup_thread")
        self.analysisVpkThread.quit()
        self.analysisVpkThread.wait(1)

    def addRow(self, modInfo: ModInfo):
        self.progress_num += 1
        if self.stateTooltip:
            self.stateTooltip.setContent(
                f"{self.progress_num}/{self.mod_total} {modInfo.filename}"
            )
        self.source_model.addModInfo(modInfo)

    def closeEvent(self, a0):
        self.cleanup()
        super().closeEvent(a0)


class ModShowView(CSegmentedWidget):
    def __init__(self, folder_path: list[Path], parent=None):
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


__all__ = ["ModShowView"]
