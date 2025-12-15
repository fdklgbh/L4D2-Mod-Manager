# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: view_base.py
from loguru import logger


class ViewBase:
    TAG = ''

    @property
    def logger(self):
        assert not self.TAG, '未定义TAG'
        return logger.bind(tag=self.TAG)
