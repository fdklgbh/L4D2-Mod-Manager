# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: exception_hook.py
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from .components import customDialog


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理器
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # 允许 Ctrl+C 正常退出
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # 弹出错误对话框（仅在有 QApplication 时）
    if QApplication.instance():
        customDialog('程序发生错误',
                     f'程序遇到一个未处理的异常。\n{"".join(traceback.format_exception(exc_type, exc_value, exc_traceback))}',
                     None, cancelBtn=False)


# 安装全局异常钩子
sys.excepthook = handle_exception
