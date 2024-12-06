# -*- coding: utf-8 -*-
# @Time: 2024/11/13
# @Author: Administrator
# @File: loggerConfig.py
import logging
import colorlog
from common.conf import LogPath
from common.Bus import signalBus
from logging.handlers import RotatingFileHandler

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
    msg_formatter = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s'

    formatter = logging.Formatter(msg_formatter)
    logger.addHandler(handler)
    handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    color_formatter = colorlog.ColoredFormatter(msg_formatter, datefmt='%Y-%m-%d %H:%M:%S')
    stream_handler.setFormatter(color_formatter)
    logger.addHandler(stream_handler)
    log_file = LogPath / 'L4d2ModManager.log'
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


__all__ = ['get_logger']
