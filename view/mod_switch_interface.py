# -*- coding: utf-8 -*-
# @Time: 2025/1/13
# @Author: Administrator
# @File: mod_switch_interface.py
from __future__ import annotations

from time import sleep

from PyQt5.QtCore import QPoint, Qt, QThread, QModelIndex
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from common import logger
from common.Bus import signalBus
from common.config import l4d2Config, vpkConfig
from common.copy_data import copy
from common.database import db
from common.item import Item
from common.messagebox import ChoiceTypeMessageBox
from common.myIcon import MyIcon
from ui.mod_switch import Ui_ModSwitchInterface
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, FluentIcon

from view.edit_type_info_page import editTypeInfoPage


class Temp(QThread):
    def __init__(self, parent, func):
        super().__init__(parent)
        self._func = func

    def run(self) -> None:
        sleep(0.5)
        self._func()


class ModSwitchInterface(QWidget, Ui_ModSwitchInterface, Item):
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.connectSignals()
        Temp(self, self.add_all_types).start()
        # thread.finished.connect(lambda: self.switch_type_info.setCurrentRow(0))

    def add_all_types(self):
        res = db.getAllSwitchInfo()
        if res:
            for type_, name, indexId in res:
                self.addType(name, indexId, type_)
            print('加载完毕')
            self.switch_type_info.setCurrentRow(0)
            return
        self.add_default_type()
        self.switch_type_info.setCurrentRow(0)

    def get_now_used_file(self):
        file_list = []
        for i in [l4d2Config.addons_path, l4d2Config.workshop_path]:
            for file in i.glob('*.vpk'):
                if not file.is_file():
                    continue
                file_list.append(file.stem)
        return file_list

    def add_default_type(self):
        data = []
        for i in [l4d2Config.addons_path, l4d2Config.workshop_path]:
            for file in i.glob('*.vpk'):
                if not file.is_file():
                    continue
                vpkInfoIndex, father_type = self.get_cache_info(file.stem)
                if father_type == '地图':
                    continue
                if vpkInfoIndex == -1:
                    logger.warn(f'出现无缓存文件, {file.stem}')
                    pass
                else:
                    data.append(vpkInfoIndex)
        status, info = self.add_type_detail_info('默认', '全部', data)
        if not isinstance(info, int):
            logger.warn('插入数据失败')
            logger.exception(info)
        # todo 后续版本切换缓存从数据库读取 删掉
        for file in l4d2Config.disable_mod_path.glob('*.vpk'):
            if not file.is_file():
                continue
            self.get_cache_info(file.stem)

    def get_cache_info(self, filename):
        result = db.getAddonInfo(filename)
        if not result:
            res = vpkConfig.get_file_config(filename)
            if not res:
                return -1, '其他'
            result = db.addVpkInfo(filename, res.get('father_type'), res.get('child_type'), res.get('file_info'),
                                   res.get('content'),
                                   res.get('customTitle', res.get('file_info', {}).get('addontitle')))
        return result.get('id'), result.get('fatherType', '其他')

    def add_type_detail_info(self, name, type_, data: list[int], selected=False):
        """
        添加切换类型
        :param selected:
        :param name:
        :param type_:
        :param data:
        :return:
        """
        try:
            id_ = db.addType(name, type_, commit=False)
            print('add_type_detail_info', id_)
            db.addClassificationInfo(id_, data)
            db.commit()
            item = self.addType(name, id_, type_)
            if selected is True:
                self.switch_type_info.setCurrentItem(item)
        except Exception as e:
            return False, e
        return True, id_

    def addType(self, name, indexId, type_):
        item = QListWidgetItem(f"{type_}-{name}")
        item.setData(Qt.UserRole, indexId)
        item.setData(Qt.UserRole + 1, type_)
        item.setData(Qt.UserRole + 2, name)
        self.switch_type_info.addItem(item)
        return item

    def addShow(self, title_list: dict):
        """
        显示读取
        :param title_list:
        :return:
        """
        for item in self.setItems(title_list):
            self.switch_type_show.addItem(item)
        # for name, title in title_list.items():
        #     item = self
        #     self.switch_type_show.addItem(item)

    def connectSignals(self):
        signalBus.fileTypeChanged.connect(self.typeChanged)
        signalBus.vpkNameChanged.connect(self.vpkNameChanged)
        self.switch_type_info.customContextMenuRequested.connect(self.infoContextMenuEvent)
        self.switch_type_info.currentItemChanged.connect(self.currentItemChanged)
        self.switch_type_show.doubleClicked.connect(self.copy)

    def vpkNameChanged(self, fileName, newTitle):
        for index in range(self.switch_type_show.count()):
            item = self.switch_type_show.item(index)
            title = self.get_item_fileName(item)
            if fileName != title:
                continue
            self.set_item_title(item, newTitle)
            break

    def typeChanged(self, data: list[str], fatherType, childType, oldFatherType, oldChildType):
        fileName = data[0]

        if fatherType == oldFatherType and oldFatherType != '':
            db.vpkInfoChangeChildType(fileName, childType)
            return
        if not (res := db.getAddonInfoType(fileName)):
            return
        if fatherType == res.get('fatherType'):
            return
        result = db.vpkInfoChangeType(fileName, fatherType, childType, oldFatherType, oldChildType)
        if result:
            count = self.switch_type_info.count()
            for index in range(count - 1, -1, -1):
                item = self.switch_type_info.item(index)
                id_ = item.data(Qt.UserRole)
                if id_ in result:
                    self.switch_type_info.takeItem(index)

    def copy(self, item: QModelIndex):
        fileTitle = item.data(Qt.UserRole)
        copy(self.window(), fileTitle)

    def currentItemChanged(self, now: QListWidgetItem | None, before: QListWidgetItem | None):
        if now:
            self.switch_type_show.clear()
            indexId = now.data(Qt.UserRole)
            result = db.findSwitchVpkInfo(indexId)
            self.addShow(result)

    def refreshType(self, item: QListWidgetItem):
        self.switch_type_info.setCurrentRow(-1)
        self.switch_type_info.setCurrentRow(self.switch_type_info.row(item))

    def infoContextMenuEvent(self, a0: QPoint):
        if not self.switch_type_info.rect().contains(a0):
            return
        item = self.switch_type_info.itemAt(a0)
        if item and not item.isSelected():
            self.switch_type_info.setCurrentItem(item)

        menu = RoundMenu()
        if item:
            use = Action(MyIcon.switch, '切换')
            use.triggered.connect(lambda x: self.menueChangeType(item))
            menu.addAction(use)
            refresh = Action(MyIcon.refresh, '刷新')
            refresh.triggered.connect(lambda x: self.refreshType(item))
            menu.addAction(refresh)
        add = Action(FluentIcon.ADD, '添加')
        add.triggered.connect(lambda x: self.menueAddType())
        menu.addAction(add)
        if item:
            edit = Action(FluentIcon.EDIT, '修改')
            edit.triggered.connect(lambda x: self.menueEditType(item))
            menu.addAction(edit)
            if self.switch_type_info.count() > 1:
                trash = Action(FluentIcon.DELETE, '删除')
                trash.triggered.connect(lambda x: self.menueRemoveType(item))
                menu.addAction(trash)
        menu.closedSignal.connect(menu.deleteLater)
        menu.exec(self.switch_type_info.mapToGlobal(a0), aniType=MenuAnimationType.DROP_DOWN)

    def menueRemoveType(self, item: QListWidgetItem):
        row = self.switch_type_info.row(item)
        self.switch_type_info.takeItem(row)
        db.deleteType(item.data(Qt.UserRole))

    def edit_type_detail_info(self, name, after: list[int], before: list[int], typeId: int):
        #     (self.saveNameEdit.text(), self._getEnableData, self.itemIds, self.typeId)
        if name:
            db.changeClassificationName(typeId, name)
        after_set = set(after)
        before_set = set(before)
        need_add = after_set.difference(before_set)
        need_remove = before_set.difference(after_set)
        print(need_add)
        print(need_remove)
        if need_remove:
            db.deleteClassificationInfo(typeId, list(need_remove), commit=False)
        if need_add:
            db.addClassificationInfo(typeId, need_add, commit=False)
        db.commit()
        for i in range(self.switch_type_info.count()):
            item = self.switch_type_info.item(i)
            if item.data(Qt.UserRole) == typeId:
                print('xxxxxxxxxxx', i)
                # item.setData(Qt.UserRole, indexId)
                #         item.setData(Qt.UserRole + 1, type_)
                #         item.setData(Qt.UserRole + 2, name)
                if name:
                    item.setData(Qt.UserRole + 2, name)
                    item.setText(f'{item.data(Qt.UserRole + 1)} - {item.data(Qt.UserRole + 2)}')
                self.refreshType(item)
                break

    def menueEditType(self, item: QListWidgetItem):
        print('修改分类', item.text(), item.data(Qt.UserRole), item.data(Qt.UserRole + 1))
        id_ = item.data(Qt.UserRole)
        res = db.findSwitchVpkInfo(id_)
        self.startNewWindow('修改', self.edit_type_detail_info, item.data(Qt.UserRole + 1), item.data(Qt.UserRole + 2),
                            res, id_)

    def menueAddType(self):
        box = ChoiceTypeMessageBox(self.window())
        if not box.exec_():
            return
        self.startNewWindow('添加', self.add_type_detail_info, box.comboBox.text())

    def startNewWindow(self, windowTitle, saveFunc, modType='全部', title=None, enabledMod: dict = None, typeId=None):
        self.w = editTypeInfoPage(None, modType, title, enabledMod, saveFunc, typeId)
        self.w.setWindowModality(Qt.ApplicationModal)
        self.w.setWindowTitle(windowTitle)
        self.w.show()

    def menueChangeType(self, item: QListWidgetItem):
        print('切换分类', item.text(), item.data(Qt.UserRole), item.data(Qt.UserRole + 1))
        # todo 移动文件
