# -*- coding: utf-8 -*-
# @Time: 2025/1/16
# @Author: Administrator
# @File: edit_type_info_page.py
import sys
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, QVariant
from PyQt5.QtGui import QKeyEvent, QIcon, QDropEvent
from PyQt5.QtWidgets import QWidget, QApplication, QListWidgetItem, QAbstractItemView
from common.conf import ModType
from common.copy_data import copy
from common.item import Item
from common.myIcon import MyIcon
from common.thread.read_cache_thread import ReadCacheThread
from ui.edit_type_info_page import Ui_Form
from qfluentwidgets import ListWidget, Dialog, RoundMenu, Action, InfoBar, InfoBarPosition


# todo 保存修改排序(1.3.0 addonlist排序,(全部类mod排序))
# todo 导入当前addons workshop文件作为预设

class editTypeInfoPage(QWidget, Ui_Form, Item):
    saveDataSignal = pyqtSignal(dict)
    closedSignal = pyqtSignal()

    def __init__(self, modType='全部', title=None, enabledMod: dict = None, saveFunc=None, typeId=None):
        super().__init__()
        self.setWindowIcon(QIcon(MyIcon.L4D2.path()))
        self.enabledMod = enabledMod or {}
        self.saveFunc = saveFunc
        self.title = title or ''
        self.typeId = typeId
        self.modType = modType
        self.filterFatherType = modType
        self.filterChildType = ''
        self.setupUi(self)
        self.enabledWidget.setDragEnabled(True)
        self.enabledWidget.setDropIndicatorShown(True)
        self.enabledWidget.setDragDropMode(ListWidget.InternalMove)
        # self.enabledWidget.setDragDropMode(QAbstractItemView.DragDrop)
        self.typeBox.setText(self.modType)
        self.menu()
        if self.enabledMod:
            self.disableAllBtn.setEnabled(True)
        self._savePage = False
        self.saveNameEdit.setClearButtonEnabled(True)
        if self.title:
            self.saveNameEdit.setText(self.title)
        self.setFocus()
        self.setCustomQss()
        self.stackedWidget.setCurrentWidget(self.page_2)
        # thread_pool = QThreadPool.globalInstance()
        self.readThread = ReadCacheThread(enabledMod, self.modType)
        self.connectSignal()
        # thread_pool.start(self.readThread)

        # self.typeBox
        self.readThread.start()
        self.itemIds = {}
        for item in self.setItems(self.enabledMod):
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if item.data(Qt.UserRole + 5) == 1:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.enabledWidget.addItem(item)
            self.itemIds[self.get_item_id(item)] = self.get_item_enable_status(item)
        self.setEnabled(False)

    def menu(self):
        menu = RoundMenu()
        if self.modType != '全部':
            # 特定分类
            child = ModType.child_keys(self.modType)
            if child:
                menu.addActions([Action(i) for i in ["全部"] + child])
                self.typeBox.setMenu(menu)
                menu.triggered.connect(self.typeChange)
            else:
                self.typeBox.setText(self.modType)
            return
        text_list = ['全部'] + ModType.father_type_keys()
        text_list.remove('地图')
        for father in text_list:
            child_keys = ModType.child_keys(father)
            if child_keys:
                father_menu = RoundMenu(father, menu)
                menu.addMenu(father_menu)
                father_menu.addAction(Action('全部', father_menu))
                for child in ModType.child_keys(father):
                    father_menu.addAction(Action(child, father_menu))
            else:
                menu.addAction(Action(father))
        self.typeBox.setMenu(menu)
        menu.triggered.connect(self.typeChange)

    def disableAllMod(self, *args):
        self.typeChange(Action(text='全部'))
        items = [item for item in self.getWidgetAllItem(self.enabledWidget)]
        self.moveWidgetItems(items, self.disabledWdiget, self.enabledWidget)

    def disableMod(self, *args):
        items = self.enabledWidget.selectedItems()
        items.sort(key=lambda x: self.enabledWidget.row(x))
        self.moveWidgetItems(items, self.disabledWdiget, self.enabledWidget)
        self.enabledWidget.setCurrentIndex(QModelIndex())

    def enableMod(self, *args):
        items = self.disabledWdiget.selectedItems()
        items.sort(key=lambda x: self.disabledWdiget.row(x))
        self.moveWidgetItems(items, self.enabledWidget, self.disabledWdiget)
        self.disabledWdiget.setCurrentIndex(QModelIndex())

    def moveWidgetItems(self, items: list[QListWidgetItem], addItemWidget: ListWidget, removeItemWidget: ListWidget):
        # todo item 移动到启用,mod选中,且滑动到第一个 scrollToItem  QListWidget.PositionAtTop
        data = []
        for item in self.getWidgetAllItem(addItemWidget):
            data.append(item.text())
        add_data = []
        for item in items:
            add_data.append(item.text())
            removeItemWidget.takeItem(removeItemWidget.row(item))
        data.extend(add_data)
        data.sort()
        index_list = [(data.index(item), items[index]) for index, item in enumerate(add_data)]
        index_list.sort(key=lambda x: x[0])
        isEnabled = addItemWidget == self.enabledWidget
        for index, item in index_list[::-1]:
            addItemWidget.insertItem(index, item)
            if isEnabled:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
            else:
                item.setData(Qt.CheckStateRole, QVariant())
        if self.enabledWidget.count() > 0:
            self.disableAllBtn.setEnabled(True)
            self.checkSaveBtn()
        else:
            self.disableAllBtn.setEnabled(False)

    def savePage(self, *args):
        print('保存')
        self._savePage = True
        if self.typeId is None:
            # 添加
            self.saveFunc(self.saveNameEdit.text(), self.modType, self._getEnableData, True)
        else:
            if self.saveNameEdit.text() == self.title:
                name = None
            else:
                name = self.saveNameEdit.text()
            # 修改
            self.saveFunc(name, self._getEnableData, self.itemIds, self.typeId)
        self.close()

    @property
    def _getEnableData(self):
        return {self.get_item_id(item): 1 if item.checkState() == 2 else 0 for item in
                self.getWidgetAllItem(self.enabledWidget)}

    def fileNameChanged(self, text):
        self.checkSaveBtn(text)

    def checkSaveBtn(self, text: str = None):
        if text is None:
            text = self.saveNameEdit.text()
        if not text:
            self.changeSaveBtn(False)
            return
        count = self.enabledWidget.count()
        if count == 0:
            self.changeSaveBtn(False)
            return
        items_file_name = []
        for item in self.getWidgetAllItem(self.enabledWidget):
            fileName = self.get_item_fileName(item)
            if fileName in items_file_name:
                continue
            items_file_name.append(fileName)
            if self.get_item_fileName(item) in self.enabledMod and self.get_item_checkState(
                    item) != self.get_item_enable_status(item):
                self.changeSaveBtn(True)
                return

        items_file_name.sort()
        enabled = list(self.enabledMod.keys())
        enabled.sort()
        print('checkSaveBtn', items_file_name, enabled)
        if items_file_name != enabled or text != self.title:
            self.changeSaveBtn(True)
        else:
            self.changeSaveBtn(False)

    @staticmethod
    def get_item_checkState(item):
        if item.checkState() == 2:
            return 1
        return item.checkState()

    def changeSaveBtn(self, status: bool):
        self.saveBtn.setEnabled(status)

    def connectSignal(self):
        self.readThread.modNumberSignal.connect(self.ProgressBar.setMaximum)
        self.readThread.doneOnceSignal.connect(self.updateProgress)
        # self.readThread.doneNumberSignal.connect(self.ProgressBar.setValue)
        self.readThread.doneNumberSignal.connect(self.setProgressBar)
        self.readThread.finished.connect(self.readThreadFinished)
        self.disabledWdiget.itemSelectionChanged.connect(self.disabledModSelected)
        self.enabledWidget.itemSelectionChanged.connect(self.enabledModSelected)
        self.enabledWidget.itemChanged.connect(self.itemChanged)
        self.enabledWidget.dropChanged.connect(self.dropChanged)

    def dropChanged(self):
        if not self.enabledMod:
            self.changeSaveBtn(True)
        else:
            print(list(self.enabledMod.keys()))
            print([self.get_item_fileName(i) for i in self.getWidgetAllItem(self.enabledWidget)])
            if list(self.enabledMod.keys()) != [self.get_item_fileName(i) for i in
                                                self.getWidgetAllItem(self.enabledWidget)]:
                self.changeSaveBtn(True)
            else:
                self.checkSaveBtn()

    def itemChanged(self, item: QListWidgetItem):
        fileName = self.get_item_fileName(item)
        if not fileName:
            return
        if fileName not in self.enabledMod:
            return
        status = item.checkState()
        if status == 2:
            status = 1
        info = self.get_item_enable_status(item)
        if info is None:
            return
        if status != info:
            self.changeSaveBtn(True)
            return
        self.checkSaveBtn()

    def keyPressEvent(self, a0: QKeyEvent):
        if self.isVisible():
            if a0.modifiers() == Qt.ControlModifier and a0.key() == Qt.Key_F:
                self.searchLineEdit.setFocus()
            elif a0.key() == Qt.Key_Escape:
                self.setFocus()
        super().keyPressEvent(a0)

    def syncTypeBtnChanged(self, status: bool):
        for item in self.getWidgetAllItem(self.enabledWidget):
            if status:
                self._checkTypeHide(item, True, True)
            else:
                item.setHidden(False)
        self.searchLineEdit.clear()
        self.enabledWidget.setCurrentIndex(QModelIndex())

    def setProgressBar(self, value: int):
        self.ProgressBar.setValue(value)

    def disabledModSelected(self, *args):
        self.enabledBtn.setEnabled(bool(self.disabledWdiget.selectedItems()))

    def enabledModSelected(self, *args):
        self.disabledBtn.setEnabled(bool(self.enabledWidget.selectedItems()))

    def readThreadFinished(self):
        self.stackedWidget.setCurrentWidget(self.page_3)
        self.setEnabled(True)

    def updateProgress(self, data: dict):
        if name := data.get('fail'):
            InfoBar.warning(
                title='',
                content=f'{name}没有解析缓存,可能不是mod文件',
                orient=Qt.Horizontal,
                isClosable=False,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self.window()
            )
            return
        name = data['fileName']
        self.loadingModText.setText(name)
        self.disabledWdiget.addItem(self.setOnceItem(name, data))

    def copyFileTitle(self, item: QListWidgetItem):
        fileTitle = item.data(Qt.UserRole)
        copy(self, fileTitle)

    def setCustomQss(self):
        self.setStyleSheet("background-color: rgb(247,249,252);")

    def _checkTypeHide(self, item, isEnableWidget=None, setHide: bool = False):
        itemFatherType = self.get_item_father_type(item)
        itemChildType = self.get_item_child_type(item)
        if isEnableWidget and self.syncType.isChecked() is False:
            status = False
        elif self.filterFatherType == '全部':
            status = False
        else:
            if itemFatherType != self.filterFatherType:
                status = True
            elif self.filterChildType == '':
                status = False
            elif itemChildType != self.filterChildType:
                status = True
            else:
                status = False
        if setHide:
            item.setHidden(status)
        return status

    def searchChange(self, text=''):
        text = text.strip().lower()
        for widget in [self.enabledWidget, self.disabledWdiget]:
            is_enAbelWidget = widget == self.enabledWidget
            for item in self.getWidgetAllItem(widget):
                if not text:
                    self._checkTypeHide(item, is_enAbelWidget, True)
                    continue
                hide = self._checkTypeHide(item, is_enAbelWidget)
                if hide:
                    item.setHidden(hide)
                    continue
                if text not in item.text():
                    item.setHidden(True)
                else:
                    item.setHidden(False)

    @staticmethod
    def getWidgetAllItem(widget: ListWidget):
        for index in range(widget.count()):
            yield widget.item(index)

    def typeChange(self, action: Action):
        if self.modType == '全部':
            child_type = action.text()
            if action.parentWidget():
                father_type = action.parentWidget().title()
                if child_type == '全部':
                    child_type = ''
            else:
                father_type = child_type
                child_type = ''
        else:
            father_type = self.modType
            if (child_type := action.text()) == '全部':
                child_type = ''

        self.typeBox.setText(child_type if child_type else father_type)
        self._set_show(self.disabledWdiget, father_type, child_type)
        self.filterFatherType = father_type
        self.filterChildType = child_type
        if self.syncType.isChecked():
            self.disabledBtn.setEnabled(False)
            self._set_show(self.enabledWidget, father_type, child_type)
        if self.searchLineEdit.text():
            self.searchLineEdit.clear()

    def _set_show(self, widget: ListWidget, fatherType: str = None, childType: str = None):
        for item in self.getWidgetAllItem(widget):
            father = self.get_item_father_type(item)
            child = self.get_item_child_type(item)
            if fatherType == '全部':
                item.setHidden(False)
                continue
            if father == fatherType and childType == child:
                item.setHidden(False)
            elif father == fatherType and childType == '':
                item.setHidden(False)
            else:
                item.setHidden(True)

    def closeEvent(self, a0):
        def showAlert(content='内容有变化,是否关闭'):
            w = Dialog('注意', content, parent=self)
            w.windowTitleLabel.hide()
            w.yesButton.setText('继续编辑')
            w.cancelButton.setText('关闭')
            result = w.exec_()
            if result:
                a0.ignore()
            else:
                self.saveDataSignal.emit({
                    'title': self.saveNameEdit.text()
                })
            return result

        if self._savePage is False:
            if self.title:
                if self.title != self.saveNameEdit.text():
                    if showAlert():
                        return
            if allItem := self.getWidgetAllItem(self.enabledWidget):
                if not allItem:
                    print('555')
                    if showAlert():
                        return
                items_file_name = [item.data(Qt.UserRole) for item in allItem]
                items_file_name.sort()
                enabled = list(self.enabledMod.keys())
                enabled.sort()
                if items_file_name != enabled:
                    print('777')
                    if showAlert():
                        print('888')
                        return
        self.readThread.stop = True
        self.readThread.quit()
        self.readThread.wait()
        self.closedSignal.emit()
        super().closeEvent(a0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = editTypeInfoPage('近战', saveFunc=lambda *args, **kwargs: print('args', args, kwargs))
    main.show()
    app.exec_()
