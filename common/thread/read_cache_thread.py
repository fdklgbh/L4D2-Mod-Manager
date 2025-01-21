# -*- coding: utf-8 -*-
# @Time: 2025/1/17
# @Author: Administrator
# @File: read_cache_thread.py

from PyQt5.QtCore import QThread, pyqtSignal, Qt, QRunnable
from PyQt5.QtWidgets import QListWidgetItem

from common.config import l4d2Config, vpkConfig
from common.database import db


class ReadCacheThread(QThread):
    # 文件名称 标题 类型
    doneOnceSignal = pyqtSignal(dict)
    doneNumberSignal = pyqtSignal(int)
    modNumberSignal = pyqtSignal(int)

    def __init__(self, enabled_data: dict = None, modeType='全部'):
        super().__init__()
        self._path_list = [l4d2Config.addons_path, l4d2Config.workshop_path, l4d2Config.disable_mod_path]
        self.stop = False
        self._modeType = modeType
        self._enabled_data = enabled_data or {}

    def run(self) -> None:
        self.modNumberSignal.emit(self.get_all_num)
        checked_filename = []
        num = 0
        files = []
        for path in self._path_list:
            for i in path.glob('*.vpk'):
                if self.stop:
                    return
                if not i.is_file():
                    continue
                files.append(i)
        files.sort(key=lambda x: x.stem)
        for i in files:
            name = i.stem
            num += 1
            self.doneNumberSignal.emit(num)
            if name in self._enabled_data or name in checked_filename:
                continue
            checked_filename.append(name)
            result = db.getAddonInfo(name)
            if not result:
                res = vpkConfig.get_file_config(name)
                if not res:
                    self.doneOnceSignal.emit({"fail": name})
                    continue
                result = db.addVpkInfo(name, res.get('father_type'), res.get('child_type'), res.get('file_info'),
                                       res.get('content'), res.get('customTitle'))
            if result['fatherType'] == '地图':
                continue
            if result['fatherType'] != self._modeType:
                if self._modeType != '全部':
                    continue
            if not result['title']:
                result['title'] = '未知标题'
            result['fileName'] = name
            self.doneOnceSignal.emit(result)

    @property
    def get_all_num(self):
        num = 0
        for path in self._path_list:
            for i in path.glob('*.vpk'):
                if i.is_file():
                    num += 1
        return num
