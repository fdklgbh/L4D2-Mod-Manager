# -*- coding: utf-8 -*-

"""页面数据库 service 的公共基类。"""

from .engine import database_service


class BasePageService:
    """所有页面数据库 service 的公共基类。"""

    @property
    def session(self):
        """获取当前线程的数据库 session。"""
        return database_service.session

    def commit(self):
        """提交当前事务。"""
        database_service.commit()

    def rollback(self):
        """回滚当前事务。"""
        database_service.rollback()

    def disconnect(self):
        """关闭应用使用的数据库服务。"""
        database_service.disconnect()


__all__ = ["BasePageService"]
