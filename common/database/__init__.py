# -*- coding: utf-8 -*-
# @Time: 2025/1/14
# @Author: Administrator
# @File: __init__.py.py
from common.conf import WORKSPACE
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, close_all_sessions
from common.database.modules import *

class SqlAlchemyOption:
    def __init__(self):
        # todo 检查config文件夹不存在,是否能先创建
        path = WORKSPACE / 'config' / 'test.db'
        self._engine = create_engine(f'sqlite:///{path}?charset=utf8', echo=True)
        Base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)()

    def addType(self, name: str):
        classification = Classification(name)
        self._add_commit(classification)
        print(classification.id)
        return classification.id

    def addInfo(self, type_id: int, data: list[str]):
        info = ClassificationInfo(type_id=type_id, data=data)
        self._add_commit(info)

    def findInfo(self, type_id: int):
        infos = self._session.query(ClassificationInfo).filter_by(type_id=type_id).all()
        for info in infos:
            print('info', info.data)

    def deleteType(self, type_id: int):
        classification = self._session.get(Classification, type_id)
        self._del_commit(classification)

    def _add_commit(self, obj):
        self._session.add(obj)
        self._session.commit()

    def _del_commit(self, obj):
        self._session.delete(obj)
        self._session.commit()

    def disconnect(self):
        close_all_sessions()


db = SqlAlchemyOption()

__all__ = ['db']

if __name__ == '__main__':
    # id_ = sql.addType('asddasd')
    # sql.addInfo(id_, ['按设计大奖', '啊看是否'])
    # sql.addInfo(1, [f'{i}-按实际花费' for i in range(10000)])
    # sql.deleteType(1)
    db.findInfo(1)
    db.disconnect()
