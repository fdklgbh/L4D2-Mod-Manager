# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: classification.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class Classification(Base):
    __tablename__ = "classification"
    __table_args__ = {"comment": "切换整套mod名称信息"}

    id = Column(Integer, primary_key=True)
    name = Column(String, comment="类型名称")
    type = Column(String, comment="mod分类,默认为全部", default="全部")
    classificationInfo = relationship(
        "ClassificationInfo",
        back_populates="classification",
        cascade="all, delete-orphan",
    )
