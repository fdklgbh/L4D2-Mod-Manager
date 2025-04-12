# -*- coding: utf-8 -*-
# @Time: 2025/1/21
# @Author: Administrator
# @File: move_switch_mod_thread.py
import time
from pathlib import Path

from PyQt5.QtCore import QThread, pyqtSignal

from common import logger
from common.Bus import signalBus
from common.check_file_used import is_used
from common.config import l4d2Config
from common.database import db

__all__ = ['MoveSwitchModThread']


class MoveSwitchModThread(QThread):
    # 需要挪动的文件没找到 忽略/退出 (还未开始)
    fileNotFindSignal = pyqtSignal(str, list)
    # 操作阶段
    optionSignal = pyqtSignal(str)
    # 操作的文件
    optionFileSignal = pyqtSignal(str)
    # 移动的文件没找到 跳过/退出 fileName
    moveFileNotExistsSignal = pyqtSignal(str, str)
    # 移动失败 重试/退出
    moveFailedSignal = pyqtSignal(str, str)
    refreshSignal = pyqtSignal(set, set, set)

    def __init__(self, type_: str, typeId: int):
        super().__init__()
        self._type = type_
        self._typeId = typeId
        self._pause = True
        self._stop = False
        self._restore = False

    def run(self):
        all_data = db.getTypeAllFileName(self._type)
        enable_data: dict = db.getTypeEnableFileNameNumber(self._typeId)
        enable_file = set(enable_data.keys())
        all_data_set = set(all_data)
        addons_file = set()
        workshop_file = set()
        # 不应该存在的mod
        exclude_data = all_data_set - enable_file
        option = '正在检查已存在的同类型mod...'
        logger.info(option)
        self.optionSignal.emit(option)
        for file in self.getAllVpkFile(l4d2Config.addons_path):
            addons_file.add(file.stem)
        for file in self.getAllVpkFile(l4d2Config.workshop_path):
            workshop_file.add(file.stem)
        # 需要禁用的addons 文件夹mod
        exclude_addons_data = exclude_data & addons_file
        logger.info(f'addons文件夹需要禁用的mod文件名称: {exclude_addons_data}')
        # 需要禁用的workshop文件夹
        exclude_workshop_data = exclude_data & workshop_file
        logger.info(f'workshop文件夹需要禁用的mod文件名称: {exclude_workshop_data}')
        # 排除addons workshop中存在的
        need_enabled_file = enable_file - addons_file - workshop_file
        logger.info(f'需要启用的mod: {need_enabled_file}')
        not_find_file = []
        not_find_file_title = []
        if need_enabled_file:
            for file in need_enabled_file:
                if (l4d2Config.disable_mod_path / f'{file}.vpk').exists():
                    continue
                title = db.getAddonInfo(file).get('title', '未知标题')
                not_find_file.append(file)
                not_find_file_title.append(title)
        if not_find_file:
            # [f"{x}-{y}" for x, y in zip(squares, cubes)]
            option = '未找到的mod'
            emit_data = [f"{name} - {title}" for name, title in zip(not_find_file, not_find_file_title)]
            self.fileNotFindSignal.emit(option, emit_data)
            if self._pauseOrStop():
                return
        option = '正在禁用mod文件'
        logger.info(option)
        self.optionSignal.emit(option)
        for path, exclude_file in [[l4d2Config.addons_path, exclude_addons_data],
                                   [l4d2Config.workshop_path, exclude_workshop_data]]:
            for file in exclude_file:
                self.optionFileSignal.emit(file)
                filePath = path / f'{file}.vpk'
                picPath = path / f'{file}.jpg'
                targetFilePath = l4d2Config.disable_mod_path / f'{file}.vpk'
                targetPicPath = l4d2Config.disable_mod_path / f'{file}.jpg'
                if not filePath.exists():
                    self.moveFileNotExistsSignal.emit(option, file)
                    if self._pauseOrStop():
                        return
                while True:
                    if self._move_file(filePath, targetFilePath):
                        break
                    self.moveFailedSignal.emit(option, f'{file}文件移动失败,可能被占用')
                    if self._pauseOrStop():
                        return
                if picPath.exists():
                    self._move_file(picPath, targetPicPath)
        option = '正在启用mod文件'
        logger.info(option)
        self.optionSignal.emit(option)
        for file in need_enabled_file:
            if file in not_find_file:
                continue
            print('file即将移动', file)
            filePath = l4d2Config.disable_mod_path / f'{file}.vpk'
            picPath = l4d2Config.disable_mod_path / f'{file}.jpg'
            targetFilePath = l4d2Config.addons_path / f'{file}.vpk'
            targetPicPath = l4d2Config.addons_path / f'{file}.jpg'
            if not filePath.exists() and file not in not_find_file:
                self.moveFileNotExistsSignal.emit(option, file)
                if self._pauseOrStop():
                    return
            self.optionFileSignal.emit(file)
            while True:
                if self._move_file(filePath, targetFilePath):
                    break
                self.moveFailedSignal.emit(option, f'{file}文件移动失败,可能被占用')
                if self._pauseOrStop():
                    return
            if picPath.exists():
                self._move_file(picPath, targetPicPath)

        if exclude_addons_data or exclude_workshop_data or need_enabled_file:
            fileData: dict = l4d2Config.read_addonlist()
            for data in [exclude_addons_data, exclude_workshop_data, need_enabled_file]:
                for name in data:
                    fileData.pop(f'{name}.vpk', '')
            
            if self._type == '全部':
                new_file_data = {}
                for file in enable_data:
                    enable = enable_data[file]
                    fullName = f"{file}.vpk"
                    if (l4d2Config.addons_path / fullName).exists():
                        new_file_data[fullName] = str(enable)
                for key in fileData:
                    if key not in new_file_data:
                        new_file_data[key] = fileData[key]
                fileData = new_file_data
            else:
                for file, enable in enable_data.items():
                    fullName = f'{file}.vpk'
                    if not (l4d2Config.addons_path / fullName).exists():
                        continue
                    fileData[fullName] = str(enable)

            l4d2Config.write_addonlist(fileData)
        signalBus.refreshChangedSignal.emit(exclude_addons_data, exclude_workshop_data, need_enabled_file)

    @staticmethod
    def _move_file(file: Path, target: Path):
        if is_used(file):
            return False
        try:
            try:
                file.rename(target)
                logger.info(f'开始移动 {file.name} 文件')
            except FileExistsError:
                file.replace(target)
                logger.info(f'已存在 {file.name} 文件, 替换')
        except PermissionError as e:
            logger.error(f'移动文件过程中出现错误')
            logger.exception(e)
            return False
        else:
            return True

    def _pauseOrStop(self):
        while self._pause is True:
            time.sleep(0.1)
            if self._stop:
                return True
        self._pause = True
        return False

    @staticmethod
    def getAllVpkFile(folder: Path = None):
        if folder is None:
            folder = [l4d2Config.addons_path, l4d2Config.workshop_path, l4d2Config.disable_mod_path]
        else:
            folder = [folder]
        for i in folder:
            for file in i.glob('*.vpk'):
                if not file.is_file():
                    continue
                yield file

    def stop(self):
        self._stop = True

    def restore(self):
        self._pause = False
