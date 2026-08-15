# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: mod_show_tableview.py
import shutil
from pathlib import Path

from PySide6.QtCore import QModelIndex, Signal, Qt
from PySide6.QtGui import QContextMenuEvent, QDesktopServices
from qfluentwidgets import (
    TableView,
    RoundMenu,
    Action,
    FluentIcon as FIF,
    MenuAnimationType,
    InfoBar,
    InfoBarPosition,
)

from core import LogBase, Icon, l4d2Config, appConstants, signalBus
from models import ProxyModSearch, ModShowModel
from schemas import ModInfo
from utils.components import customDialog


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
            move_to_addons.triggered.connect(
                lambda x: self.move_mod(l4d2Config.addons_path, select_indexes)
            )
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
        move_more.triggered.connect(
            lambda x: self.move_mod(target_path, select_indexes)
        )
        # refreshAction.triggered.connect(
        #             lambda x: self.refreshCacheSignal.emit([data.data(Qt.UserRole + 2)[0] for data in select_indexes]))
        menu.closedSignal.connect(menu.deleteLater)
        menu.exec(a0.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def move_mod(self, target_path: Path, select_indexes: list[QModelIndex]):
        """移动mod文件到目标路径

        Args:
            target_path: 目标文件夹路径
            select_indexes: 选中的代理模型索引列表
        """
        source_model = self.sourceModel()
        # 收集需要移动的信息: (source_row, mod_info)
        move_items: list[tuple[int, ModInfo]] = []
        for proxy_index in select_indexes:
            source_index = self.getSourceIndex(proxy_index)
            mod_info: ModInfo = source_index.data(Qt.UserRole)
            if mod_info:
                move_items.append((source_index.row(), mod_info))

        # 按源模型行号降序排列，避免删除时索引错位
        move_items.sort(key=lambda x: x[0], reverse=True)

        success_count = 0
        for source_row, mod_info in move_items:
            src_file = self.folderPath / f"{mod_info.filename}.vpk"
            dst_file = target_path / f"{mod_info.filename}.vpk"

            if not src_file.exists():
                self.logger.warning(f"源文件不存在: {src_file}")
                continue

            # 检查源文件是否被占用 (仅Windows)
            if self._is_file_used(src_file):
                self.logger.warning(f"源文件被占用: {src_file}")
                InfoBar.warning(
                    title="",
                    content=f"mod文件 {mod_info.filename} 被占用",
                    orient=Qt.Horizontal,
                    isClosable=False,
                    position=InfoBarPosition.TOP,
                    parent=self.window(),
                )
                continue

            target_exists = dst_file.exists()

            if target_exists:
                # 检查目标文件是否被占用 (仅Windows)
                if self._is_file_used(dst_file):
                    self.logger.warning(f"目标文件被占用: {dst_file}")
                    InfoBar.warning(
                        title="",
                        content=f"待覆盖mod文件 {mod_info.filename} 被占用",
                        orient=Qt.Horizontal,
                        isClosable=False,
                        position=InfoBarPosition.TOP,
                        parent=self.window(),
                    )
                    continue

                # 弹出确认覆盖对话框
                if not customDialog(
                    "警告",
                    f"目标文件夹中已存在 {mod_info.filename}，是否覆盖？",
                    self.window(),
                    yesBtn="覆盖",
                    cancelBtn="取消",
                ):
                    continue

            try:
                target_path.mkdir(parents=True, exist_ok=True)
                if target_exists:
                    # 目标已存在，使用 replace 进行原子替换
                    try:
                        src_file.replace(dst_file)
                    except OSError:
                        # 跨文件系统时 replace 可能失败，回退到 shutil
                        dst_file.unlink()
                        shutil.move(str(src_file), str(dst_file))
                else:
                    shutil.move(str(src_file), str(dst_file))

                # 处理关联的图片文件
                src_pic = self.folderPath / f"{mod_info.filename}.jpg"
                dst_pic = target_path / f"{mod_info.filename}.jpg"
                if src_pic.exists():
                    try:
                        if dst_pic.exists():
                            src_pic.replace(dst_pic)
                        else:
                            shutil.move(str(src_pic), str(dst_pic))
                    except Exception as e:
                        self.logger.warning(f"图片移动失败: {src_pic.name}, 错误: {e}")

                source_model.removeModInfo(source_row)
                self.logger.info(f"移动成功: {src_file.name} -> {target_path}")
                success_count += 1
            except PermissionError as e:
                if l4d2Config.is_win:
                    winerror = getattr(e, "winerror", 0)
                    if winerror == 32:  # ERROR_SHARING_VIOLATION
                        self.logger.warning(f"文件被占用: {src_file.name}")
                        InfoBar.error(
                            title="",
                            content="当前文件被占用",
                            orient=Qt.Horizontal,
                            isClosable=False,
                            position=InfoBarPosition.TOP,
                            parent=self.window(),
                        )
                    elif winerror == 5:  # ERROR_ACCESS_DENIED
                        self.logger.warning(f"拒绝访问: {dst_file.name}")
                        InfoBar.error(
                            title="移动失败",
                            content="被覆盖文件使用中",
                            orient=Qt.Horizontal,
                            isClosable=False,
                            position=InfoBarPosition.TOP,
                            parent=self.window(),
                        )
                    else:
                        self.logger.error(f"权限错误: {src_file.name}, 错误: {e}")
                        InfoBar.error(
                            title="移动失败",
                            content=str(e),
                            orient=Qt.Horizontal,
                            isClosable=False,
                            position=InfoBarPosition.TOP,
                            parent=self.window(),
                        )
                else:
                    self.logger.error(f"权限错误: {src_file.name}, 错误: {e}")
                    InfoBar.error(
                        title="移动失败",
                        content=str(e),
                        orient=Qt.Horizontal,
                        isClosable=False,
                        position=InfoBarPosition.TOP,
                        parent=self.window(),
                    )
            except Exception as e:
                self.logger.error(f"移动失败: {src_file.name}, 错误: {e}")

        self.clearSelection()
        self.logger.info(f"移动完成: 成功 {success_count}/{len(move_items)}")
        if success_count > 0:
            signalBus.modMoveSignal.emit(target_path.resolve())

    @staticmethod
    def _is_file_used(file_path: Path) -> bool:
        """检查文件是否被其他进程占用

        Windows: 通过 CreateFileW 以独占模式打开文件来检测
        Linux: 始终返回 False (Linux 下文件不会被进程锁定)
        """
        if not l4d2Config.is_win:
            return False
        try:
            import ctypes
            from ctypes import wintypes

            GENERIC_READ = 0x80000000
            OPEN_EXISTING = 3
            FILE_ATTRIBUTE_NORMAL = 0x80
            INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

            kernel32 = ctypes.windll.kernel32
            kernel32.CreateFileW.restype = wintypes.HANDLE
            handle = kernel32.CreateFileW(
                str(file_path),
                GENERIC_READ,
                0,  # dwShareMode=0 不共享，检测独占
                None,
                OPEN_EXISTING,
                FILE_ATTRIBUTE_NORMAL,
                None,
            )
            if handle == INVALID_HANDLE_VALUE:
                return True
            kernel32.CloseHandle(handle)
            return False
        except Exception:
            return False

    def sourceModel(self) -> ModShowModel:
        return self.model().sourceModel()

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
                    f"{i.filename} 目录结构:\n{'\n'.join([_ for _ in vpk])}"
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
