# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: generate_mod_info.py
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from shared.mods import ModInfo
from shared.runtime import LogBase
from shared.vpk import AnalysisVPK
from .service import mod_browser_service


class GenerateModInfo(QThread, LogBase):
    # itemSignal = Signal(list)
    itemSignal = Signal(ModInfo)

    def __init__(self, folder: Path):
        super().__init__()
        self.TAG = f"GenerateModInfo-{folder.stem}"
        self._folder = folder
        self._analysisVPK = AnalysisVPK()
        self._reload = False
        self._reload_files: set[str] | None = None

    def file(self):
        for i in self._folder.glob("*.vpk"):
            if i.is_file() and (
                self._reload_files is None or i.stem in self._reload_files
            ):
                yield i

    def get_total(self):
        return len([1 for i in self.file()])

    def reload(self, filenames: list[str] | None = None):
        self._reload = True
        self._reload_files = set(filenames) if filenames else None

    def __call__(self, *args, **kwargs):
        """批量解析当前目录中的 VPK 信息并发送结果。"""
        mod_infos = mod_browser_service.load_or_refresh_mod_infos(
            self.file(), self._analysisVPK, self._reload
        )
        for mod_info in mod_infos:
            self.itemSignal.emit(mod_info)
        self._reload = False
        self._reload_files = None

    def run(self):
        try:
            self()
        except Exception as e:
            print("error")
            self.logger.exception(e)
            raise
