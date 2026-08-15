# -*- coding: utf-8 -*-
# @Time: 2025/12/21
# @Author: Administrator
# @File: updateDb.py
from alembic import command
from alembic.config import Config

from shared.app import appConstants

cfg = Config(
    "alembic.ini"
    if not appConstants.DEBUG
    else (appConstants.workSpace.parent / "alembic.ini")
)
command.upgrade(cfg, "head")
print("success")
