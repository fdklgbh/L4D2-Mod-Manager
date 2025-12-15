# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: vpkInfo.py
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from core.database import Base


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
