# -*- coding: utf-8 -*-
# @Time: 2025/12/14
# @Author: Administrator
# @File: enums.py
from enum import Enum


class EnumBase(Enum):
    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return str(self.value)


class MenuCategory(str, EnumBase):
    MELEE = "近战"
    WEAPON = "武器"
    SURVIVOR = "幸存者"
    INFECTED = "特感"
    MEDICAL = "医疗品"
    THROW = "投掷"
    MAP = "地图"
    AMMO = "弹药"
    ITEMS = "杂项"
    UI = "UI"
    VEHICLE = "载具"
    TEXTURE_EFFECTS = "材质特效"
    ACTION = "动作"
    OTHER = "其他"


__all__ = ["MenuCategory"]

if __name__ == "__main__":
    print([type(i) for i in MenuCategory])
