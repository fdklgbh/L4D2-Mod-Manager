# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: logger_setup.py
from functools import partial

from loguru import logger

from core import appConstants


def level_filter(level: str, record):
    return record["level"].name == level.upper()


def logger_setup():
    logger.info("logger_setup")
    log_levels = {
        "DEBUG": "debug_{time:YYYY-MM-DD}.log",
        "INFO": "info_{time:YYYY-MM-DD}.log",
        "WARNING": "warning_{time:YYYY-MM-DD}.log",
        "ERROR": "error_{time:YYYY-MM-DD}.log",
        "CRITICAL": "critical_{time:YYYY-MM-DD}.log",
    }

    # 为每个日志级别添加文件处理器
    for level, log_file in log_levels.items():
        logger.add(
            str(appConstants.LogPath / log_file),
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
            level=level,
            filter=partial(level_filter, level),
            rotation="00:00",  # 每天午夜轮转
            retention="7 days",  # 保留7天
            compression="zip",  # 使用zip压缩
            encoding="utf-8",
            enqueue=True,  # 异步写入，提高性能
            backtrace=True,  # 记录异常堆栈
            diagnose=True,  # 显示变量值
        )
    logger.info("logger_setup success")


logger_setup()

__all__ = []
