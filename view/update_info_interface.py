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
**修复BUG**
1. 最小化后再打开出现的错误

## 1.0.5
**修复BUG**
1. 部分vpk文件解析路径时,解析编码后再次解码失败

**新增功能**
1. 标题列内容可以自定义,右键编辑(不会存到vpk文件中)
2. 检查有无版本更新(可以启动就检查,默认关闭, 请求链接: [update_version.json](https://fdklgbh.github.io/L4D2-Mod-Manager/update_version.json))
3. 设置-清理缓存:清除已删除vpk文件的缓存文件

## 关于
1. github打不开
    可以翻墙或者下载[fastgithub](https://gitee.com/zhaifanhua/FastGithub/releases/download/2.1.4/fastgithub_win-x64.zip)
2. 快捷键
    1. 刷新 F5
    2. 搜索 Ctrl+F
"""
        self.update_info.setMarkdown(text)
        self.update_info.anchorClicked.connect(QDesktopServices.openUrl)
