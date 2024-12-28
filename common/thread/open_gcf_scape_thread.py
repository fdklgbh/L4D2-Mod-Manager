# -*- coding: utf-8 -*-
# @Time: 2024/12/21
# @Author: Administrator
# @File: open_gcf_scape_thread.py
import os

from PyQt5.QtCore import QRunnable

from common.config import l4d2Config

class OpenGCFScape(QRunnable):
    def __init__(self):
        super().__init__()
        self.exe = l4d2Config.gcfspace_path.__str__()
        self.vpk_file = None

    def run(self):
        cmd = f'{self.exe} "{self.vpk_file}"'
        os.popen(cmd)
        self.vpk_file = None

    def set_vpk_file(self, vpk_file):
        self.vpk_file = vpk_file
