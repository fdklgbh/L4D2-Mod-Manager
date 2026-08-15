# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: logger_setup.py
import sys

from loguru import logger

from shared.app import appConstants
from shared.runtime import signalBus


def level_filter(level: str, record):
    return record["level"].name == level.upper()


def logger_setup():
    logger.bind(tag="logger_setup").info("logger_setup")
    formatter = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {extra[tag]}:{function}:{line} - {message}"
    logger.remove()
    if appConstants.DEBUG:
        logger.add(
            sink=sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{extra[tag]}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
                "<level>{message}</level>"
            ),
            colorize=True,  # 启用 ANSI 颜色（仅对终端有效）
            level="DEBUG",
        )
    #     日志页面
    logger.add(lambda msg: signalBus.loggerSignal.emit(msg), format=formatter)
    logger.add(
        str(appConstants.LogPath / "L4d2ModManager-{time:YYYY-MM-DD}.log"),
        format=formatter,
        level="DEBUG",
        rotation="00:00",  # 每天午夜轮转
        retention="7 days",  # 保留7天
        compression="zip",  # 使用zip压缩
        encoding="utf-8",
        enqueue=True,  # 异步写入，提高性能
        backtrace=True,  # 记录异常堆栈
        diagnose=True,  # 显示变量值
    )
    logger.bind(tag="logger_setup").info("logger_setup success")


logger_setup()

__all__ = []
