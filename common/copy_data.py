# -*- coding: utf-8 -*-
# @Time: 2025/1/18
# @Author: Administrator
# @File: copy_data.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import InfoBar, InfoBarIcon, InfoBarPosition


def copy(parent, data, content='', title='复制成功'):
    if content == '':
        content = f'{data} 已经复制到剪贴板'
    clipboard = QApplication.clipboard()
    clipboard.setText(data)
    w = InfoBar(
        icon=InfoBarIcon.INFORMATION,
        title=title,
        content=content,
        orient=Qt.Vertical,
        isClosable=True,
        position=InfoBarPosition.TOP_RIGHT,
        duration=2000,
        parent=parent
    )
    w.show()


__all__ = ['copy']
