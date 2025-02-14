# -*- coding: utf-8 -*-
# @Time: 2025/1/14
# @Author: Administrator
# @File: __init__.py.py
import logging
from typing import Type, Union
from logging.handlers import RotatingFileHandler
from common.conf import CONFIG, LogPath
from sqlalchemy import exc, create_engine, desc, text
from sqlalchemy.orm import sessionmaker, close_all_sessions, scoped_session
from common.database.modules import *


class SqlAlchemyOption:
    def __init__(self):
        path = CONFIG / 'L4d2ModManager.db'
        logPath = LogPath / 'SQLAlchemy.log'
        echo = False
        self._engine = create_engine(f'sqlite:///{path}?charset=utf8', echo=echo, logging_name='SQLAlchemy',
                                     pool_size=20, max_overflow=40, pool_timeout=30, pool_recycle=1800,
                                     connect_args={"check_same_thread": False})
        if echo:
            handler = RotatingFileHandler(logPath, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf8')
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            handler.setFormatter(formatter)
            self._engine.logger.logger.addHandler(handler)
        self.update_db()
        Base.metadata.create_all(self._engine)
        SessionFactory = sessionmaker(bind=self._engine)
        # Session = scoped_session(SessionFactory)
        self._session = scoped_session(SessionFactory)

    def update_db(self):
        with self._engine.connect() as connection:
            # classificationInfo 表添加 enable 字段 范围为0, 1,默认为1
            result = connection.execute(text("PRAGMA table_info(classificationInfo);")).fetchall()
            column_names = [column[1] for column in result]
            if 'enable' not in column_names:
                # 如果没有 'enable' 列，则添加该列
                sql = """
                ALTER TABLE classificationInfo ADD COLUMN enable INTEGER NOT NULL DEFAULT 1 CHECK (enable IN (0, 1));
                """
                connection.execute(text(sql))

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

    def getClassificationInfoMaxNumber(self, typeId: int):
        """
        获取classificationInfo表typeId对应的最大序号
        :param typeId:
        :return:
        """
        return self._session.query(ClassificationInfo).filter_by(typeId=typeId).order_by(
            desc(ClassificationInfo.serialNumber)).first().serialNumber

    def addClassificationInfo(self, type_id: int, vpkInfoIds: list[int], startNumber, commit=False):
        """
        对应切换信息的id 以及对应的vpk id
        :param commit:
        :param type_id:
        :param vpkInfoIds:
        :param startNumber
        :return:
        """
        # for vpkInfoId in vpkInfoIds:
        #     info = ClassificationInfo(typeId=type_id, vpkInfoId=vpkInfoId)
        #     self._session.add(info)
        infos = []
        for vpkInfoId in vpkInfoIds:
            # 使用当前的 startNumber 作为 serialNumber
            info = ClassificationInfo(typeId=type_id, vpkInfoId=vpkInfoId, serialNumber=startNumber)
            infos.append(info)
            # 更新 startNumber
            startNumber += 1
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
                'addonInfoContent': vpkInfo.customAddonInfoContent or vpkInfo.addonInfoContent
            }
        return dict(sorted(data.items()))

    def findSpecificFilesInfo(self, fileNames: list[str]) -> list:
        existing_files = self._session.query(VPKInfo.fileName).filter(VPKInfo.fileName.in_(fileNames)).all()
        return list({file[0] for file in existing_files})

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

    def updateVpkInfo(self, fileName, title, content, addonInfo):
        if not addonInfo:
            addonInfo = {}
        result = self._session.query(VPKInfo).filter_by(fileName=fileName).first()
        result.customTitle = title or addonInfo.get('addontitle')
        if not result.addonInfo:
            result.addonInfo = addonInfo
        if not result.addonInfoContent:
            result.addonInfoContent = content
        result.customAddonInfo = addonInfo
        result.customAddonInfoContent = content
        self.commit()

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

    def getAddonInfoType(self, fileName):
        vpkInfo = self._session.query(VPKInfo).filter_by(fileName=fileName).first()
        if vpkInfo is None:
            return {}
        return {'fatherType': vpkInfo.fatherType, 'childType': vpkInfo.childType, 'id': vpkInfo.id}

    def vpkInfoChangeType(self, fileName, fatherType, childType, oldFatherType, oldChildType) -> list[int]:
        if not (vpkInfo := self._getVpkInfoByFileName(fileName)):
            return []
        vpkInfo.fatherType = fatherType
        vpkInfo.childType = childType
        classificationInfo: list[ClassificationInfo] = vpkInfo.classificationInfo
        remove_id = self._checkClassification(classificationInfo, fatherType)
        self.commit()
        return remove_id

    def _checkClassification(self, infos: list[ClassificationInfo], fatherType):
        remove_classification_id = []
        if not infos:
            return remove_classification_id
        for info in infos:
            if (db_classification_type := info.classification.type) == fatherType:
                continue
            if db_classification_type == '全部':
                if fatherType != '地图':
                    continue
            classification: Classification = info.classification
            if len(classification.classificationInfo) > 1:
                self._session.delete(info)
            else:
                remove_classification_id.append(classification.id)
                self._session.delete(classification)
        return remove_classification_id

    def vpkInfoChangeChildType(self, fileName, childType):
        if not (vpkInfo := self._getVpkInfoByFileName(fileName)):
            return
        vpkInfo.childType = childType
        self.commit()

    def _getVpkInfoByFileName(self, fileName) -> Union[None, VPKInfo]:
        return self._session.query(VPKInfo).filter_by(fileName=fileName).first()

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
            'content': vpkInfo.customAddonInfoContent or vpkInfo.addonInfoContent
        }

    def changeClassificationName(self, typeId, name, commit=True):
        res = self._session.query(Classification).filter_by(id=typeId).first()
        res.name = name
        if commit:
            self._session.commit()

    def getTypeAllFileName(self, fatherType: str):
        """
        查找大分类的所有文件
        :param fatherType: 分类名称
        :return:
        """
        if fatherType == '全部':
            res = self._session.query(VPKInfo).filter(VPKInfo.fatherType != '地图').all()
        else:
            res = self._session.query(VPKInfo).filter_by(fatherType=fatherType).all()
        return [file.fileName for file in res]

    def getTypeEnableFileNameNumber(self, typeId: int) -> dict:
        """
        查找将要启用mod文件 文件名以及排序
        :param typeId:
        :return:
        """
        res = self._session.query(ClassificationInfo).filter_by(typeId=typeId).order_by(
            ClassificationInfo.serialNumber).all()
        return {info.vpkInfo.fileName: info.serialNumber for info in res}

    def setCustomTitle(self, fileName, title, commit=True):
        res = self._getVpkInfoByFileName(fileName)
        if res:
            if title:
                res.customTitle = title
            else:
                res.customTitle = res.customAddonInfo.get('addontitle', '')
            if commit:
                self.commit()
            return res.customAddonInfo.get('addontitle', '')


db = SqlAlchemyOption()

__all__ = ['db']

if __name__ == '__main__':
    import json

    # id_ = db.addType('asddasd')
    # print(db.findSwitchVpkInfo(1))
    # res = db.session.query(VPKInfo).filter_by(id=5).first()
    # for info in res.classificationInfo:
    #     info: ClassificationInfo
    #     print(info.typeId)
    #     print(info.classification.name)
    #     tmp: Classification = info.classification
    #     print(tmp.classificationInfo)
    #     print('xxxxx')

    # db.commit()
    # sql.addInfo(id_, ['按设计大奖', '啊看是否'])
    # sql.addInfo(1, [f'{i}-按实际花费' for i in range(10000)])
    # sql.deleteType(1)
    # res = db.getAllSwitchInfo()
    # print(res)
    # all_data = db.getTypeAllFileName('近战')
    enable_data = db.getAddonInfo('2411461841')
    print(json.dumps(enable_data, ensure_ascii=False, indent=4))
    db.disconnect()
