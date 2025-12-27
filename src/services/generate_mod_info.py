# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: generate_mod_info.py
from pathlib import Path

from PySide6.QtCore import QThread, Signal

from core import get_db, LogBase
from core.models import *
from schemas import ModInfo, ModCategory
from utils.vpk import AnalysisVPK


class GenerateModInfo(QThread, LogBase):
    # itemSignal = Signal(list)
    itemSignal = Signal(ModInfo)

    def __init__(self, folder: Path):
        super().__init__()
        self.TAG = f"GenerateModInfo-{folder.stem}"
        self._folder = folder
        self._analysisVPK = AnalysisVPK()
        self._reload = False

    def file(self):
        for i in self._folder.glob("*.vpk"):
            if i.is_file():
                yield i

    def get_total(self):
        return len([1 for i in self.file()])

    def reload(self):
        self._reload = True

    def __call__(self, *args, **kwargs):
        with get_db() as session:
            for file in self.file():
                vpkInfo: VPKInfo | None = (
                    session.query(VPKInfo).filter(VPKInfo.fileName == file.stem).first()
                )
                if vpkInfo is None:
                    vpkInfo = self._analysisVPK.getAddonInfo(file)
                    session.add(vpkInfo)
                    session.commit()
                elif self._reload:
                    tmp = self._analysisVPK.getAddonInfo(
                        file,
                        ModCategory(
                            category=vpkInfo.category,
                            subCategory=vpkInfo.subCategory,
                        ),
                    )
                    vpkInfo.customAddonInfo = tmp.addonInfo
                    vpkInfo.customAddonInfoContent = tmp.addonInfoContent
                    session.commit()
                self.itemSignal.emit(ModInfo.from_vpk_info(vpkInfo))
        self._reload = False

    def run(self):
        try:
            self()
        except Exception as e:
            print("error")
            self.logger.exception(e)
            raise
