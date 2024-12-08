# -*- coding: utf-8 -*-
# @Time: 2023/12/12 23:08
# @Author: Administrator
# @File: conf.py
from enum import Enum, unique
from pathlib import Path

# from common.config.main_config import setting_cfg
WINDOWS_TITLE = 'L4D2 Mod管理器'

IS_DEV = False

VERSION = '1.1.1'
if IS_DEV:
    VERSION += ' dev'

AUTHOR = 'fdklgbh'

YEAR = 2024

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

# 展示数据
NEED_DATA = [
    'addontitle', 'addonauthor', 'addondescription', 'addontagline'
]


@unique
class ModType(Enum):
    JINZHAN = '近战'
    WEAPONS = '武器'
    SURVIVORS = '幸存者'
    INFECTED = '特感'
    DRUG = '医疗品'
    THROW = '投掷'
    MAP = '地图'
    AMMO = '弹药'
    ITEMS = '杂项'

    def __str__(self):
        return self.value

    def data(self):
        return CHILE_MENUS.get(self.value)

    def __eq__(self, other):
        return self.value == other

    @classmethod
    def type_menu_info(cls):
        """
        分类 大分类 小分类
        生成菜单
        :return:
        """
        data = []
        for value in FATHER_MENUS:
            tmp: dict = CHILE_MENUS.get(value)
            if tmp and not tmp.get('no_child'):
                data.append({value: list(tmp.keys())})
            else:
                data.append(value)
        return data

    @classmethod
    def father_type_keys(cls):
        """
        一级分类 返回中文列表
        :return:
        """
        return FATHER_MENUS

    @classmethod
    def child_keys(cls, father_type):
        type_key = cls.type_menu_info()
        for father in type_key:
            if isinstance(father, dict):
                if father.get(father_type):
                    return father.get(father_type, [])
            else:
                if father == father_type:
                    return []
        return []

    @classmethod
    def weapons_goods(cls):
        """
        排除 人物 特感
        :return:
        """
        new_dict = dict(CHILE_MENUS)
        new_dict.pop(cls.SURVIVORS.value)
        new_dict.pop(cls.INFECTED.value)
        return new_dict


# 二级目录
# 人物 特感以外,还有额外可配置项
# mdl mdl_path_regex
# vtf vtf_path_regex
# vmt vmt_path_regex

