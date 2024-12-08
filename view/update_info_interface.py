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

**新增**
1. 新增日志页面
   1. 后续日志会显示在日志页面中(设置按钮上方)
   2. 日志也会存储到程序根目录下的log文件夹中,日志文件名称为L4d2ModManager.log
      
      单个文件最大存储日志5mb,文件最多备份4个


**优化**
1. 分类重写,为后续自定义分类准备
   1. 分类后续考虑是通过请求获取分类信息进行更新替换文件还是本地文件配置(大概率是通过请求获取并下载)
2. 选中多个mod右键菜单不再有单个启用/禁用(单个就单个,多个就多个)
3. 多选后,分类文本修改为修改分类(单个选中保持原样)
4. 更换类型的时候,选中多个,会同时更改多个mod(打开选择类型窗口后,没有选中mod类型即为多选)

**修复bug**
1. 连续多个文件不存在重复弹窗问题修复
2. 修复mod页面展示图片后,切换到其他页面后窗口变化再切回mod页面,大小异常问题
3. 无黑窗口版本打开vpk有黑窗口持续展示
4. 无黑窗口版本打开文件所在位置有一闪而过的黑窗口

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
6. 标题列右键可以进入编辑 自定义标题(不会写入到vpk文件中)

"""
        self.update_info.setMarkdown(text)
        self.update_info.anchorClicked.connect(QDesktopServices.openUrl)
