# -*- coding: utf-8 -*-
# @Time: 2023/12/12 23:08
# @Author: Administrator
# @File: conf.py
from enum import Enum, unique
from pathlib import Path

# from common.config.main_config import setting_cfg
WINDOWS_TITLE = 'L4D2 Mod管理器'

VERSION = 'Beta 1.0.1'

DATA = ['addontitle', 'addonauthor', 'addondescription', 'addonversion', 'addoncontent_campaign', 'addonsteamappid',
        'addontagline', 'addonauthorsteamid', 'addonsteamgroupname', 'addonurl0',
        'addoncontent_survivaladdoncontent_versusaddoncontent_scavenge', 'addoncontent_prefab',
        'addoncontent_spray', 'addoncontent_backgroundmovie', 'content_weapon', 'content_weaponmodel',
        'addondescription_locale', 'addoncontent_map', 'addoncontent_skin', 'addoncontent_weapon',
        'addoncontent_bossinfected', 'addoncontent_commoninfected', 'addoncontent_survivor', 'addoncontent_sound',
        'addoncontent_music', 'addoncontent_script', 'addoncontent_prop']

MAP_KEY = [
    'addoncontent_campaign', 'addoncontent_map'
]

NEED_DATA = [
    'addontitle', 'addonauthor', 'addondescription', 'addontagline'
]


@unique
class ModType(Enum):
    JINZHAN = 'jinzhan'
    WEAPONS = 'weapons'
    SURVIVORS = 'survivors'
    INFECTED = 'infected'
    DRUG = 'drug'
    THROW = 'throw'
    MAP = 'map'

    def __str__(self):
        return self.value

    def data(self):
        return MOD_TYPE.get(self.value.lower())

    def __eq__(self, other):
        return self.value == other

    @classmethod
    def keys_convert(cls):
        data = []
        for key, value in MOD_TYPE_KEY.items():
            data.append(value)
        return data

    @classmethod
    def type_key(cls):
        data = []
        for key, value in MOD_TYPE_KEY.items():
            tmp: dict = MOD_TYPE.get(key)
            if tmp:
                data.append({MOD_TYPE_KEY.get(key): list(tmp.keys())})
            else:
                data.append(MOD_TYPE_KEY.get(key))
        return data

    @classmethod
    def keys(cls):
        return list(MOD_TYPE_KEY.keys())

    @classmethod
    def child_keys(cls):
        type_key = cls.type_key()
        child_keys = []
        for data in type_key:
            if isinstance(data, dict):
                child_keys.extend(list(data.values())[0])
        return child_keys

    @classmethod
    def value_to_key(cls, value):
        return VALUE_TO_KEY.get(value)

    @classmethod
    def key_to_value(cls, key):
        return MOD_TYPE_KEY.get(key)

    @classmethod
    def weapons_goods(cls):
        """
        排除 人物 特感
        :return:
        """
        new_dict = dict(MOD_TYPE)
        new_dict.pop(cls.SURVIVORS.value)
        new_dict.pop(cls.INFECTED.value)
        return new_dict


MOD_TYPE = {
    # 人物
    "survivors": {
        "比尔": ['bill', 'namvet'],
        "弗朗西斯": ['francis', 'biker'],
        "路易斯": ['louis', 'manager'],
        '佐伊': ['zoey', 'teenangst'],
        "ellis": ['mechanic', 'ellis'],
        "coach": ["教练", 'coach'],
        "nick": ['gambler', 'nick'],
        "rochelle": ["rochelle", "producer"]
    },
    # 特感
    "infected": {
        "胖子": ['boomer', 'boomette'],
        "猎人": ['hunter'],
        "舌头": ['smoker'],
        "坦克": ['tank', 'hulk'],
        "猴子": ['jockey'],
        "口水": ['spitter'],
        "妹子": ['witch']

    },
    # 武器
    "weapons": {
        "手枪": ["pistol"],
        "马格南": ["magnum", "deagle", 'desert eagle'],
        "木喷": ["pump shotgun", 'shotgun wood'],
        "铁喷": ["chrome shotgun"],
        "一代连喷": ["autoshotgun", 'xm1014'],
        "二代连喷": ["combat shotgun", 'spas', 'autoshot m4super'],
        "乌兹": ['uzi', 'smg'],
        "mac-10": ['silenced smg'],
        "mp5": ['mp5'],
        "ak": ["ak47", 'ak-47'],
        "m4": ["m16", "m4a1", "rifle m16a2"],
        "三连发": ["combat rifle", 'scar', 'desert rifle'],
        "sg552": [],
        "鸟狙": ['scout'],
        # 十五连
        "木狙": ['hunting rifle', '猎枪', 'sniper mini14'],
        # 30连
        "连狙": ['military sniper', 'sniper military'],
        "大狙": ['awp'],
        "机枪": ['m60'],
        "榴弹枪": ['榴弹', 'grenade launcher'],
        '加特林枪台': ['minigun'],
        '重机枪': ['50cal']
    },
    # 近战
    "jinzhan": {
        "砍刀": ['machete'],
        "武士刀": ['katana'],
        "撬棍": ["crowbar"],
        "消防斧": ['fire axe'],
        "电锯": ['chainsaw'],
        "小刀": ['knife'],
        "防爆盾": ['riot shield'],
        "平底锅": ['frying pan'],
        "吉他": ['guitar'],
        "警棍": ['nightstick', 'shockbaton'],
        "棒球棒": ['baseball bat'],
        "板球棒": ['cricket bat'],
        "高尔夫": ['golf club'],
        "干草叉": ['pitchfork'],
        "铁锹": ['shovel']
    },
    # 医疗
    "drug": {
        "医疗包": ['medkit', 'first aid kit'],
        "电击器": ["defibrillator"],
        "止痛药": ['pain pills', 'pills'],
        "肾上腺素": ['adrenaline', 'shot', 'epinephrine']
    },
    # 投掷
    "throw": {
        "土制炸弹": ['pipebomb', '土制'],
        "燃烧瓶": ['molotov'],
        "胆汁": ['bile bomb', 'vomitjar', 'bile flask']
    }
}

MOD_TYPE_KEY = {
    "survivors": '幸存者',
    "infected": "特感",
    "weapons": "武器",
    "jinzhan": '近战',
    'drug': '医疗品',
    "throw": "投掷",
    'map': '地图',
    'other': '其他'
}

VALUE_TO_KEY = {value: key for key, value in MOD_TYPE_KEY.items()}
CustomData = {}

WORKSPACE = Path(__file__).parent

if __name__ == '__main__':
    print(ModType.child_keys())
