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

**修复bug**
1. 检查更新请求连接失败返回msg导致的报错
2. 切换mod编辑页面
   1. 搜索关键词修改导致显示不出来结果
   2. 搜索内容限制为当前的分类信息
   3. 分类和搜索词关联(切换清除搜索词)
   4. 分类筛选开关和搜索词关联(切换清除搜索词)
   5. 分类筛选同步当前配置的mod
3. 从未使用过配置游戏路径显示文本修改为游戏路径
4. 数据文件不存在报错处理
5. 没有自定义标题的时候,修改标题会直接写入vpk,修改为如果和原本一致就不写入

**优化**
1. 加载mod过程中,页面禁止操作 避免后续判定错误
2. 启用列表的mod,可以配置写入addonlist文件为启用还是禁用
3. mod切换的时候会依据配置的启用禁用写入addonlist.txt(全部则会按照顺序写在最前面,后续可拖动排序),其余分类直接写入到文件最底部
4. 新增切换mod类型的时候,提供加载目前启用的对应分类mod为启用
5. mod页面描述可修改
6. mod切换编辑页面启用栏支持拖拽切换顺序

## 关于
1. github打不开
    可以翻墙或者下载[Steamcommunity 302](https://www.dogfight360.com/blog/18682/) 可找进入找最新版下载 (fastgithub gitee删库)
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
