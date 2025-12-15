# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: revision.py
import sys

from alembic import command
from alembic.config import Config

if len(sys.argv) != 2:
    raise ValueError('需要message作为脚本')

alembic_cfg = Config('alembic.ini')
command.revision(alembic_cfg, sys.argv[-1], True)

