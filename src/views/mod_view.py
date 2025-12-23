# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: mod_view.py
from pathlib import Path

from PyQt5.QtCore import (
    Qt,
    QRegularExpression,
    QModelIndex,
    QTimer,
    QThread,
    QCoreApplication,
)
from PyQt5.QtWidgets import QWidget, QAbstractItemView, QApplication
from qfluentPackage.widget import CSegmentedWidget
from qfluentwidgets import RoundMenu, Action, InfoBar, InfoBarIcon, InfoBarPosition

from core import l4d2Config, LogBase
from models import *
from services import GenerateModInfo
from .ui import Ui_modShowView


class ModuleStacked(QWidget, Ui_modShowView, LogBase):
    TAG = "ModuleStacked"

    def __init__(self, path: Path):
        super().__init__()
        self.setupUi(self)
        self.analysisVpkThread = GenerateModInfo(path)
        menu = RoundMenu(parent=self.refresh_btn)
        menu.addAction(
            Action(text="重新读取VPK文件", triggered=lambda: print("重新读取"))
        )
        self.refresh_btn.setFlyout(menu)
        self.source_model = ModShowModel(
            self, ["文件名", "标题", "作者", "描述", "标语"], path
        )
        # self.proxy_model = ProxyModSearch(self)
        # self.proxy_model.setSourceModel(self.source_model)
        # self.tableView.setModel(self.proxy_model)
        self.tableView.setModel(self.source_model)
        self.changePlaceholderText(False)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.hide_vkp_info()
        self.connectSignal()
        # if not l4d2Config.is_disable_mod_path(path):
        #     self.analysisVpkThread.start()
        self.analysisVpkThread.start()

    def perform_search(self, text: str = ""):
        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        # 恢复表列头的初始升序/降序状态
        self.tableView.clearSelection()
        # if self.regexBtn.isChecked():
        #     self.verify_regex(text)
        # else:
        #     self.proxy_model.setFilterFixedString(text)
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

    def refresh(self):
        self.source_model.clearAll()
        # self.tableView.setModel(self.source_model)
        self.analysisVpkThread.start()

    def threadFinished(self):
        self.logger.debug("threadFinished 触发")
        self.setDisabled(False)
        # self.proxy_model.setDynamicSortFilter(True)
        # self.proxy_model.disableFilter(False)
        # self.tableView.setModel(self.proxy_model)

    def threadStarted(self):
        self.logger.debug("threadStarted 触发")
        self.setDisabled(True)
        # self.proxy_model.disableFilter(True)
        # self.proxy_model.setDynamicSortFilter(False)
        self.search_edit.clear()
        self.perform_search()

    def cleanup(self):
        self.logger.debug("cleanup_thread")
        self.analysisVpkThread.quit()
        self.analysisVpkThread.wait(1)

    def addRow(self, modInfo):
        self.source_model.addModInfo(modInfo)
        self.logger.debug(f"数据添加成功")

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
