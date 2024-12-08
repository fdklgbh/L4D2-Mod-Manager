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

**修复bug**
1. 修复文件被占用提示文件不存在错误
2. 修复mod表格中快捷键F2 编辑非标题列内容后报错

## 关于
1. github打不开
    可以翻墙或者下载[fastgithub](https://gitee.com/zhaifanhua/FastGithub/releases/download/2.1.4/fastgithub_win-x64.zip)
2. **地图**

    **部分地图拆分为多个part 部分part没有地图相关信息(没有maps/或者missions/开头的文件,且addoninfo中也没有代表地图的字段,或者有但值为0)**
3. 快捷键
    1. 刷新 F5
    2. 搜索 Ctrl+F
4. 更新
    可以在设置中检查更新,或者设置启动后自动检查更新
5. mod多选 ctrl按下再选中 也可以按住shift选中第一个选中的到再次点击的mod
6. 标题列右键可以进入编辑 自定义标题(不会写入到vpk文件中) 也可以选中标题列内容后使用F2快捷键

"""
        self.update_info.setMarkdown(text)
        self.update_info.anchorClicked.connect(QDesktopServices.openUrl)
