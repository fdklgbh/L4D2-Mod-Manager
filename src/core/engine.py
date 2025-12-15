# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: engine.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .constants import appConstants

engine = create_engine(appConstants.dbUrl, echo=False, logging_name='SQLAlchemy',
                       pool_size=50, max_overflow=100, pool_timeout=30, pool_recycle=1800,
                       connect_args={"check_same_thread": False})

class DBBase:
    def __init__(self):
        SessionFactory = sessionmaker(bind=engine)
        self._session = scoped_session(SessionFactory)


__all__ = ['DBBase']