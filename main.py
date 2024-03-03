# -*- coding: utf-8 -*-
# @Time: 2023/12/25
# @Author: Administrator
# @File: main.py
import sys
import traceback
from pathlib import Path
sys.path.append(str(Path(__file__).parent.absolute()))
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator
from resources import resource_rc
from common import logger
from view.main_window import MainWindow

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
    app.exec_()
except Exception as e:
    logger.error(traceback.format_exc())
