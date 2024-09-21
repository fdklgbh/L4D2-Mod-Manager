# -*- coding: utf-8 -*-
# @Time: 2023/12/25
# @Author: Administrator
# @File: __init__.py.py

from common.config.main_config import L4d2Config
from common.config.vpk_config import VPKConfig

l4d2Config = L4d2Config()

vpkConfig = VPKConfig()

__all__ = ['l4d2Config', 'vpkConfig']
