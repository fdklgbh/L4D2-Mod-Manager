# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: safe_application.py
from PyQt5.QtWidgets import QApplication
from loguru import logger

from .components import customDialog
import sys
import traceback

class SafeApplication(QApplication):
    def notify(self, receiver, event):
        try:
            return QApplication.notify(self, receiver, event)
        except Exception as e:
            logger.exception(e)
            traceback.print_exc()
            # 可在这里弹窗或记录日志
            customDialog('程序发生错误',
                         f'程序遇到一个未处理的异常。\n{traceback.format_exc()}',
                         None, cancelBtn=False)
            return False

# 使用自定义 Application
app = SafeApplication(sys.argv)