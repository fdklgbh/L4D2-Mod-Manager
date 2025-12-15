# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: mod_info.py
from pydantic import BaseModel

from .mod_category import ModCategory


class ModInfo(BaseModel):
    title: str
    customTitle: str
    modCategory: ModCategory

