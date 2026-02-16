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

from core import l4d2Config, LogBase, Menu, signalBus
from models import *
from schemas import ModInfo, ModCategory
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
        self.tableView.folderPath = self._folder
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
        self.refresh()

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

    def handleSplitterMoved(self, *args):
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
        signalBus.modMoveSignal.connect(self.onModMoved)
        QShortcut(QKeySequence("ctrl+f"), self).activated.connect(
            self.search_edit.setFocus
        )
        QShortcut(QKeySequence("f5"), self).activated.connect(self.refresh)

    def onModMoved(self, target_path: Path):
        """当mod被移动到本目录时, 触发刷新"""
        if self._folder.resolve() == target_path:
            self.logger.info(f"检测到mod移入目录 {self._folder.name}, 触发刷新")
            self.refresh()

    def refresh(self):
        self.source_model.clearAll()
        self.proxy_model.setCategoryFilter(None)
        self.menu_btn.setText("全部")
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
        self.logger.debug(
            f"{self._folder.name}-分类信息: {self.source_model.get_menu_infos}"
        )
        self.set_menu()

    def set_menu(self):
        if old_menu := self.menu_btn.menu():
            old_menu.deleteLater()
        _menu = RoundMenu(parent=self.menu_btn)
        source_menu_info = self.source_model.get_menu_infos
        action_all = Action(text=f'全部({source_menu_info.get("all")})', parent=_menu)
        action_all.setToolTip("全部")
        _menu.addAction(action_all)
        for category in Menu.category:
            all_num = source_menu_info.get(f"{category}", 0)
            if Menu.has_child(category):
                category_menu = RoundMenu(parent=_menu, title=f"{category}({all_num})")
                action = Action(text=f"全部({all_num})", parent=category_menu)
                action.setData(ModCategory(category=category))
                action.setToolTip(category)
                category_menu.addAction(action)
                for sub in Menu.find_subcategory(category):
                    num = source_menu_info.get(f"{category}-{sub}", 0)
                    sub_action = Action(text=sub + f"({num})", parent=category_menu)
                    sub_action.setData(ModCategory(category=category, subCategory=sub))
                    sub_action.setToolTip(sub)
                    category_menu.addAction(sub_action)
                _menu.addMenu(category_menu)
            else:
                action = Action(text=f"{category}({all_num})", parent=_menu)
                action.setData(ModCategory(category=category))
                action.setToolTip(category)
                _menu.addAction(action)
        _menu.triggered.connect(self.menu_choice)
        self.menu_btn.setMenu(_menu)

    def menu_choice(self, action: Action):
        self.logger.debug(f"menu_choice: {action}, {action.data()}")
        mod_type: ModCategory = action.data()
        self.proxy_model.setCategoryFilter(mod_type)
        if mod_type:
            text = mod_type.category
            if mod_type.subCategory:
                text = mod_type.subCategory
        else:
            text = "全部"
        self.menu_btn.setText(text)

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
