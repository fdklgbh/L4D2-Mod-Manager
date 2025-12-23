# -*- coding: utf-8 -*-
# @Time: 2025/12/13
# @Author: Administrator
# @File: classificationInfo.py
from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from core.database import Base


class ClassificationInfo(Base):
    __tablename__ = "classificationInfo"

    id = Column(Integer, primary_key=True)
    typeId = Column(
        Integer, ForeignKey("classification.id"), comment="外键,对应Classification的id"
    )
    vpkInfoId = Column("vpkInfoId", Integer, ForeignKey("vpkInfo.id"))
    classification = relationship(
        "Classification", back_populates="classificationInfo", viewonly=True
    )
    vpkInfo = relationship(
        "VPKInfo", back_populates="classificationInfo", viewonly=True
    )
    serialNumber = Column(Integer, comment="排序", nullable=False)
    enable = Column(Integer, comment="是否启用", default=1, nullable=False)

    __table_args__ = (
        CheckConstraint("enable IN (0, 1)", name="check_enable_value"),
        {"comment": "切换mod组信息"},
    )
