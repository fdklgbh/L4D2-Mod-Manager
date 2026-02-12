# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: mod_show_tableview.py
from pathlib import Path

from PySide6.QtCore import QModelIndex, Signal, Qt
from PySide6.QtGui import QContextMenuEvent, QDesktopServices
from qfluentwidgets import (
    TableView,
    RoundMenu,
    Action,
    FluentIcon as FIF,
    MenuAnimationType,
)

from core import LogBase, Icon, l4d2Config, appConstants
from models import ProxyModSearch
from schemas import ModInfo


class ModShowTableView(TableView, LogBase):
    TAG = "ModShowTableView"

    openFolderSignal = Signal(str)
    openGCFSpaceSignal = Signal(str)
    modeEnableSignal = Signal(Path, int, str)
    refreshCacheSignal = Signal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self._folderPath = None

    @property
    def folderPath(self) -> Path:
        return self._folderPath

    @folderPath.setter
    def folderPath(self, value: Path):
        self._folderPath = value

    def contextMenuEvent(self, a0: QContextMenuEvent, /):
        item = self.indexAt(a0.pos())
        if not item.isValid():
            return
        row = item.row()
        selected_indexes = self.selectedIndexes()
        select_rows: set[int] = set()
        for index in selected_indexes:
            select_rows.add(index.row())
        if row not in select_rows:
            self.selectRow(row)
        menu = RoundMenu(parent=self)
        if item.column() in [1, 3]:
            edit = Action(FIF.EDIT, self.tr("编辑"))
            menu.addAction(edit)
            edit.triggered.connect(lambda: self.edit(item))
        open_file = Action(FIF.FOLDER, self.tr("打开文件所在文件夹"))
        open_gcf = Action(Icon.GCF, self.tr("打开GCFSpace"))
        if not l4d2Config.gcfspace_path:
            open_gcf.setVisible(False)
        else:
            open_gcf.setVisible(True)
        is_disable_path = l4d2Config.is_disable_mod_path(self.folderPath)
        if not is_disable_path:
            target_path = l4d2Config.disable_mod_path
            text = "禁用"
            icon = FIF.CANCEL_MEDIUM
        else:
            target_path = l4d2Config.addons_path
            text = "启用"
            icon = FIF.ACCEPT_MEDIUM
        select_indexes: list[QModelIndex] = []
        for i in self.selectionModel().selectedRows():
            self.logger.debug(f"{i.row()} ===> {i.data()}")
            if i not in select_indexes:
                select_indexes.append(i)
        modInfo = self.getSourceIndexInfo(item)
        is_more = len(select_indexes) > 1
        type_action = Action(
            FIF.FLAG,
            (
                f"类型： {modInfo.modCategory.subCategory or modInfo.modCategory.category}"
                if not is_more
                else "修改分类"
            ),
            self,
        )
        menu.addActions([open_file, open_gcf, type_action])
        self.logger.debug(f"{self.folderPath=}")
        if is_more:
            more_text = "多个"
        else:
            more_text = ""
        if l4d2Config.is_workshop(self.folderPath):
            move_to_addons = Action(FIF.MOVE, self.tr(f"移动{more_text}到Addons"))
            menu.addAction(move_to_addons)
            # move_to_addons.triggered.connect(
            #     lambda x: self.move_mod(l4d2Config.addons_path, select_indexes)
            # )
        move_more = Action(icon, self.tr(f"{text}{more_text}mod"))
        refreshAction = Action(
            Icon.refresh, "刷新缓存" if not is_more else "刷新多个缓存", self
        )
        menu.addActions([move_more, refreshAction])
        if modInfo.url:
            open_url_action = Action(FIF.LINK, self.tr("打开steam链接"))
            menu.addAction(open_url_action)
            open_url_action.triggered.connect(
                lambda: QDesktopServices.openUrl(modInfo.url)
            )
        if appConstants.DEBUG:
            dev_action = Action(text="输出结构")
            menu.addAction(dev_action)
            dev_action.triggered.connect(lambda x: self.dev_action(select_indexes))
        source = self.getSourceIndexInfo(item)
        open_file.triggered.connect(lambda: self.openFolderSignal.emit(source.filename))
        open_gcf.triggered.connect(
            lambda x: self.openGCFSpaceSignal.emit(source.filename)
        )
        type_action.triggered.connect(
            lambda x: self.changeCategory(
                [self.getSourceIndexInfo(j) for j in select_indexes],
            )
        )
        # move_more.triggered.connect(lambda x: self.move_mod(target_path, select_indexes))
        # refreshAction.triggered.connect(
        #             lambda x: self.refreshCacheSignal.emit([data.data(Qt.UserRole + 2)[0] for data in select_indexes]))
        menu.closedSignal.connect(menu.deleteLater)
        menu.exec(a0.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def changeCategory(self, data: list[ModInfo]):
        data.sort(key=lambda x: x.filename)
        self.clearSelection()

    def dev_action(self, select_index: list[QModelIndex]):
        from utils.vpk.open_vpk import OpenVPK

        self.logger.debug(f"[DEV]目录: {self.folderPath}")
        select_modInfos = [self.getSourceIndexInfo(i) for i in select_index]
        self.logger.debug(
            "[DEV]选择的文件 %s",
            [i.filename for i in select_modInfos],
        )
        for i in select_modInfos:
            vpk = OpenVPK(self.folderPath / f"{i.filename}.vpk")
            if vpk.verify():
                self.logger.debug(
                    f'{i.filename} 目录结构:\n{"\n".join([_ for _ in vpk])}'
                )
            else:
                self.logger.warning(f"{i.filename}.vpk打开失败")

    def getSourceIndex(self, index: QModelIndex) -> QModelIndex:
        return self.model().mapToSource(index)

    def getSourceIndexInfo(self, index: QModelIndex) -> ModInfo:
        return self.getSourceIndex(index).data(Qt.UserRole)

    def getProxyIndex(self, index: QModelIndex):
        return self.model().mapFromSource(index)

    def model(self, /) -> ProxyModSearch:
        return super().model()
