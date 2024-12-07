# -*- coding: utf-8 -*-
# @Time: 2024/2/12
# @Author: Administrator
# @File: ExceptionHook.py
import sys
import time
import traceback
from pathlib import Path
from common import logger
from PyQt5.QtCore import pyqtSignal


class ExceptionHook:
    exceptionSignal = pyqtSignal(str)

    def __init__(self, log_folder='log'):
        self.old = sys.excepthook
        self.form = None
        sys.excepthook = self._custom_exception_handler
        self.log_folder = log_folder

    def _custom_exception_handler(self, type_, value, trace: traceback):
        traceback_format = traceback.format_exception(type_, value, trace)
        error_msg = "".join(traceback_format)
        file_name = f'error_{int(time.time())}.log'
        logger.exception(f"错误信息:\n{error_msg}")
        self.exceptionSignal.emit(str(error_msg) + f'日志文件保存在Log文件夹下\n文件名：{file_name}')
        # QMessageBox.critical(self.form, "错误", str(error_msg) + f'日志文件保存在Log文件夹下\n文件名：{file_name}')
        path = Path(self.log_folder)
        path.mkdir(exist_ok=True)
        with open(path / file_name, 'w', encoding='utf8') as f:
            f.write(error_msg)
