# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: modShowModel.py
from pathlib import Path

from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QWidget


class modShowModel(QAbstractTableModel):
    def __init__(self, parent: QWidget, headers: list[str], folder_path: Path):
        super().__init__(parent=parent)
