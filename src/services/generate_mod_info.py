# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: generate_mod_info.py
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, QThread, QCoreApplication

from core import get_db, LogBase
from core.models import *
from schemas import ModInfo
from utils.vpk import AnalysisVPK


class GenerateModInfo(QThread, LogBase):
    # itemSignal = pyqtSignal(list)
    itemSignal = pyqtSignal(ModInfo)

    def __init__(self, folder: Path):
        super().__init__()
        self.TAG = f"GenerateModInfo-{folder.stem}"
        self._folder = folder
        self._analysisVPK = AnalysisVPK()

    def file(self):
        for i in self._folder.glob("*.vpk"):
            if i.is_file():
                yield i

    def __call__(self, *args, **kwargs):
        with get_db() as session:
            for file in self.file():
                if (
                    vpkInfo := session.query(VPKInfo)
                    .filter(VPKInfo.fileName == file.stem)
                    .first()
                ) is None:
                    vpkInfo = self._analysisVPK.getAddonInfo(file)
                    session.add(vpkInfo)
                    session.commit()
                    self.logger.debug("commit success")
                self.itemSignal.emit(ModInfo.from_vpk_info(vpkInfo))
        # all_num = len([1 for _ in self.file()])
        # if all_num > 1000:
        #     max_num = 100
        # elif all_num > 100:
        #     max_num = 10
        # else:
        #     max_num = 1
        # data = []
        # num = 0
        # with get_db() as session:
        #     for file in self.file():
        #         vpkInfo = (
        #             session.query(VPKInfo).filter(VPKInfo.fileName == file.stem).first()
        #         )
        #         if vpkInfo is None:
        #             vpkInfo = self._analysisVPK.getAddonInfo(file)
        #             session.add(vpkInfo)
        #             session.commit()
        #             self.logger.debug('commit success')
        #         num += 1
        #         data.append(ModInfo.from_vpk_info(vpkInfo))
        #         if num < 40 or len(data) >= max_num or num >= all_num:
        #             self.itemSignal.emit(data)
        #             self.logger.debug(f'emit success')
        #             data = []
        #             self.msleep(10)

    def run(self):
        try:
            self()
        except Exception as e:
            print("error")
            self.logger.exception(e)
            raise
