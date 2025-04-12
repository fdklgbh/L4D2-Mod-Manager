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
        self.setupUi(self)
        self.setObjectName('UpdateInfoInterface')
        text = f"""
# 求生之路2 模组管理器
## {VERSION} 更新日志

**新增**

1. 一键切换预设mod(不会替换地图, 可以选择全部替换或者替换单个大分类)

   第一次打开加载会比较慢,需要先等待左侧出现"全部-默认"再使用

**优化**

1. 检查更新的请求地址更换,超时时间修改为5秒
2. 缓存切换为数据库(逐渐切换,目前先读取缓存文件写入数据库,后续直接读取数据库,即可不再需要缓存文件)


## 关于
1. github打不开
    可以翻墙或者下载[Steamcommunity 302](https://www.dogfight360.com/blog/18682/) (fastgithub gitee删库)
2. **地图**

    **部分地图拆分为多个part 部分part没有地图相关信息(没有maps/或者missions/开头的文件,且addoninfo中也没有代表地图的字段,或者有但值为0)**
    
    **如果看见部分和地图没有关系的mod,那应该就是addoninfo中有addoncontent_campaign或者addoncontent_map字段,且值为1导致的,需要自己手动更换一下类型**
3. 快捷键
    1. 刷新 F5
    2. 搜索 Ctrl+F
4. 更新
    可以在设置中检查更新,或者设置启动后自动检查更新
5. mod多选 ctrl按下再选中 也可以按住shift选中第一个选中的到再次点击的mod
6. 标题列右键可以进入编辑 自定义标题(不会写入到vpk文件中) 也可以选中标题列内容后使用F2快捷键
7. 刷新按钮右键可刷新缓存
"""
        self.update_info.setMarkdown(text)
        self.update_info.anchorClicked.connect(QDesktopServices.openUrl)
