# -*- coding: utf-8 -*-
# @Time: 2025/1/13
# @Author: Administrator
# @File: mod_switch_interface.py
from __future__ import annotations

import time
from pathlib import Path
from time import sleep

import psutil
from PyQt5.QtCore import QPoint, Qt, QThread, QModelIndex, QTimer
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from common import logger
from common.Bus import signalBus
from common.config import l4d2Config, vpkConfig
from common.copy_data import copy
from common.database import db
from common.item import Item
from common.messagebox import ChoiceTypeMessageBox, LoadingMessageBox, NotFoundFileMessageBox
from common.myIcon import MyIcon
from common.widget.dialog import *
from common.thread import MoveSwitchModThread
from ui.mod_switch import Ui_ModSwitchInterface
from qfluentwidgets import RoundMenu, Action, MenuAnimationType, FluentIcon, InfoBarIcon, InfoBar, InfoBarPosition

from view.edit_type_info_page import editTypeInfoPage

temp = []
temp_map = []


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
        self._pauseMove = False
        self.switchWindows: editTypeInfoPage = None
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

    def add_default_type(self):
        data = []
        for i in l4d2Config.read_addonlist(True):
            file = l4d2Config.addons_path / i
            logger.info(f'加载启用的mod文件:{file}')
            if not file.exists() or not file.is_file():
                continue
            if file.suffix != '.vpk':
                continue
            max_retry = 10
            while max_retry >= 0:
                max_retry -= 1
                vpkInfoIndex, father_type = self.get_cache_info(file.stem)
                if father_type == '地图':
                    temp_map.append(i.replace('.vpk', ''))
                    break
                if vpkInfoIndex == -1:
                    logger.warn(f'出现无缓存文件, {file.stem}, 等待0.2秒')
                    time.sleep(0.2)
                else:
                    data.append(vpkInfoIndex)
                    break
                if max_retry < 0:
                    logger.warn(f'加载启用的mod文件失败:{file}')
        logger.debug(f'加载mod数量:{len(data)}')
        status, info = self.add_type_detail_info('默认', '全部', data)
        if not isinstance(info, int):
            logger.warn('插入数据失败')
            logger.exception(info)
        logger.info('默认mod加载完毕')

    def get_cache_info(self, filename):
        temp.append(filename)
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
        todo data改为字典 {id: 0/1}
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
            db.addClassificationInfo(id_, data, 1)
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
        print([fileName, fatherType, childType, oldFatherType, oldChildType])
        if fatherType == oldFatherType and oldFatherType != '':
            db.vpkInfoChangeChildType(fileName, childType)
            return
        if not (res := db.getAddonInfoType(fileName)):
            return
        if fatherType == res.get('fatherType'):
            return
        result = db.vpkInfoChangeType(fileName, fatherType, childType, oldFatherType, oldChildType)
        if result:
            print('result', db.vpkInfoChangeType)
            count = self.switch_type_info.count()
            for index in range(count - 1, -1, -1):
                item = self.switch_type_info.item(index)
                id_ = item.data(Qt.UserRole)
                if id_ in result:
                    self.switch_type_info.takeItem(index)
        print('刷新')
        selected_row = self.switch_type_info.currentRow()
        self.switch_type_info.setCurrentRow(-1)
        self.switch_type_info.setCurrentRow(selected_row)

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
            if self.switch_type_info.count() > 1 and self.switchWindows is None:
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
        """
        todo after before 改为字典 {id: 0/1}
        :param name:
        :param after:
        :param before:
        :param typeId:
        :return:
        """
        if name:
            db.changeClassificationName(typeId, name)
        after_set = set(after)
        before_set = set(before)
        need_add = after_set.difference(before_set)
        need_remove = before_set.difference(after_set)
        # 交叉的表示重复,或者有修改 todo
        logger.info(f'需要添加的vpkInfo.id:{need_add}')
        logger.info(f'需要删除的vpkInfo.id:{need_remove}')
        if need_remove:
            db.deleteClassificationInfo(typeId, list(need_remove), commit=False)
        if need_add:
            start = db.getClassificationInfoMaxNumber(typeId) + 1
            db.addClassificationInfo(typeId, need_add, start, commit=False)
        db.commit()
        for i in range(self.switch_type_info.count()):
            item = self.switch_type_info.item(i)
            if item.data(Qt.UserRole) == typeId:
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
        if self.switchWindows:
            w = InfoBar(
                icon=InfoBarIcon.WARNING,
                title='',
                content='已存在待编辑窗口,请先关闭',
                orient=Qt.Vertical,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=2000,
                parent=self
            )
            w.show()
            print(self.switchWindows)
            return

        self.switchWindows = editTypeInfoPage(modType, title, enabledMod, saveFunc, typeId)
        # self.w.setWindowModality(Qt.ApplicationModal)
        self.switchWindows.setWindowTitle(windowTitle)
        self.switchWindows.closedSignal.connect(lambda: setattr(self, 'switchWindows', None))
        self.switchWindows.show()

    @staticmethod
    def find_process_by_name(name='left4dead2.exe'):
        for proc in psutil.process_iter(['pid', 'name']):
            if proc:
                if name == proc.name():
                    return True

    def menueChangeType(self, item: QListWidgetItem):

        def pause():
            load_window.loadingStatusChangedSignal.emit(True)

        def resume():
            load_window.loadingStatusChangedSignal.emit(False)

        def fileNotFind(option, not_find_file: list):
            pause()
            print('未找到mod:', not_find_file)
            w = NotFoundFileMessageBox(self.window(), option, not_find_file)
            if w.exec():
                resume()
                thread.restore()
                return
            quitSwitchModThread()

        def moveFailed(option, info):
            pause()
            if customMessageBox(option, info, self.window(), '重试', '退出'):
                thread.restore()
                resume()
                return
            quitSwitchModThread()

        def moveFileNotExists(option, fileName):
            pause()
            if customMessageBox(option, f'移动文件时 {fileName} 不存在', self.window(), '跳过', '退出'):
                thread.restore()
                resume()
                return
            quitSwitchModThread()

        def quitSwitchModThread():
            if customMessageBox('退出切换', '退出切换不会回滚之前的操作,确定退出吗', self.window(), '继续', '退出'):
                resume()
                thread.restore()
            else:
                thread.stop()
                load_window.yesButton.click()

        def finished():
            print('结束')
            load_window.yesButton.click()
            load_window.close()
            QTimer.singleShot(1, load_window.close)
            print('退出')

        id_ = item.data(Qt.UserRole)
        type_ = item.data(Qt.UserRole + 1)
        thread = MoveSwitchModThread(type_, id_)
        logger.info(f'切换分类: {item.text()}, id: {id_}, 分类: {type_}')
        if not customMessageBox(f'切换mod为{item.text()}?', '请确认游戏已关闭, mod文件未被占用, 避免切换过程中出现错误',
                                self.window(), cancelBtn='退出'):
            return
        if self.find_process_by_name():
            customDialog('警告', '请先关闭游戏', self.window(), '退出', cancelBtn=False)
            return
        thread.moveFileNotExistsSignal.connect(moveFileNotExists)
        thread.moveFailedSignal.connect(moveFailed)
        thread.fileNotFindSignal.connect(fileNotFind)
        load_window = LoadingMessageBox(self.window())
        thread.optionSignal.connect(load_window.optionChangedSignal.emit)
        thread.optionFileSignal.connect(load_window.optionFileChangedSignal.emit)
        thread.finished.connect(finished)
        thread.start()
        load_window.exec()

    @staticmethod
    def getAllVpkFile(folder: Path = None):
        if folder is None:
            folder = [l4d2Config.addons_path, l4d2Config.workshop_path, l4d2Config.disable_mod_path]
        else:
            folder = [folder]
        for i in folder:
            for file in i.glob('*.vpk'):
                if not file.is_file():
                    continue
                yield file
