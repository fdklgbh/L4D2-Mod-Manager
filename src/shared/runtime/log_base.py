# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: log_base.py
from loguru import logger


class LogBase:
    TAG = ""

    # def __init__(self, *args, **kwargs):
    #     print("LogBase", args, kwargs)
    #     super().__init__()

    @property
    def logger(self):
        assert self.TAG, "未定义TAG"
        return logger.bind(tag=self.TAG)
