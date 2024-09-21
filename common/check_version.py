# -*- coding: utf-8 -*-
# @Time: 2024/9/10
# @Author: Administrator
# @File: check_version.py

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices
from qfluentwidgets import MessageBox

from common.conf import VERSION


def show_version_dialog(result, parent, isAuto=False):
    yes_text = '去更新'
    need_open = False
    if result.get('status') is True:
        if result['update'] is True:
            content = f'有新版本 {VERSION} -> {result["version"]}'
            need_open = True
        else:
            if isAuto:
                return
            content = '当前已是最新版本, 无需更新'
            yes_text = '确定'
    else:
        content = result.get('msg')
        yes_text = '确定'
    w = MessageBox('更新', content, parent.window())
    w.yesButton.setText(yes_text)
    w.cancelButton.setText('关闭')
    if w.exec() and need_open:
        QDesktopServices.openUrl(QUrl(result.get('url') + f'/tag/' + result.get('version')))
