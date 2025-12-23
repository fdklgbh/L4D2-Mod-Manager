# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: main.py
import sys

from PyQt5.QtCore import (
    Qt,
    QLocale,
)
from PyQt5.QtWidgets import QApplication
from loguru import logger
from qfluentwidgets import FluentTranslator

import utils.exception_hook  # type: ignore
import utils.logger_setup  # type: ignore
from core import l4d2Config, dispose
from resources import resource_rc  # type: ignore
from utils.safe_application import SafeApplication
from views.first_view import FirstView
from views.main_view import MainWindow


QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = SafeApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

locale = QLocale(QLocale.Chinese, QLocale.China)
translator = FluentTranslator(locale)

app.installTranslator(translator)
app.setStyleSheet("""* {background-color: transparent;border: none}""")


try:
    w = None

    def show():
        from utils import updateDB  # type: ignore

        global w
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
