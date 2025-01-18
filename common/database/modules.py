# -*- coding: utf-8 -*-
# @Time: 2025/1/14
# @Author: Administrator
# @File: modules.py
from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Classification(Base):
    __tablename__ = "classification"

    id = Column(Integer, primary_key=True)
    name = Column(String, comment='类型名称', unique=True)
    type = Column(String, comment='mod分类,默认为全部', default='全部')
    classificationInfo = relationship("ClassificationInfo", back_populates="classification",
                                      cascade="all, delete-orphan")

    def __init__(self, name: str, type_: str = '全部'):
        self.name = name
        self.type = type_


class ClassificationInfo(Base):
    __tablename__ = "classificationInfo"

    id = Column(Integer, primary_key=True)
    typeId = Column(Integer, ForeignKey('classification.id'), comment='外键,对应Classification的id')
    vpkInfoId = Column('vpkInfoId', Integer, ForeignKey('vpkInfo.id'))
    classification = relationship("Classification", back_populates="classificationInfo", viewonly=True)
    vpkInfo = relationship("VPKInfo", back_populates="classificationInfo", viewonly=True)

    def __init__(self, typeId: int, vpkInfoId):
        self.typeId = typeId
        self.vpkInfoId = vpkInfoId


class VPKInfo(Base):
    __tablename__ = "vpkInfo"
    __table_args__ = {'comment': "vpk信息"}

    id = Column(Integer, primary_key=True)
    fileName = Column(String, comment='VPK文件名称', unique=True)
    fatherType = Column(String, comment='一级分类', default='全部')
    childType = Column(String, comment='二级分类', default='')
    customTitle = Column(String, comment='mod自定义名称', default='')
    addonInfo = Column(JSON, comment='addonInfo文件解析内容', default={})
    addonInfoContent = Column(String, comment='addonInfo原始内容', default='')
    customContent = Column(String, comment='addonInfo修改后的内容', default='')
    classificationInfo = relationship("ClassificationInfo", back_populates="vpkInfo")

    def __init__(self, fileName: str, fatherType: str, childType: str, addonInfo: dict = None, customTitle='',
                 addonInfoContent: str = '', customContent: str = ''):
        self.fileName = fileName
        self.fatherType = fatherType or '其他'
        self.childType = childType or ''
        self.customTitle = customTitle or ''
        self.addonInfo = addonInfo or {}
        self.addonInfoContent = addonInfoContent or ''
        self.customContent = customContent or ''


__all__ = ['Base', 'Classification', 'ClassificationInfo', 'VPKInfo']
