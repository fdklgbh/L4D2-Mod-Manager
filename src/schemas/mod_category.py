# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: mod_category.py

from pydantic import BaseModel


class ModCategory(BaseModel):
    category: str
    subCategory: str


__all__ = ['ModCategory']
