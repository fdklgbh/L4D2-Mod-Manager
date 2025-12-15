# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: database.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()

__all__ = ['Base']