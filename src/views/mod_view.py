# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: mod_view.py
from pathlib import Path
from .components import ModShowTableView
from .ui import Ui_modShowView
from PyQt5.QtWidgets import QWidget
from qfluentPackage.widget import CSegmentedWidget


class ModuleStacked(QWidget, Ui_modShowView):
    def __init__(self, path: Path):
        super().__init__()
        self.setupUi(self)
        self.proxy_search =


class ModulesInterfaceSplitter(CSegmentedWidget):
    def __init__(self, folder_path: list[Path], parent=None):
        super().__init__(parent=parent)
        if folder_path:
            for path in folder_path:
                self.module_interface = ModuleStacked(path)
                text = path.name.title()
                self.addSubInterface(self.module_interface, text, path)
                if l4d2Config.is_addons(path):
                    self.setDefaultCurrent(self.module_interface)
        if self.getItemsNum() <= 1:
            self.pivot.setVisible(False)
