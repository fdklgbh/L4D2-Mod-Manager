# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: mod_category.py
from schemas.base import Base


class ModCategory(Base):
    category: str
    subCategory: str = ""


__all__ = ["ModCategory"]