CHILE_MENUS = {
    # 人物 根据mdl文件检查, 完成
    "幸存者": {
        "比尔": 'namvet',
        "比尔躯体": "namvet_deathpose",
        "弗朗西斯": 'biker',
        "路易斯": 'manager',
        '佐伊': 'teenangst',
        "Ellis": 'mechanic',
        "Coach": 'coach',
        "Nick": 'gambler',
        "Rochelle": "producer",
        "语音": '',
        '其他': ''
    },
    # 特感 重写完成(声音)
    "特感": {
        "小丧尸": {
            "mdl": ['common_fem_infected_w_abdomen_l4d1', 'common_fem_infected_w_abdomen_thru_l4d1',
                    'common_fem_infected_w_back_lower_l4d1', 'common_fem_infected_w_back_upper_l4d1',
                    'common_fem_infected_w_l_arm_lower_l4d1', 'common_fem_infected_w_l_arm_shoulder_l4d1',
                    'common_fem_infected_w_l_arm_upper_l4d1', 'common_fem_infected_w_l_obliques_l4d1',
                    'common_fem_infected_w_r_arm_lower_l4d1', 'common_fem_infected_w_r_arm_shoulder_l4d1',
                    'common_fem_infected_w_r_arm_upper_l4d1', 'common_fem_infected_w_r_obliques_l4d1',
                    'common_fem_infected_w_slash_torso1_l4d1', 'common_fem_infected_w_slash_torso2_l4d1',
                    'common_fem_infected_w_slash_torso3_l4d1', 'common_fem_infected_w_slash_torso4_l4d1',
                    'common_fem_infected_w_slash_torso5_l4d1', 'common_fem_infected_w_slash_torso6_l4d1',
                    'common_fem_infected_w_slash_torso9_l4d1', 'common_fem_infected_w_slash_torso10_l4d1',
                    'common_fem_infected_w_slash_torso11_l4d1', 'common_fem_infected_w_slash_torso12_l4d1',
                    'common_fem_infected_w_slash_torso13_l4d1', 'common_fem_infected_w_slash_torso14_l4d1',
                    'common_fem_infected_w_spine_l4d1', 'common_fem_infected_w_t_half_l4d1',
                    'common_female_baggagehandler_01', 'common_female_nurse01', 'common_female_rural01',
                    'common_female01', 'common_female01_suit', 'common_male_baggagehandler_01',
                    'common_male_baggagehandler_02', 'common_male_ceda_l4d1', 'common_male_fallen_survivor_l4d1',
                    'common_male_mud_l4d1', 'common_male_parachutist', 'common_male_pilot', 'common_male_riot_l4d1',
                    'common_male_roadcrew_l4d1', 'common_male_rural01', 'common_male_suit', 'common_male01',
                    'common_male02', 'common_military_male01', 'common_patient_male01', 'common_police_male01',
                    'common_surgeon_male01', 'common_tsaagent_male01', 'common_worker_male01'],
            "folder": 'common'
        },
        "胖子": {
            "mdl": ['boomer', 'boomette', 'exploded_boomette', 'boomer_l4d1'],
            "folder": 'boomer'
        },
        "猎人": {
            "mdl": ['hunter', 'hunter_l4d1'],
            "folder": 'hunter'
        },
        "牛牛": {
            'mdl': ['charger'],
            'folder': 'charger'
        },
        "舌头": {
            "mdl": ['smoker', 'smoker_l4d1'],
            "folder": 'smoker'
        },
        "坦克": {
            "mdl": ['tank', 'hulk', 'hulk_l4d1', 'hulk_dlc3'],
            "folder": 'hulk'
        },
        "猴子": {
            "mdl": ['jockey'],
            'folder': 'jockey'
        },
        "口水": {
            "mdl": ['spitter'],
            'folder': 'spitter'
        },
        "妹子": {
            "mdl": ['witch'],
            'folder': 'witch'
        },
        # read_vpk使用文本
        "多种特感": {
            'mdl': [],
            'folder': ''
        },
        "语音": {
            'path': ['sound/player/(?:hunter|boomer|charger|jockey|smoker|spitter|tank)/',
                     'sound/player/footsteps/(?:hunter|boomer|charger|jockey|smoker|spitter|tank)',
                     'sound/npc/infected', 'sound/music/witch']
        },
        '其他': {
            'mdl': [],
            'folder': ''
        }
    },
    # 武器
    "武器": {
        "手枪": {
            "mdl": ["v_dual_pistola", "v_pistola", "w_pistol_a", "w_pistol_a_dual", "w_pistol_b"],
            "vmt": ["v_4pistols"],
            "vtf": ["v_4pistols", "v_4pistols_exp"]
        },
        "马格南": {
            "mdl": ["v_desert_eagle", "w_desert_eagle"],
            "vmt": ["deserteagle", "deserteagle_bluewood", "deserteagle_operative"],
            "vtf": ["deserteagle", "deserteagle_bluewood", "deserteagle_bluewood_exp", "deserteagle_normal",
                    "deserteagle_operative", "deserteagle_operative_exp"]
        },
        "木喷": {
            "mdl": ["v_pumpshotgun", "w_shotgun"],
            "vtf": ["v_shotgun_wood", "v_shotgun_wood_exp", "v_pump_shotgun_reference"],
            "vmt": ["v_shotgun_wood", "v_pump_shotgun_reference", "v_pump_shotgun_reference_world"]
        },
        "铁喷": {
            "mdl": ["v_shotgun_chrome", "w_pumpshotgun_a"],
            "vmt": ["v_shotgun_a"],
            "vtf": ["v_shotgun_a", "v_shotgun_a_exp"]
        },
        "一代连喷": {
            "mdl": ["v_autoshotgun", "w_autoshot_m4super"],
            "vmt": ["m4super", "m4super_world", "m4super_worn"],
            "vtf": ["m4super", "m4super_worn"]
        },
        "二代连喷": {
            "mdl": ["v_shotgun_spas", "w_shotgun_spas"],
            "vmt": ["shotgun_spas"],
            "vtf": ["shotgun_spas", "shotgun_spas_exp"]
        },
        "乌兹": {
            "mdl": ["v_smg", "w_smg_uzi"],
            "vmt": ["uzi", "uzi_world", "uzi_worn"],
            "vtf": ["uzi", "uzi_worn"]
        },
        "MAC-10": {
            "mdl": ["v_silenced_smg", "w_smg_a"],
            "vmt": ["smg_a", "smg_a_worn"],
            "vtf": ["smg_a", "smg_a_worn", "smg_a_worn_exp"]
        },
        "MP5": {
            "mdl": ["v_smg_mp5", "w_smg_mp5"],
            "vmt": ["mp5_1", "w_smg_mp5"],
            "vtf": ["mp5_1", "mp5_1_ref", "w_smg_mp5"]
        },
        "AK": {
            "mdl": ["v_rifle_ak47", "w_rifle_ak47"],
            "vmt": ["ak47", "ak47_rural", "ak47_wartorn"],
            "vtf": ["ak47", "ak47_exp", "ak47_rural", "ak47_rural_exp", "ak47_wartorn", "ak47_wartorn_exp"]
        },
        "M4": {
            "mdl": ["v_rifle", "w_rifle_m16a2"],
            "vmt": ["m16a2", "m16a2_namvet", "m16a2_world", "m16a2_worn"],
            "vtf": ["m16a2", "m16a2_namvet", "m16a2_worn"]
        },
        "三连发": {
            "mdl": ["v_desert_rifle", "w_rifle_b", "w_desert_rifle"],
            "vtf": ["rifle_b", "rifle_a"],
            "vmt": ["rifle_b"]
        },
        "SG552": {
            "mdl": ["v_rif_sg552", "w_rifle_sg552"],
            "vmt": ["rif_sg552"],
            "vtf": ["rif_sg552", "rif_sg552_ref"]
        },
        "鸟狙": {
            "mdl": ["v_snip_scout", "w_sniper_scout"],
            "vmt": ["w_snip_scout", "snip_scout"],
            "vtf": ["w_snip_scout", "snip_scout", "snip_scout_ref"]
        },
        # 十五连
        "木狙": {
            "mdl": ["v_huntingrifle", "w_sniper_mini14"],
            "vtf": ["v_sniper_reference_worn", "v_sniper_reference_ref", "v_sniper_reference"],
            "vmt": ["v_sniper_reference_worn", "v_sniper_reference"]
        },
        # 30连
        "连狙": {
            "mdl": ["v_sniper_military", "w_sniper_military"],
            "vtf": ["v_sniper_a"],
            "vmt": ["v_sniper_a"]
        },
        "大狙": {
            "mdl": ["v_snip_awp", "w_sniper_awp"],
            "vmt": ["v_awp", "v_awp_scope", "w_snip_awp"],
            "vtf": ["v_awp", "v_awp_ref", "v_awp_scope", "v_awp_scope_ref", "w_snip_awp"]
        },
        "机枪": {
            "mdl": ["v_m60", "w_m60"],
            "vtf": ["m60"],
            "vmt": ["m60"]
        },
        "榴弹枪": {
            "mdl": ["v_grenade_launcher", "w_grenade_launcher", "w_he_grenade"],
            "vmt": ["w_he_grenade", "grenade_launcher"],
            "vtf": ["w_he_grenade_normal", "w_he_grenade", "grenade_launcher", "grenade_launcher_exponent"]
        },
        '加特林枪台': {
            "mdl": ["w_minigun"],
            "vtf": ["w_minigun"],
            "vmt": ["w_minigun"]
        },
        '重机枪': {
            "mdl": ["50_cal_broken", "50cal"],
            "vmt": ["50cal"],
            "vtf": ["50cal", "50cal_detail"]
        }
    },
    # 近战
    "近战": {
        "砍刀": {
            "mdl": ["v_machete", "w_machete"],
            "vtf": ["machete_exponent", "machete"],
            "vmt": ["machete"]
        },
        "武士刀": {
            "mdl": ["v_katana", "w_katana"],
            "vtf": ["katana_normal", "katana"],
            "vmt": ["katana"]
        },
        "撬棍": {
            "mdl": ["v_crowbar", "w_crowbar"],
            "vtf": ["crowbar_normal", "crowbar", "crowbar_gold", "crowbar_gold_tint"],
            "vmt": ["crowbar", "crowbar_gold"]
        },
        "消防斧": {
            "mdl": ["v_fireaxe", "w_fireaxe"],
            "vtf": ["v_fireaxe"],
            "vmt": ["v_fireaxe"]
        },
        "电锯": {
            "mdl": ["v_chainsaw", "w_chainsaw"],
            "vmt": ["chainsaw", "chainsaw_chain"],
            "vtf": ["chainsaw", "chainsaw_chain", "chainsaw_exp"]
        },
        "小刀": {
            "mdl": ["v_knife_t", "w_knife_t"],
            "vtf": ["knife_t", "knife_t_ref", "w_knife_t"],
            "vmt": ["knife_t", "w_knife_t"]
        },
        "防爆盾": {
            "mdl": ["w_riotshield", "v_riotshield"],
            "vtf": ["riotshield_plastic", "riotshield_metal", "riotshield_metal_normal"],
            "vmt": ["riotshield_metal", "riotshield_plastic"]
        },
        "平底锅": {
            "mdl": ["v_frying_pan", "w_frying_pan"],
            "vmt": ["4melee_weapons"],
            "vtf": ["4melee_weapons", "4melee_weapons_normal"]
        },
        "吉他": {
            "mdl": ["v_electric_guitar", "w_electric_guitar"],
            "vtf": ["electric_guitar_normal", "electric_guitar", "electric_guitar_exp"],
            "vmt": ["electric_guitar"]
        },
        "警棍": {
            "mdl": ["v_tonfa"],
            "vtf": ["tonfa_normal", "tonfa"],
            "vmt": ["tonfa"]
        },
        "棒球棒": {
            "mdl": ["v_bat", "w_bat"],
            "vtf": ["bat_normal", "bat"],
            "vmt": ["bat"]
        },
        "板球棒": {
            "mdl": ["v_cricket_bat", "w_cricket_bat"],
            "vtf": ["cricket_bat_trophy_normal", "cricket_bat", "cricket_bat_normal", "cricket_bat_trophy"],
            "vmt": ["cricket_bat", "cricket_bat_trophy"]
        },
        "高尔夫": {
            "mdl": ["v_golfclub", "w_golfclub"],
            "vmt": ["golf_club"],
            "vtf": ["golf_club", "golf_club_normal"]
        },
        "干草叉": {
            "mdl": ["v_pitchfork", "w_pitchfork"],
            "vmt": ["pitchfork"],
            "vtf": ["pitchfork", "pitchfork_exponent", "pitchfork_normal"]
        },
        "铁锹": {
            "mdl": ["v_shovel", "w_shovel"],
            "vtf": ["shovel_normal", "shovel", "shovel_exp"],
            "vmt": ["shovel"]
        }
    },
    # 医疗
    "医疗品": {
        "医疗包": {
            "mdl": ["v_medkit", "w_eq_medkit"],
            "vmt": ["w_eq_medkit", "v_eq_medkit"],
            "vtf": ["w_eq_medkit", "w_eq_medkit_nrm"]
        },
        "电击器": {
            "mdl": ["v_defibrillator", "w_eq_defibrillator", "w_eq_defibrillator_no_paddles",
                    "w_eq_defibrillator_paddles"],
            "vmt": ["defibrillator", "v_eq_defibrillator", "w_eq_defibrillator"],
            "vtf": ["defibrillator", "w_eq_defibrillator"]
        },
        "止痛药": {
            "mdl": ["v_painpills", "w_eq_painpills"],
            "vmt": ["w_eq_painpills", "v_eq_painpills"],
            "vtf": ["w_eq_painpills"]
        },
        "肾上腺素": {
            "mdl": ["v_adrenaline", "w_eq_adrenaline"],
            "vmt": ["adrenaline_shot", "adrenaline_shot_clear", "adrenaline_shot_plastic", "v_eq_adrenaline",
                    "w_eq_adrenaline"],
            "vtf": ["adrenaline_shot", "adrenaline_shot_clear", "adrenaline_shot_plastic", "w_eq_adrenaline"]
        },
    },
    # 投掷
    "投掷": {
        "土制炸弹": {
            "mdl": ["v_pipebomb", "w_eq_pipebomb"],
            "vmt": ["v_eq_pipebomb", "w_eq_pipebomb"],
            "vtf": ["v_eq_pipebomb"]
        },
        "燃烧瓶": {
            "mdl": ["v_molotov", "w_eq_molotov"],
            "vmt": ["v_eq_molotov_bottle", "v_eq_molotov_rag", "w_eq_molotov_bottle", "w_eq_molotov_rag"],
            "vtf": ["v_eq_molotov_bottle", "v_eq_molotov_bottle_normal", "v_eq_molotov_rag", "v_eq_molotov_rag_normal",
                    "w_eq_molotov_bottle", "w_eq_molotov_rag"]
        },
        "胆汁": {
            "mdl": ["v_bile_flask", "w_eq_bile_flask"],
            "vmt": ["v_bile_flask", "v_bile_flask_cap"],
            "vtf": ["v_bile_flask", "v_bile_flask_cap"]
        },
    },
    '杂项': {
        '门': {
            "path": ["materials/models/props_doors"]
        },
        "天空盒": {},
        "点唱机": {
            "vtf": ["jukebox_menu_selection5", "jukebox", "jukebox_envmap", "jukebox_menu_glow1", "jukebox_menu_glow2",
                    "jukebox_menu_selection1", "jukebox_menu_selection2", "jukebox_menu_selection3",
                    "jukebox_menu_selection4"],
            "vmt": ["jukebox", "jukebox_menu_glow1", "jukebox_menu_glow2", "jukebox_menu_selection1",
                    "jukebox_menu_selection2", "jukebox_menu_selection3", "jukebox_menu_selection4",
                    "jukebox_menu_selection5"]
        },
        "可乐": {
            "mdl": ["v_cola", "w_cola"],
            "vmt": ["v_cola_glass", "v_cola_logos"],
            "vtf": ["v_cola_glass", "v_cola_glass_normal", "v_cola_logos", "v_cola_logos_normal"]
        },
        "红外线盒子": {
            "mdl": ["w_laser_sights"],
            "vtf": ["w_laser_sights"],
            "vmt": ["w_laser_sights"]
        },
        "油桶": {
            "mdl": ["gascan001a", 'wooden_barricade_gascans', 'dieselcan'],
            "vtf": ["phys_objects02d", "phys_objects02a", "phys_objects02a_normal", "phys_objects02b",
                    "phys_objects02c", "phys_objects04a"],
            "vmt": ["phys_objects02a", "phys_objects02b", "phys_objects02c", "phys_objects02d", "phys_objects04a"]
        },
        "煤气罐": {
            "vmt": ["propanecanister01a"],
            "vtf": ["propanecanister01a"],
            "mdl": ["propanecanister001a"]
        },
        "氧气罐": {
            "vtf": ["oxygentank01"],
            "mdl": ["oxygentank01"],
            "vmt": ["oxygentank01"]
        },
        "烟花盒": {
            "vtf": ["explosive_box001"],
            "vmt": ["explosive_box001_hinges", "explosive_box001"],
            "mdl": ["explosive_box001"]
        },
        "树": {
            'path': ['materials/models/props_foliage']
        },
        "声音": {
            'path': ['sound']
        },
        "喷漆": {
            'path': ['materials/vgui/logos']
        },
        "侏儒": {
            "mdl": ['gnome', 'v_gnome']
        },
        "自动贩卖机": {
            "vmt": ["vending_machine01", "vending_machine", "vending_machine_off"],
            "vtf": ["vending_machine01", "vending_machine01_mask"]
        },
        "脚本": {
            'path': ['scripts']
        },
        '医疗箱': {
            "vtf": ['medicalcabinet02', 'medicalcabinet02_ref'],
            'vmt': ['medicalcabinet02']
        },
        '涂鸦': {
            'vtf': ["graffiti_alleys_01", "graffiti_alleys_02", "graffiti_alleys_03", "graffiti_alleys_04",
                    "graffiti_alleys_05", "graffiti_alleys_06", "graffiti_docks_01", "graffiti_docks_02",
                    "graffiti_docks_03",
                    "graffiti_docks_04", "graffiti_docks_05", "graffiti_docks_06", "graffiti_docks_07",
                    "graffiti_fight",
                    "graffiti_japanese", "graffiti_lighthouse_01", "graffiti_lighthouse_02", "graffiti_lighthouse_03",
                    "graffiti_lighthouse_04", "graffiti_lighthouse_05", "graffiti_lighthouse_06",
                    "graffiti_lighthouse_07",
                    "graffiti_lighthouse_08", "graffiti_lighthouse_08a", "graffiti_lighthouse_09",
                    "graffiti_lighthouse_10",
                    "graffiti_nonesurvive", "graffiti_saferoom_airport01_02", "graffiti_saferoom_airport01_03",
                    "graffiti_saferoom_airport02_01", "graffiti_saferoom_airport02_02",
                    "graffiti_saferoom_airport03_01",
                    "graffiti_saferoom_airport03_02", "graffiti_saferoom_c1_m3-4_01", "graffiti_saferoom_c1_m3-4_02",
                    "graffiti_saferoom_c2_m4-5_01", "graffiti_saferoom_c2_m4-5_02", "graffiti_saferoom_c2_m4-5_03",
                    "graffiti_saferoom_c3_m2-3_01", "graffiti_saferoom_c3_m2-3_02", "graffiti_saferoom_c3_m2-3_03",
                    "graffiti_saferoom_c3_m3-4_01", "graffiti_saferoom_c3_m3-4_02", "graffiti_saferoom_c4_m1-2_01",
                    "graffiti_saferoom_c4_m1-2_02", "graffiti_saferoom_c4_m2-3_01", "graffiti_saferoom_c4_m2-3_02",
                    "graffiti_saferoom_c4_m2-3_03", "graffiti_saferoom_c4_m2-3_04", "graffiti_saferoom_c4_m2-3_05",
                    "graffiti_saferoom_c5_m1-2_01", "graffiti_saferoom_c5_m1-2_02", "graffiti_saferoom_c5_m1-2_03",
                    "graffiti_saferoom_c5_m1-2_04", "graffiti_saferoom_c5_m3-4_01", "graffiti_saferoom_c5_m3-4_02",
                    "graffiti_saferoom_c5_m3house02", "graffiti_saferoom_c5_m3house03", "graffiti_saferoom_chicagoted",
                    "graffiti_saferoom_citygone", "graffiti_saferoom_crashcourse01_01",
                    "graffiti_saferoom_crashcourse01_02",
                    "graffiti_saferoom_crashcourse01_03", "graffiti_saferoom_crashcourse01_04",
                    "graffiti_saferoom_farm01_01",
                    "graffiti_saferoom_farm01_02", "graffiti_saferoom_farm01_03", "graffiti_saferoom_farm01_04",
                    "graffiti_saferoom_farm02_02", "graffiti_saferoom_farm03_01", "graffiti_saferoom_farm04_01",
                    "graffiti_saferoom_farm04_02", "graffiti_saferoom_farm04_03", "graffiti_saferoom_heatherignore",
                    "graffiti_saferoom_hospitaloverrun", "graffiti_saferoom_ikilled63",
                    "graffiti_saferoom_nobodycoming",
                    "graffiti_saferoom_nobodysave", "graffiti_saferoom_peterwaited", "graffiti_saferoom_port_m2-3_01",
                    "graffiti_saferoom_port_m2-3_02", "graffiti_saferoom_port_m2-3_03",
                    "graffiti_saferoom_port_m2-3_04",
                    "graffiti_saferoom_port_m2-3_05", "graffiti_saferoom_port_m2-3_06",
                    "graffiti_saferoom_port_m2-3_07",
                    "graffiti_saferoom_port_m2-3_08", "graffiti_saferoom_smalltown01_02",
                    "graffiti_saferoom_smalltown02_01",
                    "graffiti_saferoom_smalltown02_02", "graffiti_saferoom_smalltown02_03",
                    "graffiti_saferoom_smalltown03_01",
                    "graffiti_saferoom_smalltown03_02", "graffiti_saferoom_smalltown03_03",
                    "graffiti_saferoom_smalltown03_04",
                    "graffiti_saferoom_smalltown03_05", "graffiti_saferoom_smalltown04_01",
                    "graffiti_saferoom_smalltown04_02",
                    "graffiti_saferoom_smalltown04_03"],
            "vtf_path_regex": ['^materials/graffiti/(?:psd)?.*$']
        },
        "手电筒": {
            'vtf': ['flashlight001'],
            'vtf_path_regex': ['materials/effects']
        }
    },
    # 生成菜单兼容
    "弹药": {
        "no_child": True,
        'mdl': ['v_explosive_ammopack', 'w_eq_explosive_ammopack', 'v_incendiary_ammopack', 'w_eq_incendiary_ammopack',
                'w_rd_grenade_scale_x1', 'w_rd_grenade_scale_x4', 'w_rd_grenade_scale_x4_burn', 'ammo_stack',
                'coffeeammo'],
        'vtf': ['explosive_ammopack', 'exploding_ammo', 'incendiary_ammopack', 'w_rd_grenade', 'w_rd_grenade_normal',
                'w_eq_ammopack'],
        'vmt': ['exploding_ammo', 'explosive_ammopack', 'incendiary_ammopack', 'w_rd_grenade', 'w_eq_ammopack',
                'v_eq_ammopack']
    },
    'UI': {
        "no_child": True,
        'path': ['resource/ui', 'materials/vgui']
    },
    "材质特效": {
        "no_child": True,
    },
    "动作": {
        "no_child": True,
        'path': ['models/xdreanims']
    },
}
# 一级目录
FATHER_MENUS = [
    '幸存者', '特感', '武器', '近战', '医疗品', '投掷', 'UI', '杂项', '弹药', '动作', '地图', '其他'
]

CustomData = {}

WORKSPACE = Path(__file__).parent.parent

CachePath = WORKSPACE / 'Cache'
CachePath.mkdir(parents=True, exist_ok=True)
LogPath = WORKSPACE / 'log'
LogPath.mkdir(parents=True, exist_ok=True)
