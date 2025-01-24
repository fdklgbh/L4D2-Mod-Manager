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
    name = Column(String, comment='类型名称')
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
    serialNumber = Column(Integer, comment='排序', nullable=False)

    def __init__(self, typeId: int, vpkInfoId, serialNumber: int):
        self.typeId = typeId
        self.vpkInfoId = vpkInfoId
        self.serialNumber = serialNumber


# 数据表数据不可删除
class VPKInfo(Base):
    __tablename__ = "vpkInfo"
    __table_args__ = {'comment': "vpk信息"}

    id = Column(Integer, primary_key=True)
    fileName = Column(String, comment='VPK文件名称', unique=True)
    fatherType = Column(String, comment='一级分类', default='全部')
    childType = Column(String, comment='二级分类', default='')
    customTitle = Column(String, comment='mod自定义名称', default='')
    addonInfo = Column(JSON, comment='原始addonInfo文件解析内容', default={})
    addonInfoContent = Column(String, comment='addonInfo原始内容', default='')
    customAddonInfo = Column(JSON, comment='addonInfo解析,修改内容', default={})
    customAddonInfoContent = Column(String, comment='addonInfo修改后的内容', default='')
    classificationInfo = relationship("ClassificationInfo", back_populates="vpkInfo")
    url = Column(String, comment='mod获取链接', default='')
    modComment = Column(String, comment='mod信息备注', default='')

    def __init__(self, fileName: str, fatherType: str, childType: str, addonInfo: dict = None, customTitle='',
                 addonInfoContent: str = '', customAddonInfoContent: str = '', customAddonInfo='', url: str = '',
                 modComment: str = ''):
        if not addonInfo:
            addonInfo = {}
        if not customAddonInfo:
            customAddonInfo = addonInfo
        if not customTitle:
            customTitle = customAddonInfo.get('addontitle', '')
        self.fileName = fileName
        self.fatherType = fatherType or '其他'
        self.childType = childType or ''
        self.customTitle = customTitle
        self.addonInfo = addonInfo
        self.customAddonInfo = customAddonInfo
        self.addonInfoContent = addonInfoContent or ''
        self.customAddonInfoContent = customAddonInfoContent or addonInfoContent
        self.url = url
        self.modComment = modComment


__all__ = ['Base', 'Classification', 'ClassificationInfo', 'VPKInfo']
