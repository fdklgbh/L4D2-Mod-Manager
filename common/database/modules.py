# -*- coding: utf-8 -*-
# @Time: 2025/1/14
# @Author: Administrator
# @File: modules.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Classification(Base):
    __tablename__ = "Classification"

    id = Column(Integer, primary_key=True)
    name = Column(String, comment='类型名称')
    type = Column(String, comment='mod分类,默认为全部')
    classification_infos = relationship("ClassificationInfo", backref="classification", cascade="all, delete-orphan")

    def __init__(self, name, type_='全部'):
        self.name = name
        self.type = type_


class ClassificationInfo(Base):
    __tablename__ = "ClassificationInfo"

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('Classification.id'), comment='外键,对应Classification的id')
    data = Column(JSON, comment='数据')

    def __init__(self, type_id: int, data: list):
        self.type_id = type_id
        self.data = data


__all__ = ['Base', 'Classification', 'ClassificationInfo']
