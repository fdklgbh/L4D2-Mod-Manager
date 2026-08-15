# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: exception_hook.py
import sys
import traceback

from PySide6.QtWidgets import QApplication
from loguru import logger

from shared.persistence import dispose
from shared.widgets import customDialog


def handle_exception(exc_type, exc_value, exc_traceback):
    """
    全局异常处理器
    Args:
        exc_type:
        exc_value:
        exc_traceback:
    """
    if issubclass(exc_type, KeyboardInterrupt):
        # 允许 Ctrl+C 正常退出
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # logger.bind(tag="handle_exception").exception(exc_value)
    execTionInfo = traceback.format_exception(exc_type, exc_value, exc_traceback)
    info = "".join(execTionInfo)
    logger.bind(tag="handle_exception").exception(info)

    # 弹出错误对话框（仅在有 QApplication 时）
    if app := QApplication.instance():
        customDialog(
            "程序发生错误",
            f"程序遇到一个未处理的异常。\n{info[:500]}...",
            None,
            cancelBtn=False,
        )
        app.quit()
        dispose()
    sys.exit(2)


# 安装全局异常钩子
sys.excepthook = handle_exception
