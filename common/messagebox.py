# -*- coding: utf-8 -*-
# @Time: 2024/2/23
# @Author: Administrator
# @File: messagebox.py
from pathlib import Path

from PyQt5.QtCore import QThreadPool, pyqtSignal, Qt
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import MessageBoxBase, IndeterminateProgressBar, PlainTextEdit, SubtitleLabel, BodyLabel, ComboBox, \
    IndeterminateProgressRing, ListWidget

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
    def __init__(self, parent, file_path: Path, key, new_value):
        super().__init__(parent)
        self._file = file_path
        self.inProgressBar = IndeterminateProgressBar(self)
        self.widget.setMinimumWidth(520)
        self.plainText = PlainTextEdit(self)
        self.plainText.setReadOnly(True)
        self.plainText.setMinimumHeight(100)
        self._thread_pool = QThreadPool.globalInstance()
        title = SubtitleLabel(self)
        title.setText(f'写入配置到 {self._file.stem} 的addoninfo文件中')
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
        file_info.update({key: new_value})
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
    """
    添加切换mod前,先选择分类
    todo 添加的时候,选择是否勾选读取addons workshop中的mod文件(可能会读取addonlist中启用或者禁用)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.comboBox = ComboBox()
        self.loadTypeComboBox = ComboBox()
        text_list = ['全部'] + ModType.father_type_keys()
        text_list.remove('地图')
        self.all_type = text_list
        self.comboBox.addItems(text_list)
        self.subtitle = SubtitleLabel()
        self.subtitle.setText('选择后续的分类: ')
        layout.addWidget(self.subtitle)
        layout.addWidget(self.comboBox)
        self.viewLayout.addLayout(layout)
        self.load_used()
        self.yesButton.setText('确定')
        self.cancelButton.setText('取消')
        self.comboBox.currentTextChanged.connect(self.newTypeChoice)
        self.widget.setMinimumWidth(350)

    def load_used(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.loadTypeComboBox.addItem('')
        self.loadTypeComboBox.addItems(self.all_type)
        self.loadTypeComboBox.setMinimumWidth(100)
        subtitle = BodyLabel()
        subtitle.setText('加载启用mod分类: ')
        layout.addWidget(subtitle)
        layout.addWidget(self.loadTypeComboBox)
        self.viewLayout.addLayout(layout)

    def getLoadType(self):
        return self.loadTypeComboBox.text()

    def newTypeChoice(self, text):
        self.loadTypeComboBox.clear()
        self.loadTypeComboBox.addItem('')
        if text == '全部':
            self.loadTypeComboBox.addItems(self.all_type)
        else:
            self.loadTypeComboBox.addItem(text)


class LoadingMessageBox(MessageBoxBase):
    optionChangedSignal = pyqtSignal(str)
    optionFileChangedSignal = pyqtSignal(str)
    loadingStatusChangedSignal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.loading = IndeterminateProgressRing()
        self.option = SubtitleLabel()
        self.option.setText('准备开始切换')
        self.optionFile = BodyLabel()
        self.optionFile.setText('正在处理文件...')

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))  # 左侧空白
        horizontalLayout.addWidget(self.loading)
        horizontalLayout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))  # 右侧空白

        layout.addLayout(horizontalLayout)
        layout.addWidget(self.option)
        layout.addWidget(self.optionFile)
        self.viewLayout.addLayout(layout)
        self.widget.setMinimumWidth(350)
        self.buttonGroup.hide()

        self.optionChangedSignal.connect(lambda x: self.option.setText(x))
        self.optionFileChangedSignal.connect(lambda x: self.optionFile.setText(f'正在处理文件: {x}'))
        self.loadingStatusChangedSignal.connect(lambda x: self.loading.stop() if x else self.loading.start())


class NotFoundFileMessageBox(MessageBoxBase):
    def __init__(self, parent, title, notFoundFileList: list[str]):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.option = SubtitleLabel()
        self.option.setText(title)
        self.listWidget = ListWidget()
        self.listWidget.addItems(notFoundFileList)

        layout.addWidget(self.option)
        layout.addWidget(self.listWidget)
        self.viewLayout.addLayout(layout)
        self.yesButton.setText('忽略')
        self.cancelButton.setText('退出')
