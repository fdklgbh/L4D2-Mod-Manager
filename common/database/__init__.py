# -*- coding: utf-8 -*-
# @Time: 2025/1/14
# @Author: Administrator
# @File: __init__.py.py
from typing import Type, Union

from common.conf import WORKSPACE
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.orm import sessionmaker, close_all_sessions
from common.database.modules import *


class SqlAlchemyOption:
    def __init__(self):
        path = WORKSPACE / 'config' / 'test.db'
        self._engine = create_engine(f'sqlite:///{path}?charset=utf8', echo=False)
        Base.metadata.create_all(self._engine)
        self._session = sessionmaker(bind=self._engine)()

    def addType(self, name: str, type_='全部', commit=True):
        """
        添加切换mod信息分类+名称
        :param commit:
        :param name:
        :param type_:
        :return:
        """
        classification = Classification(name, type_)
        self._session.add(classification)
        if commit:
            self._session.commit()
        else:
            self._session.flush()
        # self._add_commit(classification)
        return classification.id

    def addClassificationInfo(self, type_id: int, vpkInfoIds: list[int], commit=False):
        """
        对应切换信息的id 以及对应的vpk id
        :param commit:
        :param type_id:
        :param vpkInfoIds:
        :return:
        """
        # for vpkInfoId in vpkInfoIds:
        #     info = ClassificationInfo(typeId=type_id, vpkInfoId=vpkInfoId)
        #     self._session.add(info)
        infos = [ClassificationInfo(typeId=type_id, vpkInfoId=vpkInfoId) for vpkInfoId in vpkInfoIds]
        self._session.add_all(infos)
        if commit:
            self.commit()

    def commit(self):
        self._session.commit()

    def deleteClassificationInfo(self, type_id: int, vpkInfoIds: list[int], commit=True):

        self._session.query(ClassificationInfo).filter(
            ClassificationInfo.typeId == type_id,
            ClassificationInfo.vpkInfoId.in_(vpkInfoIds)
        ).delete(synchronize_session=False)
        if commit:
            self._session.commit()

    def findSwitchVpkInfo(self, typeId: int):
        infos = self._session.query(ClassificationInfo).filter_by(typeId=typeId).all()
        data = {}
        for info in infos:
            vpkInfo: VPKInfo = info.vpkInfo
            fileName = vpkInfo.fileName
            data[fileName] = {
                'id': vpkInfo.id,
                'title': vpkInfo.customTitle or vpkInfo.addonInfo.get('addontitle', '未知标题'),
                'fatherType': vpkInfo.fatherType,
                'childType': vpkInfo.childType,
                'addonInfo': vpkInfo.addonInfo or {},
                'addonInfoContent': vpkInfo.customContent or vpkInfo.addonInfoContent
            }
        return dict(sorted(data.items()))

    def addVpkInfo(self, fileName, fatherType, childType, addonInfo: dict = None, addonInfoContent='', customTitle=''):
        """
        添加VPK信息
        :param customTitle:
        :param fileName: 文件名称
        :param fatherType: 一级目录
        :param childType: 二级目录
        :param addonInfo: addonInfo 原始数据
        :param addonInfoContent:
        :return:
        """
        try:
            vpkInfo = VPKInfo(fileName, fatherType, childType, addonInfo=addonInfo or {}, customTitle=customTitle,
                              addonInfoContent=addonInfoContent)
            self._add_commit(vpkInfo)
        except exc.IntegrityError:
            self._session.rollback()
            return self._vpkInfoToDict(self._session.query(VPKInfo).filter_by(fileName=fileName).first())
        return self._vpkInfoToDict(vpkInfo)

    def updateVpkInfoCustomTitle(self, fileName, customTitle):
        """
        设置自定义标题
        :param fileName:
        :param customTitle:
        :return:
        """
        vpkInfo = self._session.query(VPKInfo).filter_by(fileName=fileName).first()
        vpkInfo.customTitle = customTitle
        self._session.commit()

    def updateVpkInfoType(self, fileName, fatherType, childType):
        vpkInfo = self._session.query(VPKInfo).filter_by(fileName=fileName).first()
        vpkInfo.fatherType = fatherType
        vpkInfo.childType = childType
        self._session.commit()

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

    def getAllSwitchInfo(self):
        """
        获取类型
        :return:
        """
        return [[i.type, i.name, i.id] for i in self._session.query(Classification).all()]

    def getAddonInfo(self, fileName):
        vpkInfo = self._session.query(VPKInfo).filter_by(fileName=fileName).first()
        if vpkInfo is None:
            return {}
        return self._vpkInfoToDict(vpkInfo)

    def get_type_info(self, fatherType, childType):
        if fatherType == '全部':
            filter_kw = {'childType': childType}
        else:
            filter_kw = {'fatherType': fatherType, 'childType': childType}
        vpkInfos = self._session.query(VPKInfo).filter_by(**filter_kw).order_by(VPKInfo.fileName).all()
        result = {}
        for vpkInfo in vpkInfos:
            result[vpkInfo.fileName] = self._vpkInfoToDict(vpkInfo)
        return result

    @staticmethod
    def _vpkInfoToDict(vpkInfo: Union[Type[VPKInfo], VPKInfo]):
        return {
            'id': vpkInfo.id,
            'fatherType': vpkInfo.fatherType,
            'childType': vpkInfo.childType,
            'title': vpkInfo.customTitle or vpkInfo.addonInfo.get('addontitle', ''),
            'addonInfo': vpkInfo.addonInfo,
            'content': vpkInfo.customContent or vpkInfo.addonInfoContent
        }

    def changeClassificationName(self, typeId, name, commit=True):
        res = self._session.query(Classification).filter_by(id=typeId).first()
        res.name = name
        if commit:
            self._session.commit()


db = SqlAlchemyOption()

__all__ = ['db']

if __name__ == '__main__':
    # id_ = db.addType('asddasd')
    # print(db.findSwitchVpkInfo(1))

    # sql.addInfo(id_, ['按设计大奖', '啊看是否'])
    # sql.addInfo(1, [f'{i}-按实际花费' for i in range(10000)])
    # sql.deleteType(1)
    # res = db.getAllSwitchInfo()
    # print(res)
    db.disconnect()
