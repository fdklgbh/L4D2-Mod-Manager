# -*- coding: utf-8 -*-
# @Time: 2025/12/16
# @Author: Administrator
# @File: mod_info.py
from pydantic import Field

from shared.persistence.models import VPKInfo

from .base import Base
from .category import ModCategory


class ModInfo(Base):
    filename: str = Field(..., description="文件名")
    title: str = Field(default="", description="标题")
    customTitle: str = Field(default="", description="自定义标题")
    modCategory: ModCategory = Field(..., description="分类")
    pic: str = Field(
        default="", description="图片名称/路径(文件加中是图片名称, 路径是vpk中的)"
    )
    url: str = Field(default="", description="地址链接")
    addonInfo: dict = Field(default={}, description="addonInfo解析,修改内容")
    addonInfoContent: str = Field(default="", description="addonInfo修改后的内容")
    modComment: str = Field(default="", description="mod信息备注")
    addonAuthor: str = Field(default="", description="作者")
    addonDescription: str = Field(default="", description="描述")
    addonTagline: str = Field(default="", description="标语")

    @classmethod
    def from_vpk_info(cls, vpkInfo: VPKInfo):
        addonInfo: dict[str, dict] = vpkInfo.customAddonInfo or vpkInfo.addonInfo or {}
        return cls(
            filename=vpkInfo.fileName,
            title=addonInfo.get("addontitle", ""),
            customTitle=vpkInfo.customTitle,
            modCategory=ModCategory(
                category=vpkInfo.category, subCategory=vpkInfo.subCategory
            ),
            url=vpkInfo.url,
            addonInfo=addonInfo,
            addonInfoContent=vpkInfo.customAddonInfoContent or vpkInfo.addonInfoContent,
            modComment=vpkInfo.modComment or "",
            addonAuthor=addonInfo.get("addonauthor", ""),
            addonDescription=addonInfo.get("addondescription", ""),
            addonTagline=addonInfo.get("addontagline", ""),
        )


if __name__ == "__main__":
    import bisect

    modCategory = ModCategory(category="近战", subCategory="撬棍")
    info = ModInfo(title="xxx", modCategory=modCategory, filename="a")
    info1 = info.model_copy(update={"filename": "v"})
    info2 = info.model_copy(update={"filename": "a12"})
    info3 = info.model_copy(update={"filename": "ac"})
    info4 = info.model_copy(update={"filename": "sad"})
    info5 = info.model_copy(update={"filename": "a1"})
    datas = [info4, info5, info3, info1, info, info2]
    datas.sort(key=lambda x: x.filename)
    for i in datas:
        print(i)
    mod_info = info.model_copy(update={"filename": "d"})
    pos = bisect.bisect_left([x.filename for x in datas], mod_info.filename)
    print(pos)
    # res = next((k for k, v in ModInfo.model_fields.items() if v.description == '标题'), None)
    # print(res)
    del datas[7]
