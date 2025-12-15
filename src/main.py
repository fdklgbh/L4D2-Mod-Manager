# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: main.py
import sys
from loguru import logger
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

locale = QLocale(QLocale.Chinese, QLocale.China)
translator = FluentTranslator(locale)

app.installTranslator(translator)
app.setStyleSheet("""* {background-color: transparent;border: none}""")
try:
    w = MainWindow()
    w.show()
except Exception as e:
    logger.exception(e)
finally:
    app.exec_()
