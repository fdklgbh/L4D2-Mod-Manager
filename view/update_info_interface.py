# -*- coding: utf-8 -*-
# @Time: 2024/3/3
# @Author: Administrator
# @File: update_info_interface.py
from PyQt5.QtGui import QDesktopServices
from qfluentwidgets import ScrollArea

from common.conf import VERSION
from ui.update_page import Ui_Form


class UpdateInfoInterface(ScrollArea, Ui_Form):
    def __init__(self, parent):
        ScrollArea.__init__(self, parent)
        self.setObjectName('UpdateInfoInterface')
        self.setupUi(self)
        text = f"""
# 求生之路2 模组管理器
## {VERSION} 更新日志

##  更新日志
###  1.0.4
**修复BUG**
1. 1.0.3的兜底把文件找不到一块处理了,暴露出来
2. 内容编码多次解析失败直接强转字符串

## 关于
1. github打不开
    可以翻墙或者下载[fastgithub](https://gitee.com/zhaifanhua/FastGithub/releases/download/2.1.4/fastgithub_win-x64.zip)
2. 快捷键
    1. 刷新 F5
    2. 搜索 Ctrl+F
"""
        self.update_info.setMarkdown(text)
        self.update_info.anchorClicked.connect(QDesktopServices.openUrl)
