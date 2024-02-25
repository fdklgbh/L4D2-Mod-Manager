# -*- coding: utf-8 -*-
# @Time: 2024/2/12
# @Author: Administrator
# @File: ExceptionHook.py
import sys
import time
import traceback
from pathlib import Path

from PyQt5.QtWidgets import QMessageBox


class ExceptionHook:
    def __init__(self, parent=None):
        sys.excepthook = self._custom_exception_handler
        self.parent = parent

    def _custom_exception_handler(self, type_, value, trace: traceback):
        traceback_format = traceback.format_exception(type_, value, trace)
        error_msg = "".join(traceback_format)
        file_name = f'error_{int(time.time())}.log'
        print('error_msg', error_msg)
        QMessageBox.critical(self.parent, "错误", str(error_msg) + f'日志文件保存在Log文件夹下\n文件名：{file_name}')
        path = Path('log')
        path.mkdir(exist_ok=True)
        with open(path / file_name, 'w', encoding='utf8') as f:
            f.write(error_msg)
        sys.exit(-1)
