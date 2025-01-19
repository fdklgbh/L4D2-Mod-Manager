# -*- coding: utf-8 -*-
# @Time: 2024/2/23
# @Author: Administrator
# @File: messagebox.py
from pathlib import Path

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QHBoxLayout, QComboBox
from qfluentwidgets import MessageBoxBase, IndeterminateProgressBar, PlainTextEdit, SubtitleLabel, BodyLabel, ComboBox

from common import logger
from common.Bus import signalBus
from common.conf import ModType
from common.config import vpkConfig, l4d2Config
from common.thread.rewrite_addoninfo_thread import ReWriteAddonInfoThread
from common.widget.custom_tree_widget import CustomTreeWidget


class ChangeTypeMessageBox(MessageBoxBase):
    def __init__(self, parent, data: list, more=False):
        super().__init__(parent)
        self.new_check_type = ''
        self.new_father_type = ''
        self.setWindowTitle('修改Mod分类')
        self.data_info, self.child_type, self.father_type = data
        self._more = len(self.data_info) > 1
        if more:
            self.child_type = ''
            self.father_type = ''
        self.tableWidget = CustomTreeWidget(self, [self.child_type, self.father_type])

        # add widget to view layout
        self.viewLayout.addWidget(self.tableWidget)
        # change the text of button
        self.yesButton.setText(self.tr('确定'))
        self.cancelButton.setText(self.tr('取消'))

        self.widget.setMinimumWidth(360)
        self.yesButton.setDisabled(True)
        self.tableWidget.selectedSignal.connect(self.check)
        self.yesButton.clicked.connect(self.yesButton_clicked)

    def yesButton_clicked(self, *args):
        child_type = self.new_check_type
        father_type = self.new_father_type
        logger.debug('yesButton_clicked %s %s', child_type, father_type)
        for data in self.data_info:
            signalBus.fileTypeChanged.emit(data, father_type, child_type, self.father_type, self.child_type)

    def check(self, child_type: str, father_type: str, no_child: bool):
        """
        确定按钮显示与否
        :param no_child: 是否无二级分类
        :param child_type:
        :param father_type:
        :return:
        """

        def change_disable_status(status):
            self.yesButton.setDisabled(status)
            if status is False:
                self.new_check_type = child_type
                self.new_father_type = father_type

        if father_type == self.father_type:
            if child_type and child_type != self.child_type:
                change_disable_status(False)
                return
            change_disable_status(True)
            return
        # 一级目录不一样的时候
        if no_child:
            change_disable_status(False)
        elif child_type:
            change_disable_status(False)
        else:
            change_disable_status(True)


class ReWriteMessageBox(MessageBoxBase):
    def __init__(self, parent, file_path: Path, new_title):
        super().__init__(parent)
        self._file = file_path
        self._new_title = new_title
        self.inProgressBar = IndeterminateProgressBar(self)
        self.widget.setMinimumWidth(520)
        self.plainText = PlainTextEdit(self)
        self.plainText.setReadOnly(True)
        self.plainText.setMinimumHeight(100)
        self._thread_pool = QThreadPool.globalInstance()
        title = SubtitleLabel(self)
        title.setText(f'写入标题到 {self._file.stem} 的addoninfo文件中')
        body = BodyLabel(self)
        body.setText('写入成功会直接退出,如果没有成功,点击确定')
        self.cancelButton.setText('我知道了')
        self.yesButton.setText('确定')
        self.viewLayout.addWidget(title)
        self.viewLayout.addWidget(body)
        self.viewLayout.addWidget(self.inProgressBar)
        self.viewLayout.addWidget(self.plainText)
        signalBus.reWriteLogSignal.connect(self.plainText.appendPlainText)
        res = vpkConfig.get_file_config(self._file.stem)
        file_info = res.get('file_info', {"addonsteamappid": '550'})
        file_info.update({'addontitle': new_title})
        self.yesButton.hide()
        self.buttonLayout.insertStretch(0, 1)
        self.cancelButton.setEnabled(False)
        vpkConfig.change_file_single_config(self._file.stem, 'file_info', file_info)
        self.thread = ReWriteAddonInfoThread(self._file, file_info)
        self.thread.resultSignal.connect(self.updateResult)
        self.thread.finished.connect(self.thread_finished)
        self.thread.start()

    def thread_finished(self):
        if self.cancelButton.isEnabled():
            return
        self.yesButton.click()

    def updateResult(self, status: bool, data: str, filename: str) -> None:
        if not status:
            self.cancelButton.setEnabled(True)
            return
        signalBus.reWriteResultSignal.emit(self._file.parent, filename, data)
        self.buttonLayout.insertStretch(0)
        self.yesButton.show()
        self.inProgressBar.pause()
        self.inProgressBar.hide()


class ChoiceTypeMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        # self.titleLabel = SubtitleLabel('打开 URL')
        # self.urlLineEdit = LineEdit()
        layout = QHBoxLayout()
        self.comboBox = ComboBox()
        text_list = ['全部'] + ModType.father_type_keys()
        text_list.remove('地图')
        self.comboBox.addItems(text_list)
        self.subtitle = SubtitleLabel()
        self.subtitle.setText('选择后续的分类: ')
        layout.addWidget(self.subtitle)
        layout.addWidget(self.comboBox)

        # self.urlLineEdit.setPlaceholderText('输入文件、流或者播放列表的 URL')
        # self.urlLineEdit.setClearButtonEnabled(True)

        # 将组件添加到布局中
        # self.viewLayout.addWidget(self.titleLabel)
        # self.viewLayout.addWidget(self.urlLineEdit)
        self.viewLayout.addLayout(layout)
        # 设置对话框的最小宽度
        self.widget.setMinimumWidth(350)

    # def showMessage(window):
    #     w = CustomMessageBox(window)
    #     if w.exec():
    #         print(w.urlLineEdit.text())
