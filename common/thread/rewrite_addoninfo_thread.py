# -*- coding: utf-8 -*-
# @Time: 2024/12/21
# @Author: Administrator
# @File: rewrite_addoninfo_thread.py
from subprocess import Popen, PIPE
from pathlib import Path
import vdf
from PyQt5.QtCore import QThread, pyqtSignal, QRunnable, QObject
from common.config import l4d2Config
from common.conf import TmpPath
from common.crypto import md5
from common import logger
import shutil
from common.Bus import signalBus


class ReWriteAddonInfoThread(QThread):
    # 成功失败
    resultSignal = pyqtSignal(bool, str, str)

    def __init__(self, file: Path, save_data: dict):
        super().__init__()
        self._file: Path = file
        self._save_data: dict = save_data
        self._save_data.update({'addonsteamappid': 550})

    def run(self):
        workspace = TmpPath / md5(self._file.__str__())
        workspace.mkdir(parents=True, exist_ok=True)
        with open(workspace / 'addoninfo.txt', 'w+', encoding='utf-8') as f:
            save = {"AddonInfo": self._save_data}
            vdf.dump(save, f, True)
            new_addon_info = vdf.dumps(save, True)
        cmd = f'"{l4d2Config.l4d2_vpk_path}" a "{self._file}" addoninfo.txt'
        logger.info(f'执行命令:{cmd}')
        process = Popen(cmd, cwd=workspace, shell=True, text=True, stdout=PIPE, stderr=PIPE)
        result = ''
        for text in iter(process.stdout.readline, ''):
            result += text
            text = text.strip()
            signalBus.reWriteLogSignal.emit(text)
        # process.wait()
        logger.info(f'重写{self._file.stem} addoninfo文件内容输出日志\n{result}')
        if 'Tried to Write NULL file handle' in result:
            text = f'{self._file.stem}写入失败,请查看上方执行日志'
            status = False
        else:
            text = f'{self._file.stem}写入成功'
            status = True
        signalBus.reWriteLogSignal.emit(text)
        self.resultSignal.emit(status, new_addon_info, self._file.stem)

        logger.info('开始删除临时工作文件夹')
        shutil.rmtree(workspace, True)
        logger.debug('删除临时工作文件夹成功')


if __name__ == '__main__':
    _file = Path(r'E:\SteamLibrary\steamapps\common\Left 4 Dead 2\left4dead2\addons\map 活死人黎明加长版 - 副本.vpk')
    data = {
        "addonSteamAppID": "550",
        "addontitle": "活死人黎明加长版-副本4",
        "addonversion": "4.2",
        "addontagline": "Shop 'Til You Drop",
        "addonauthor": "darth_brush",
        "addonSteamGroupName": "Expansion Maps L4D2",
        "addonauthorSteamID": "darth_brush",
        "addonContent_Campaign": 1,
        "addonURL0": "https://steamcommunity.com/workshop/filedetails/?id=2083853186",
        "addonDescription": "The survivors must escape thru 6 maps starting in the doomed City of Dawn from L4D1, thru the city mall, and to its rooftop to find an escape!"
    }
    rewrite = ReWriteAddonInfoThread(_file, save_data=data)
    rewrite.run()
    # folder = Path(r'F:\pythonData\left4dead2\tmp\24e50dcb6b30a1fc6abb0c9cd50c84cf')
    # print(folder)
