# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: engine.py
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions, scoped_session, sessionmaker

from ..app import appConstants


class DatabaseService:
    """统一管理数据库引擎、连接池和 scoped session。"""

    def __init__(self):
        """只初始化一次数据库引擎和当前线程 session。"""
        self._engine = create_engine(
            appConstants.dbUrl,
            echo=False,
            logging_name="SQLAlchemy",
            pool_size=50,
            max_overflow=100,
            pool_timeout=30,
            pool_recycle=1800,
            connect_args={"check_same_thread": False},
        )
        print(f"{appConstants.dbUrl}")
        self._session_factory = sessionmaker(bind=self._engine)
        self._session = scoped_session(self._session_factory)

    @property
    def session(self):
        """获取当前线程的数据库 session。"""
        return self._session()

    def commit(self):
        """提交当前事务。"""
        self.session.commit()

    def rollback(self):
        """回滚当前事务。"""
        self.session.rollback()

    def disconnect(self):
        """关闭所有 session 和数据库连接。"""
        close_all_sessions()
        self._session.remove()
        self._engine.dispose()


database_service = DatabaseService()


def dispose():
    """关闭应用使用的数据库服务。"""
    database_service.disconnect()


__all__ = ["DatabaseService", "database_service", "dispose"]
