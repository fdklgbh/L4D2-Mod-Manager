# -*- coding: utf-8 -*-
# @Time: 2024/11/13
# @Author: Administrator
# @File: loggerConfig.py
import logging
import colorlog

from common.Bus import signalBus


class CustomHandler(logging.Handler):
    def emit(self, record):
        log_message = self.format(record)
        log_message = log_message.replace(record.levelname, record.levelname[0])
        signalBus.loggerSignal.emit(log_message)
        # print(log_message)
        return log_message


def get_logger(level=logging.DEBUG):
    logger = logging.getLogger('L4D2Manager')
    logger.setLevel(level)
    handler = CustomHandler()
    formatter = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'
    color_formatter = colorlog.ColoredFormatter(formatter, datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(color_formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(color_formatter)
    logger.addHandler(stream_handler)
    return logger


__all__ = ['get_logger']
