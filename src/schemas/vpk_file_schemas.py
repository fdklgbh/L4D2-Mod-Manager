# -*- coding: utf-8 -*-
# @Time: 2025/12/18
# @Author: Administrator
# @File: vpk_file_schemas.py

from pydantic import BaseModel, Field


class VPKFilePath(BaseModel):
    mdl: list[str] = Field(default=[], description="mdl文件目录")
    vtf: list[str] = Field(default=[], description="vtf文件目录")
    vmt: list[str] = Field(default=[], description="vmt文件目录")
    path: list[str] = Field(
        default=[], description="排除地图,missions vtx vvd phy jpg文件目录"
    )


__all__ = ["VPKFilePath"]
