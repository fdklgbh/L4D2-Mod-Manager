# -*- coding: utf-8 -*-
# @Time: 2024/3/3
# @Author: Administrator
# @File: update_info_interface.py
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

**优化**
1. 增加快捷键
   1. 刷新 F5
   2. 搜索 Ctrl+F
2. 列表选中其中一个后,右侧展示信息可拖动隐藏
3. 增加多个文件一起禁用启用
4. 筛选分类或者搜索后,移动文件后,操作后还存在数据,不会复原
5. addonsinfo文件不存在会把文本信息控件隐藏
6. 新增更新日志

**修复问题**

1. vpk文件打开成功,读取vpk文件路径,编码错误
2. 配置禁用目录后,不会自动创建
"""
        self.undate_info.setMarkdown(text)
