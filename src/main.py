# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: main.py
import sys

from PyQt5.QtCore import (
    Qt,
    QLocale,
    QtMsgType,
    QMessageLogContext,
    qInstallMessageHandler,
)
from PyQt5.QtWidgets import QApplication
from loguru import logger
from qfluentwidgets import FluentTranslator


def qt_message_handler(mode: QtMsgType, context: QMessageLogContext, message: str):
    """
    处理 Qt 发出的消息
    """
    if mode == QtMsgType.QtDebugMsg:
        level = "DEBUG"
    elif mode == QtMsgType.QtWarningMsg:
        level = "WARNING"
    elif mode == QtMsgType.QtCriticalMsg:
        level = "CRITICAL"
    elif mode == QtMsgType.QtFatalMsg:
        level = "FATAL"
    else:
        level = "INFO"

    # 打印文件、行号、函数（如果可用）
    print(
        f"[{level}] {message} "
        f"(file: {context.file}, line: {context.line}, func: {context.function})",
        file=sys.stderr,
    )


# 安装消息处理器（必须在 QApplication 创建之前！）
qInstallMessageHandler(qt_message_handler)


import utils.exception_hook  # type: ignore
import utils.logger_setup  # type: ignore
from core import l4d2Config, dispose
from resources import resource_rc  # type: ignore
from views.first_view import FirstView
from views.main_view import MainWindow


QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

locale = QLocale(QLocale.Chinese, QLocale.China)
translator = FluentTranslator(locale)

app.installTranslator(translator)
app.setStyleSheet("""* {background-color: transparent;border: none}""")


try:

    def show():
        from utils import updateDB  # type: ignore

        w = MainWindow()
        w.show()

    if not l4d2Config.l4d2_path or not l4d2Config.disable_mod_path:
        print(l4d2Config.l4d2_path, l4d2Config.disable_mod_path)
        first = FirstView()
        first.finished.connect(show)
        first.exec()
    else:
        show()
    res = app.exec_()
    print(f"code {res=}")

except Exception as e:
    logger.debug("Exception")
    logger.exception(e)
    dispose()
    sys.exit(1)
finally:
    dispose()
    logger.info("db closed")
