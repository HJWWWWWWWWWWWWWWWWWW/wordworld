"""
WordWorld Pygame UI — 残火长明：瓦片地图探索 + 回合制战斗。

运行：python run_pygame.py
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pygame

from wordworld.core.engine import (
    GameEngine, STORY_PHASES, COMBO_MAX, COMBO_DAMAGE_PER_STACK, SKILL_ELEMENTS,
    ELEMENT_TYPES, ELEMENT_WEAKNESS, REGION_BY_MAP, item_price,
    EQUIPMENT_DATA, EQUIPMENT_SLOTS, TIME_PERIODS, EXPLORATION_ACTIONS,
    wallet_display, wallet_add, wallet_can_afford, wallet_normalize, wallet_total,
)
from wordworld.config.paths import SAVE_PATH
from wordworld.ui.item_art import draw_item_icon

# ═══════════════════════════════════════════════════════════════════
# 常量
# ═══════════════════════════════════════════════════════════════════

TILE_SIZE = 32
MAP_VIEW_W = 20
MAP_VIEW_H = 15
PANEL_W = 280
WIN_W = MAP_VIEW_W * TILE_SIZE + PANEL_W
WIN_H = MAP_VIEW_H * TILE_SIZE
FPS = 30

# 全部音效均由代码实时生成，保持单文件发行且不依赖外部音频资源。
PROGRAMMATIC_SOUND_RECIPES: Dict[str, List[Tuple[int, int, str, float]]] = {
    "step": [(180, 32, "noise", 0.10)],
    "bump": [(90, 70, "square", 0.18)],
    "select": [(520, 35, "square", 0.10)],
    "confirm": [(620, 45, "sine", 0.18), (820, 60, "sine", 0.16)],
    "cancel": [(420, 45, "sine", 0.14), (260, 70, "sine", 0.12)],
    "alert": [(280, 100, "square", 0.22), (360, 130, "square", 0.20)],
    "travel": [(260, 70, "noise", 0.12), (420, 80, "sine", 0.16), (620, 110, "sine", 0.14)],
    "treasure": [(660, 60, "sine", 0.20), (880, 70, "sine", 0.18), (1100, 120, "sine", 0.16)],
    "buy": [(740, 45, "square", 0.14), (980, 80, "sine", 0.17)],
    "sell": [(920, 45, "sine", 0.15), (620, 80, "square", 0.12)],
    "rest": [(520, 120, "sine", 0.10), (390, 160, "sine", 0.09), (260, 220, "sine", 0.08)],
    "cultivate": [(180, 100, "sine", 0.10), (360, 160, "sine", 0.13), (720, 220, "sine", 0.12)],
    "story": [(440, 100, "sine", 0.13), (660, 120, "sine", 0.14), (880, 180, "sine", 0.15)],
    "hit": [(115, 65, "noise", 0.28), (80, 100, "square", 0.24)],
    "critical": [(150, 80, "noise", 0.34), (70, 180, "square", 0.32)],
    "skill": [(260, 70, "sine", 0.16), (520, 100, "sine", 0.22), (1040, 180, "square", 0.20)],
    "defend": [(180, 80, "noise", 0.16), (120, 130, "sine", 0.18)],
    "charge": [(110, 100, "sine", 0.12), (220, 130, "sine", 0.16), (440, 180, "sine", 0.20)],
    "item": [(700, 60, "sine", 0.16), (900, 100, "sine", 0.18)],
    "victory": [(440, 100, "square", 0.14), (660, 110, "square", 0.16), (880, 240, "sine", 0.20)],
    "defeat": [(320, 130, "square", 0.16), (220, 170, "square", 0.15), (110, 260, "sine", 0.14)],
    "escape": [(520, 50, "noise", 0.12), (360, 70, "noise", 0.10), (220, 100, "noise", 0.08)],
    "save": [(600, 70, "square", 0.13), (900, 120, "sine", 0.17)],
    "load": [(900, 70, "sine", 0.14), (600, 120, "square", 0.14)],
    "equip": [(420, 50, "square", 0.14), (760, 90, "sine", 0.16)],
}

PROGRAMMATIC_AMBIENT_PROFILES: Dict[str, Tuple[int, int, float]] = {
    "city": (110, 2, 0.03),
    "wild": (82, 1, 0.08),
    "danger": (55, 3, 0.12),
    "battle": (73, 6, 0.16),
}

# 瓦片类型
TILE_FLOOR = 0
TILE_WALL = 1
TILE_DOOR = 2
TILE_COUNTER = 3
TILE_ROAD = 4
TILE_PLAZA = 5
TILE_WATER = 6
TILE_GARDEN = 7
TILE_LANDMARK = 8

# 实体类型
ENTITY_PLAYER = 10
ENTITY_SHOP = 11
ENTITY_INN = 12
ENTITY_GUILD = 13
ENTITY_NPC = 14
ENTITY_TREASURE = 15
ENTITY_ENEMY = 16
ENTITY_EXIT = 17
ENTITY_ENCOUNTER = 18
ENTITY_GATHER = 19  # 探索随机遭遇

# 场景
SCENE_EXPLORE = "explore"
SCENE_TRAVEL = "travel"
SCENE_SHOP = "shop"
SCENE_INN = "inn"
SCENE_MENU = "menu"
SCENE_INVENTORY = "inventory"
SCENE_COMBAT = "combat"
SCENE_ENCOUNTER = "encounter"
SCENE_GUILD = "guild"
SCENE_SKILL_SELECT = "skill_select"
SCENE_ITEM_SELECT = "item_select"
SCENE_ALCHEMY = "alchemy"
SCENE_AUCTION = "auction"
SCENE_TECHNIQUE = "technique"
SCENE_FLAME = "flame"
C_BG = (18, 18, 24)
C_FLOOR = (42, 42, 54)
C_WALL = (65, 65, 80)
C_DOOR = (80, 50, 30)
C_COUNTER = (100, 70, 40)
C_PLAYER = (80, 210, 120)
C_ENEMY = (220, 60, 60)
C_NPC = (60, 140, 220)
C_SHOP = (240, 180, 40)
C_INN = (100, 200, 200)
C_GUILD = (200, 140, 240)
C_TREASURE = (240, 200, 40)
C_EXIT = (100, 220, 160)
C_ENCOUNTER = (240, 140, 60)
C_PANEL = (24, 24, 32)
C_TEXT = (220, 220, 230)
C_ACCENT = (200, 160, 40)
C_HP_BAR = (200, 50, 50)
C_QI_BAR = (50, 120, 200)
C_HP_BG = (40, 15, 15)
C_QI_BG = (15, 25, 40)
C_BUTTON = (50, 50, 70)
C_BUTTON_HOVER = (70, 70, 100)

ENTITY_COLORS = {
    ENTITY_ENEMY: C_ENEMY, ENTITY_TREASURE: C_TREASURE, ENTITY_NPC: C_NPC,
    ENTITY_SHOP: C_SHOP, ENTITY_INN: C_INN, ENTITY_GUILD: C_GUILD,
    ENTITY_EXIT: C_EXIT, ENTITY_ENCOUNTER: C_ENCOUNTER,
}
ENTITY_LABELS = {
    ENTITY_ENEMY: "敌", ENTITY_TREASURE: "宝", ENTITY_NPC: "人",
    ENTITY_SHOP: "商", ENTITY_INN: "栈", ENTITY_GUILD: "会", ENTITY_EXIT: "出",
    ENTITY_ENCOUNTER: "!",
    ENTITY_GATHER: "采",
}

_NPC_CANONICAL_VISUALS: Dict[str, Dict[str, Any]] = {
    # 原文重点人物：颜色与标志物优先依据人物首次登场和长期形象。
    "npc_yun_xi": {"robe": (91, 63, 139), "trim": (224, 184, 62), "hair": (26, 24, 34), "hair_style": "long", "accessory": "gold_flame"},
    "npc_xuanlu_elder": {"robe": (35, 35, 43), "trim": (205, 208, 214), "hair": (220, 220, 224), "hair_style": "elder", "accessory": "staff"},
    "npc_lin_zhan": {"robe": (94, 92, 99), "trim": (196, 151, 72), "hair": (39, 31, 28), "hair_style": "short", "accessory": "brows"},
    "npc_su_wanqing": {"robe": (118, 183, 178), "trim": (230, 240, 233), "hair": (35, 31, 39), "hair_style": "long", "accessory": "sword"},
    "npc_qing_yun": {"robe": (112, 164, 191), "trim": (218, 235, 240), "hair": (38, 35, 42), "hair_style": "long", "accessory": "sword"},
    "npc_chi_lin": {"robe": (155, 48, 70), "trim": (235, 176, 67), "hair": (41, 25, 54), "hair_style": "long", "accessory": "crown"},
    "npc_xiao_yixian": {"robe": (224, 229, 220), "trim": (132, 186, 132), "hair": (42, 39, 47), "hair_style": "long", "accessory": "medicine"},
    "npc_ya_fei": {"robe": (176, 48, 62), "trim": (231, 174, 76), "hair": (66, 37, 30), "hair_style": "long", "accessory": "jewel"},
    "npc_hai_bodong": {"robe": (72, 116, 151), "trim": (183, 222, 231), "hair": (207, 214, 218), "hair_style": "elder", "accessory": "ice"},
    "npc_zi_yan": {"robe": (139, 75, 166), "trim": (238, 174, 220), "hair": (63, 35, 76), "hair_style": "twin", "accessory": "dragon"},
    "npc_han_feng": {"robe": (45, 101, 137), "trim": (83, 207, 218), "hair": (35, 35, 39), "hair_style": "short", "accessory": "blue_flame"},
    "npc_qing_lin": {"robe": (74, 147, 117), "trim": (139, 225, 184), "hair": (41, 48, 42), "hair_style": "long", "accessory": "snake_eye"},
    "npc_hun_tiandi": {"robe": (42, 35, 49), "trim": (177, 47, 64), "hair": (28, 24, 31), "hair_style": "long", "accessory": "crown"},
}

_FACTION_VISUALS = {
    "faction_xiao": ((66, 104, 126), (183, 151, 79)),
    "faction_gu": ((92, 70, 132), (224, 184, 62)),
    "faction_yunlan": ((111, 166, 177), (224, 237, 232)),
    "faction_snake": ((139, 59, 78), (224, 167, 67)),
    "faction_miteer": ((137, 72, 58), (224, 174, 74)),
    "faction_canaan": ((63, 120, 130), (151, 211, 196)),
    "faction_black_corner": ((91, 55, 65), (198, 100, 67)),
    "faction_star_pavilion": ((71, 92, 137), (170, 182, 224)),
    "faction_dan_tower": ((139, 72, 54), (230, 166, 72)),
    "faction_hun": ((47, 39, 55), (166, 52, 67)),
}

# ═══════════════════════════════════════════════════════════════════
# 地图模板系统
# ═══════════════════════════════════════════════════════════════════

def _make_border(w: int, h: int, doors: list) -> list:
    """围墙+城门。"""
    tiles = []
    for x in range(w):
        if (x, 0) not in doors:
            tiles.append((x, 0, TILE_WALL))
        if (x, h - 1) not in doors:
            tiles.append((x, h - 1, TILE_WALL))
    for y in range(h):
        if (0, y) not in doors:
            tiles.append((0, y, TILE_WALL))
        if (w - 1, y) not in doors:
            tiles.append((w - 1, y, TILE_WALL))
    return tiles


def _add_town_building(
    tiles: list,
    entities: list,
    x: int,
    y: int,
    width: int,
    height: int,
    etype: int,
    label: str,
    door_side: str = "bottom",
) -> None:
    """添加多格城镇建筑，并在面向街道的一侧保留可交互入口。"""
    door_x = x + width // 2
    door_y = y if door_side == "top" else y + height - 1
    for by in range(y, y + height):
        for bx in range(x, x + width):
            tiles.append((bx, by, TILE_FLOOR if (bx, by) == (door_x, door_y) else TILE_WALL))
    entities.append((door_x, door_y, etype, label))


_TOWN_STYLE_PROFILES = {
    "wutan": ("族坊", ["林家坊", "药铺", "铁匠铺", "茶楼", "客栈", "米特尔行", "演武馆"]),
    "desert": ("沙城", ["水站", "佣兵会", "香料铺", "地图铺", "商栈", "药铺", "驼队行"]),
    "capital": ("帝都", ["皇都客栈", "炼药师会", "米特尔行", "珍宝阁", "药材行", "茶楼", "商会"]),
    "black_corner": ("黑角", ["黑店", "拍卖行", "药材铺", "佣兵会", "情报馆", "酒馆", "黑市"]),
    "academy": ("学院", ["食堂", "任务厅", "交易所", "炼药房", "宿舍", "藏书楼", "竞技馆"]),
    "dan": ("丹城", ["丹药铺", "药材行", "炼药师会", "鉴宝阁", "丹阁驿馆", "药鼎行", "灵药斋"]),
    "zhongzhou": ("中州", ["虫洞驿站", "商会", "灵宝阁", "酒楼", "药材行", "拍卖行", "客栈"]),
    "sect": ("宗门", ["任务殿", "功法阁", "丹房", "弟子居", "执事堂", "灵药园", "修炼堂"]),
    "ancient": ("云族", ["云族客舍", "血脉堂", "灵药阁", "传承殿", "族库", "议事堂", "古市"]),
    "frontier": ("边城", ["驿站", "粮行", "兵器铺", "佣兵会", "药铺", "酒馆", "商栈"]),
}

_CITY_IDENTITIES: List[Tuple[Tuple[str, ...], Dict[str, str]]] = [
    (("wutan", "xiao_"), {
        "name": "青石城", "layout": "clan", "theme": "wutan_town",
        "landmark": "clan_monument", "motto": "青石族坊",
    }),
    (("black_rock",), {
        "name": "黑岩城", "layout": "trade", "theme": "black_rock_town",
        "landmark": "alchemy_guild", "motto": "炼药商街",
    }),
    (("salt_city", "salt_market", "salt_inn"), {
        "name": "盐城", "layout": "canal", "theme": "salt_town",
        "landmark": "salt_crane", "motto": "白盐水巷",
    }),
    (("ghost_pass", "garrison", "mountain_pass", "battle_front", "xuanhuang"), {
        "name": "边关", "layout": "fortress", "theme": "frontier_town",
        "landmark": "beacon", "motto": "烽火边城",
    }),
    (("qingshan",), {
        "name": "青山镇", "layout": "garden", "theme": "forest_town",
        "landmark": "medicine_tree", "motto": "药香山镇",
    }),
    (("mo_city", "mo_market", "mo_inn", "mo_trade"), {
        "name": "漠城", "layout": "oasis", "theme": "sand_town",
        "landmark": "oasis_well", "motto": "风沙绿洲",
    }),
    (("stone_mo",), {
        "name": "石漠城", "layout": "fortress", "theme": "sand_town",
        "landmark": "mercenary_standard", "motto": "佣兵石垒",
    }),
    (("jia_ma_capital", "capital_", "imperial_palace", "miteer_"), {
        "name": "沧澜帝都", "layout": "imperial", "theme": "capital_town",
        "landmark": "imperial_statue", "motto": "金阙御道",
    }),
    (("canaan", "inner_", "pan_gate", "peace_town"), {
        "name": "迦南学院", "layout": "academy", "theme": "academy_town",
        "landmark": "academy_crest", "motto": "学院庭院",
    }),
    (("black_seal",), {
        "name": "黑印城", "layout": "dark_market", "theme": "dark_town",
        "landmark": "auction_bell", "motto": "地下拍卖城",
    }),
    (("feng_city", "black_emperor", "black_corner", "black_auction"), {
        "name": "暗角域", "layout": "dark_market", "theme": "dark_town",
        "landmark": "black_obelisk", "motto": "暗巷斗城",
    }),
    (("tianya", "wormhole", "transfer_square", "zhongzhou"), {
        "name": "天涯城", "layout": "wormhole", "theme": "void_town",
        "landmark": "wormhole", "motto": "空间枢纽",
    }),
    (("tianbei", "ye_city", "ye_market", "ye_mansion"), {
        "name": "中州古城", "layout": "garden", "theme": "jade_town",
        "landmark": "clan_tower", "motto": "世家园城",
    }),
    (("sacred_dan", "dan_", "small_dan", "yao_realm", "alchemy"), {
        "name": "丹域", "layout": "alchemy", "theme": "dan_town",
        "landmark": "great_cauldron", "motto": "丹火药都",
    }),
    (("ancient", "gu_", "heaven_tomb"), {
        "name": "远云族域", "layout": "imperial", "theme": "void_town",
        "landmark": "bloodline_gate", "motto": "云族天城",
    }),
    (("yunlan", "pavilion", "sect", "flower_", "burning_", "valley"), {
        "name": "宗门", "layout": "academy", "theme": "jade_town",
        "landmark": "sect_stela", "motto": "云阶仙坊",
    }),
]


def _city_identity(map_id: str) -> Dict[str, str]:
    """返回城市的布局、美术主题与专属地标。"""
    text = map_id.lower()
    for keys, identity in _CITY_IDENTITIES:
        if any(key in text for key in keys):
            return identity
    style_name, _ = _town_style(map_id)
    fallback = {
        "沙城": ("oasis", "sand_town", "oasis_well", "沙海商镇"),
        "黑角": ("dark_market", "dark_town", "black_obelisk", "暗巷斗城"),
        "学院": ("academy", "academy_town", "academy_crest", "学院庭院"),
        "丹城": ("alchemy", "dan_town", "great_cauldron", "丹火药都"),
        "宗门": ("academy", "jade_town", "sect_stela", "云阶仙坊"),
        "云族": ("imperial", "void_town", "bloodline_gate", "云族天城"),
        "中州": ("wormhole", "void_town", "wormhole", "空间都会"),
        "帝都": ("imperial", "capital_town", "imperial_statue", "金阙御道"),
        "族坊": ("clan", "wutan_town", "clan_monument", "青石族坊"),
    }.get(style_name, ("trade", "frontier_town", "caravan_post", "边城商路"))
    return {
        "name": style_name, "layout": fallback[0], "theme": fallback[1],
        "landmark": fallback[2], "motto": fallback[3],
    }


def _town_style(map_id: str) -> Tuple[str, List[str]]:
    """根据城市身份选择店铺组合，子地图也继承所属城市气质。"""
    text = map_id.lower()
    if any(key in text for key in ("wutan", "xiao_")):
        key = "wutan"
    elif any(key in text for key in ("mo_city", "stone_mo", "desert", "tager")):
        key = "desert"
    elif any(key in text for key in ("capital", "jia_ma", "miteer", "nalan")):
        key = "capital"
    elif any(key in text for key in ("black_", "feng_", "peace_town", "emperor_city")):
        key = "black_corner"
    elif any(key in text for key in ("canaan", "inner_", "pan_gate")):
        key = "academy"
    elif any(key in text for key in ("dan_", "sacred_dan", "yao_", "alchemy", "small_dan")):
        key = "dan"
    elif any(key in text for key in ("ancient", "gu_", "heaven_tomb")):
        key = "ancient"
    elif any(key in text for key in (
        "sect", "pavilion", "yunlan", "star_", "flower_", "burning_", "valley",
    )):
        key = "sect"
    elif any(key in text for key in ("tianya", "zhongzhou", "wormhole", "transfer", "tianbei", "ye_city")):
        key = "zhongzhou"
    else:
        key = "frontier"
    return _TOWN_STYLE_PROFILES[key]


def _town_seed(map_id: str) -> int:
    """返回跨进程稳定的城市种子。"""
    value = 2166136261
    for char in map_id:
        value ^= ord(char)
        value = (value * 16777619) & 0xFFFFFFFF
    return value


def _npc_visual(npc_id: str, profile: Dict[str, str]) -> Dict[str, Any]:
    """结合原文重点档案与 Excel 身份字段生成稳定人物造型。"""
    if npc_id in _NPC_CANONICAL_VISUALS:
        return dict(_NPC_CANONICAL_VISUALS[npc_id])

    seed = _town_seed(npc_id)
    faction = profile.get("Faction_ID", "")
    robe, trim = _FACTION_VISUALS.get(
        faction,
        (
            (62 + seed % 70, 70 + (seed >> 4) % 65, 78 + (seed >> 9) % 70),
            (155 + seed % 70, 155 + (seed >> 5) % 70, 145 + (seed >> 10) % 80),
        ),
    )
    gender = profile.get("Gender", "")
    role = profile.get("Role", "")
    char_type = profile.get("Char_Type", "")
    skills = profile.get("Skills", "")
    hair_style = "long" if gender == "female" else "short"
    if any(key in role for key in ("长老", "族长", "会长", "尊者", "老人")):
        hair_style = "elder"
    elif seed % 7 == 0:
        hair_style = "twin"

    accessory = ""
    if "炼药" in role or "alchemy" in skills:
        accessory = "medicine"
    elif any(key in role for key in ("宗主", "女王", "皇", "族长")):
        accessory = "crown"
    elif any(key in role for key in ("强者", "护法", "将", "佣兵", "宿敌")):
        accessory = "sword"
    elif char_type == "enemy_npc":
        accessory = "red_aura"
    elif "ice" in skills:
        accessory = "ice"
    hair_palette = [(31, 28, 35), (66, 45, 35), (39, 45, 55), (104, 91, 75)]
    return {
        "robe": robe,
        "trim": trim,
        "hair": hair_palette[(seed >> 13) % len(hair_palette)],
        "hair_style": hair_style,
        "accessory": accessory,
    }


def _paint_rect(tiles: list, x: int, y: int, width: int, height: int, tile: int) -> None:
    """用指定瓦片填充矩形区域。"""
    for ty in range(y, y + height):
        for tx in range(x, x + width):
            tiles.append((tx, ty, tile))


def _paint_road_cross(tiles: list, w: int, h: int, width: int = 2) -> None:
    """铺设贯穿城镇的十字主路。"""
    _paint_rect(tiles, w // 2 - width // 2, 1, width, h - 1, TILE_ROAD)
    _paint_rect(tiles, 1, h // 2 - width // 2, w - 2, width, TILE_ROAD)


def _town_building_specs(layout: str) -> List[Tuple[int, int, int, int, str]]:
    """返回不同城市原型的建筑轮廓。"""
    return {
        "clan": [
            (1, 1, 5, 3, "bottom"), (14, 1, 5, 3, "bottom"),
            (1, 6, 4, 3, "bottom"), (15, 6, 4, 3, "bottom"),
            (1, 10, 5, 3, "top"), (14, 10, 5, 3, "top"),
        ],
        "trade": [
            (1, 1, 5, 3, "bottom"), (7, 1, 5, 3, "bottom"), (13, 1, 6, 3, "bottom"),
            (1, 10, 5, 3, "top"), (7, 10, 5, 3, "top"), (13, 10, 6, 3, "top"),
        ],
        "canal": [
            (1, 1, 6, 3, "bottom"), (13, 1, 6, 3, "bottom"),
            (1, 6, 5, 3, "bottom"), (14, 6, 5, 3, "bottom"),
            (1, 10, 6, 3, "top"), (13, 10, 6, 3, "top"),
        ],
        "fortress": [
            (1, 1, 6, 3, "bottom"), (13, 1, 6, 3, "bottom"),
            (1, 6, 4, 4, "bottom"), (15, 6, 4, 4, "bottom"),
            (2, 11, 5, 2, "top"), (13, 11, 5, 2, "top"),
        ],
        "oasis": [
            (1, 1, 5, 3, "bottom"), (14, 1, 5, 3, "bottom"),
            (1, 6, 4, 3, "bottom"), (15, 6, 4, 3, "bottom"),
            (1, 10, 6, 3, "top"), (13, 10, 6, 3, "top"),
        ],
        "academy": [
            (1, 1, 6, 3, "bottom"), (13, 1, 6, 3, "bottom"),
            (1, 6, 5, 3, "bottom"), (14, 6, 5, 3, "bottom"),
            (1, 11, 6, 2, "top"), (13, 11, 6, 2, "top"),
        ],
        "imperial": [
            (1, 1, 6, 3, "bottom"), (7, 1, 6, 3, "bottom"), (13, 1, 6, 3, "bottom"),
            (1, 7, 5, 3, "bottom"), (14, 7, 5, 3, "bottom"),
            (1, 11, 6, 2, "top"), (13, 11, 6, 2, "top"),
        ],
        "dark_market": [
            (1, 1, 7, 3, "bottom"), (12, 1, 7, 3, "bottom"),
            (1, 6, 5, 3, "bottom"), (8, 5, 4, 3, "bottom"), (14, 7, 5, 3, "bottom"),
            (1, 11, 7, 2, "top"), (12, 11, 7, 2, "top"),
        ],
        "wormhole": [
            (1, 1, 5, 3, "bottom"), (14, 1, 5, 3, "bottom"),
            (1, 6, 4, 3, "bottom"), (15, 6, 4, 3, "bottom"),
            (1, 11, 6, 2, "top"), (13, 11, 6, 2, "top"),
        ],
        "alchemy": [
            (1, 1, 6, 3, "bottom"), (13, 1, 6, 3, "bottom"),
            (1, 6, 5, 3, "bottom"), (14, 6, 5, 3, "bottom"),
            (1, 11, 6, 2, "top"), (13, 11, 6, 2, "top"),
        ],
        "garden": [
            (1, 1, 6, 3, "bottom"), (13, 1, 6, 3, "bottom"),
            (1, 7, 5, 3, "bottom"), (14, 7, 5, 3, "bottom"),
            (1, 11, 6, 2, "top"), (13, 11, 6, 2, "top"),
        ],
    }.get(layout, [])


def _decorate_town_layout(tiles: list, layout: str, seed: int, w: int, h: int) -> None:
    """为城市原型铺设道路、水系、园林和地标。"""
    if layout in ("clan", "academy", "imperial", "alchemy", "garden"):
        _paint_road_cross(tiles, w, h, 2 if layout != "imperial" else 4)
    elif layout == "trade":
        _paint_rect(tiles, 1, 5, w - 2, 4, TILE_ROAD)
        _paint_rect(tiles, w // 2, 3, 1, h - 3, TILE_ROAD)
    elif layout == "canal":
        _paint_rect(tiles, 8, 1, 4, h - 2, TILE_WATER)
        _paint_rect(tiles, 1, 5, w - 2, 2, TILE_ROAD)
        _paint_rect(tiles, 8, 5, 4, 2, TILE_PLAZA)
        _paint_rect(tiles, 9, 7, 2, h - 7, TILE_ROAD)
    elif layout == "fortress":
        _paint_rect(tiles, 8, 1, 4, h - 1, TILE_ROAD)
        _paint_rect(tiles, 5, 5, 10, 4, TILE_PLAZA)
        for x in (5, 14):
            _paint_rect(tiles, x, 4, 1, 7, TILE_WALL)
            tiles.append((x, 5, TILE_PLAZA))
            tiles.append((x, 7, TILE_PLAZA))
            tiles.append((x, 10, TILE_ROAD))
    elif layout == "oasis":
        _paint_road_cross(tiles, w, h, 2)
        _paint_rect(tiles, 7, 4, 6, 3, TILE_WATER)
        _paint_rect(tiles, 9, 6, 2, 2, TILE_PLAZA)
        for x, y in ((6, 4), (13, 4), (6, 7), (13, 7)):
            tiles.append((x, y, TILE_GARDEN))
    elif layout == "dark_market":
        _paint_rect(tiles, 1, 4, w - 2, 2, TILE_ROAD)
        _paint_rect(tiles, 6, 4, 2, h - 4, TILE_ROAD)
        _paint_rect(tiles, 11, 1, 2, h - 3, TILE_ROAD)
        _paint_rect(tiles, 6, 8, 7, 2, TILE_PLAZA)
    elif layout == "wormhole":
        _paint_road_cross(tiles, w, h, 2)
        _paint_rect(tiles, 6, 4, 8, 7, TILE_PLAZA)
        for x, y in ((6, 4), (13, 4), (6, 10), (13, 10)):
            tiles.append((x, y, TILE_LANDMARK))

    if layout == "clan":
        _paint_rect(tiles, 6, 4, 2, 2, TILE_GARDEN)
        _paint_rect(tiles, 12, 4, 2, 2, TILE_GARDEN)
        _paint_rect(tiles, 6, 9, 2, 2, TILE_GARDEN)
        _paint_rect(tiles, 12, 9, 2, 2, TILE_GARDEN)
    elif layout == "academy":
        for x, y in ((6, 4), (13, 4), (6, 9), (13, 9), (8, 7), (11, 7)):
            tiles.append((x, y, TILE_GARDEN))
    elif layout == "imperial":
        for x in (6, 13):
            _paint_rect(tiles, x, 5, 1, 5, TILE_GARDEN)
    elif layout in ("alchemy", "garden"):
        for x, y in ((6, 4), (13, 4), (6, 9), (13, 9), (8, 11), (11, 11)):
            tiles.append((x, y, TILE_GARDEN))

    landmark_positions = {
        "clan": (10, 5), "trade": (10, 5), "canal": (15, 5),
        "fortress": (10, 5), "oasis": (10, 5), "academy": (10, 5),
        "imperial": (10, 5), "dark_market": (9, 8), "wormhole": (10, 7),
        "alchemy": (10, 5), "garden": (10, 5),
    }
    if layout in landmark_positions:
        tiles.append((*landmark_positions[layout], TILE_LANDMARK))

    # 每张子地图保留稳定但不同的街景密度。
    detail_spots = [(5, 4), (14, 4), (5, 10), (14, 10), (7, 7), (12, 7)]
    for bit, spot in enumerate(detail_spots):
        if seed & (1 << bit) and layout not in ("canal", "wormhole"):
            tiles.append((*spot, TILE_COUNTER))


def _town_square_template(map_id: str) -> Tuple[int, int, list, list]:
    """按城市身份生成具有稳定特色的城镇街区。"""
    w, h = 20, 15
    doors = [(w//2, h-1), (w//2-1, h-1), (0, h//2), (w-1, h//2)]
    tiles = _make_border(w, h, doors)
    entities = []
    seed = _town_seed(map_id)
    style_name, shop_names = _town_style(map_id)
    identity = _city_identity(map_id)
    layout = identity["layout"]
    shop_names = shop_names[seed % len(shop_names):] + shop_names[:seed % len(shop_names)]

    _decorate_town_layout(tiles, layout, seed, w, h)

    building_types = [ENTITY_GUILD, ENTITY_INN] + [ENTITY_SHOP] * 5
    for index, (bx, by, building_w, building_h, door_side) in enumerate(_town_building_specs(layout)):
        _add_town_building(
            tiles,
            entities,
            bx,
            by,
            building_w,
            building_h,
            building_types[index % len(building_types)],
            shop_names[index % len(shop_names)],
            door_side,
        )

    npcs = _pick_npcs_for_map(map_id)
    treasure_spot = {
        "clan": (7, 7), "trade": (3, 7), "canal": (6, 6),
        "fortress": (7, 7), "oasis": (6, 8), "academy": (7, 7),
        "imperial": (7, 7), "dark_market": (7, 9), "wormhole": (7, 7),
        "alchemy": (7, 7), "garden": (7, 6),
    }.get(layout, (7, 7))
    npc_spots = {
        "canal": [(7, 8), (12, 8)],
        "dark_market": [(8, 9), (13, 9)],
    }.get(layout, [(8, 8), (12, 8)])
    entities.extend([
        (*treasure_spot, ENTITY_TREASURE, f"{style_name}摊"),
        (w // 2, 12, ENTITY_EXIT, "离开"),
    ])
    # 区域 NPC
    for j, npc_id in enumerate(npcs[:2]):
        entities.append((*npc_spots[j], ENTITY_NPC, npc_id))
    return w, h, tiles, entities


def _mansion_template(map_id: str = "") -> Tuple[int, int, list, list]:
    """府邸/室内——林家、纳兰家等。"""
    w, h = 16, 12
    tiles = _make_border(w, h, [(w//2, h-1), (w//2-1, h-1)])
    # 内部房间隔断
    for y in [3, 7]:
        for x in range(2, w - 2):
            if x not in (w // 2, w // 2 + 1, w // 2 - 1):
                tiles.append((x, y, TILE_COUNTER))
    # 竖向隔断
    for mid_x in [w // 3, 2 * w // 3]:
        for y in range(4, 7):
            tiles.append((mid_x, y, TILE_WALL))
    npcs = _pick_npcs_for_map(map_id)
    entities = [
        (w // 2, 1, ENTITY_NPC, npcs[0] if npcs else "族长"),
        (3, 5, ENTITY_TREASURE, "功法架"),
        (w - 4, 5, ENTITY_NPC, npcs[1] if len(npcs) > 1 else "族人"),
        (w // 2, 10, ENTITY_EXIT, "出门"),
    ]
    return w, h, tiles, entities


def _training_ground_template(map_id: str = "") -> Tuple[int, int, list, list]:
    """演武场——切磋训练。"""
    w, h = 16, 12
    tiles = _make_border(w, h, [(w//2, h-1)])
    # 中央擂台
    for x in range(w // 2 - 3, w // 2 + 3):
        tiles.append((x, h // 2 - 2, TILE_COUNTER))
        tiles.append((x, h // 2 + 2, TILE_COUNTER))
    for y in range(h // 2 - 2, h // 2 + 3):
        tiles.append((w // 2 - 3, y, TILE_COUNTER))
        tiles.append((w // 2 + 2, y, TILE_COUNTER))
    npcs = _pick_npcs_for_map(map_id)
    entities = [
        (w // 2, 1, ENTITY_NPC, npcs[0] if npcs else "教头"),
        (3, h - 2, ENTITY_NPC, "陪练弟子"),
        (w // 2, h // 2, ENTITY_ENEMY, "切磋对手"),
        (w - 4, h - 2, ENTITY_TREASURE, "武器架"),
        (w // 2, h - 2, ENTITY_EXIT, "离开"),
    ]
    return w, h, tiles, entities


def _wilderness_forest(map_id: str) -> Tuple[int, int, list, list]:
    """森林/山脉野外——曲折路径+散落敌人。"""
    rng = random.Random(_town_seed(map_id))
    w, h = 20 + rng.randint(0, 3), 15 + rng.randint(0, 2)
    tiles = _make_border(w, h, [(1, h//2), (w-2, h//2)])
    # 散落树木
    for _ in range(w * h // 6):
        x, y = rng.randint(1, w - 2), rng.randint(1, h - 2)
        tiles.append((x, y, TILE_WALL))
    # 蜿蜒通道
    for y in range(2, h - 2, 2):
        cx = w // 2 + (rng.randint(-3, 3) if y % 4 == 0 else rng.randint(-5, 5))
        for dx in range(-2, 3):
            tx = max(1, min(w - 2, cx + dx))
            tiles.append((tx, y, TILE_FLOOR))

    entities = [(1, h//2, ENTITY_EXIT, "返回"), (w-2, h//2, ENTITY_EXIT, "前进")]
    for _ in range(rng.randint(3, 6)):
        x, y = rng.randint(1, w - 2), rng.randint(1, h - 2)
        entities.append((x, y, ENTITY_ENEMY, "魔兽"))
    for _ in range(rng.randint(1, 3)):
        x, y = rng.randint(1, w - 2), rng.randint(1, h - 2)
        entities.append((x, y, ENTITY_TREASURE, "药材"))
    return w, h, tiles, entities


def _wilderness_desert(map_id: str) -> Tuple[int, int, list, list]:
    """沙漠/荒原野外——开阔+散落敌人。"""
    rng = random.Random(_town_seed(map_id))
    w, h = 22, 14
    tiles = _make_border(w, h, [(1, h//2), (w-2, h//2)])
    # 稀疏障碍
    for _ in range(w * h // 10):
        x, y = rng.randint(1, w - 2), rng.randint(1, h - 2)
        tiles.append((x, y, TILE_WALL))
    entities = [(1, h//2, ENTITY_EXIT, "返回"), (w-2, h//2, ENTITY_EXIT, "深入")]
    for _ in range(rng.randint(4, 7)):
        x, y = rng.randint(1, w - 2), rng.randint(1, h - 2)
        entities.append((x, y, ENTITY_ENEMY, "蛇人"))
    for _ in range(rng.randint(1, 2)):
        x, y = rng.randint(1, w - 2), rng.randint(1, h - 2)
        entities.append((x, y, ENTITY_TREASURE, "沙中遗物"))
    return w, h, tiles, entities


def _wilderness_cave(map_id: str) -> Tuple[int, int, list, list]:
    """洞穴/遗迹——狭窄通道+Boss。"""
    rng = random.Random(_town_seed(map_id))
    w, h = 14 + rng.randint(0, 2), 12 + rng.randint(0, 2)
    tiles = _make_border(w, h, [(1, h//2), (w-2, h//2)])
    # 狭窄通道
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if abs(x - w // 2) > 4:
                tiles.append((x, y, TILE_WALL))
    # 开洞——房间
    for room_cx in [w // 4, 3 * w // 4]:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                rx, ry = room_cx + dx, h // 2 + dy
                if 1 <= rx < w - 1 and 1 <= ry < h - 1:
                    tiles.append((rx, ry, TILE_FLOOR))
    entities = [(1, h//2, ENTITY_EXIT, "出口")]
    for _ in range(rng.randint(2, 4)):
        x, y = rng.randint(1, w - 2), rng.randint(1, h - 2)
        entities.append((x, y, ENTITY_ENEMY, "守护兽"))
    entities.append((3 * w // 4, h // 2, ENTITY_TREASURE, "宝物"))
    return w, h, tiles, entities


# ── 地图连接表：基于原文地理的完整路线网 ─────────────────

_MAP_CONNECTIONS: Dict[str, List[str]] = {
    # ═══════════════════════════════════════════════════════════
    # 沧澜帝国 —— 青石城区域
    # ═══════════════════════════════════════════════════════════
    "map_wutan": [
        "map_xiao_mansion", "map_xiao_training_ground",
        "map_wutan_commercial_street", "map_wutan_inn",
        "map_wutan_back_mountain", "map_wutan_gate",
        "map_jia_ma_road",
    ],
    "map_xiao_mansion": ["map_wutan"],
    "map_xiao_training_ground": ["map_wutan"],
    "map_wutan_commercial_street": [
        "map_wutan", "map_xiao_market", "map_wutan_pharmacy",
        "map_wutan_smithy", "map_wutan_east_market",
        "map_wutan_warehouse_district", "map_miteer_auction",
    ],
    "map_xiao_market": ["map_wutan_commercial_street"],
    "map_wutan_pharmacy": ["map_wutan_commercial_street"],
    "map_wutan_smithy": ["map_wutan_commercial_street"],
    "map_wutan_east_market": ["map_wutan_commercial_street"],
    "map_wutan_warehouse_district": ["map_wutan_commercial_street"],
    "map_wutan_inn": ["map_wutan", "map_wutan_teahouse"],
    "map_wutan_teahouse": ["map_wutan_inn"],
    "map_wutan_back_mountain": ["map_wutan"],
    "map_wutan_gate": ["map_wutan", "map_jia_ma_road"],
    "map_xiao_council_hall": ["map_xiao_mansion"],

    # ═══════════════════════════════════════════════════════════
    # 沧澜帝国 —— 官道沿线城市
    # ═══════════════════════════════════════════════════════════
    "map_jia_ma_road": [
        "map_wutan", "map_black_rock_city", "map_salt_city",
        "map_ghost_pass", "map_jia_ma_post_station",
        "map_qingshan", "map_jia_ma_capital", "map_daling_city",
    ],
    "map_black_rock_city": [
        "map_jia_ma_road", "map_black_rock_market",
        "map_black_rock_black_market", "map_black_rock_inn",
    ],
    "map_black_rock_market": ["map_black_rock_city"],
    "map_black_rock_black_market": ["map_black_rock_city"],
    "map_black_rock_inn": ["map_black_rock_city"],
    "map_salt_city": ["map_jia_ma_road", "map_salt_market", "map_salt_inn"],
    "map_salt_market": ["map_salt_city"],
    "map_salt_inn": ["map_salt_city"],
    "map_ghost_pass": [
        "map_jia_ma_road", "map_ghost_pass_market", "map_ghost_pass_barracks",
    ],
    "map_ghost_pass_market": ["map_ghost_pass"],
    "map_ghost_pass_barracks": ["map_ghost_pass"],
    "map_daling_city": ["map_jia_ma_road", "map_daling_market", "map_daling_inn"],
    "map_daling_market": ["map_daling_city"],
    "map_daling_inn": ["map_daling_city"],
    "map_jia_ma_post_station": ["map_jia_ma_road"],

    # ═══════════════════════════════════════════════════════════
    # 沧澜帝国 —— 魔兽山脉 & 青山镇
    # ═══════════════════════════════════════════════════════════
    "map_qingshan": [
        "map_jia_ma_road", "map_magic_mountains",
        "map_qingshan_mercenary_camp", "map_qingshan_medical_hall",
        "map_qingshan_market",
    ],
    "map_qingshan_mercenary_camp": ["map_qingshan"],
    "map_qingshan_medical_hall": ["map_qingshan"],
    "map_qingshan_market": ["map_qingshan"],
    "map_magic_mountains": [
        "map_qingshan", "map_jia_ma_capital", "map_jia_ma_mountain_pass",
        "map_magic_inner", "map_magic_herb_valley", "map_wolfhead_camp",
        "map_magic_hidden_cave", "map_tager",
    ],
    "map_magic_inner": ["map_magic_mountains"],
    "map_magic_herb_valley": ["map_magic_mountains"],
    "map_wolfhead_camp": ["map_magic_mountains"],
    "map_magic_hidden_cave": ["map_magic_mountains"],
    "map_jia_ma_mountain_pass": [
        "map_magic_mountains", "map_jia_ma_border", "map_jia_ma_garrison",
    ],
    "map_jia_ma_garrison": ["map_jia_ma_mountain_pass"],

    # ═══════════════════════════════════════════════════════════
    # 沧澜帝国 —— 赤沙荒漠
    # ═══════════════════════════════════════════════════════════
    "map_tager": [
        "map_magic_mountains", "map_mo_city", "map_stone_mo_city",
        "map_snake_temple_outer", "map_desert_trade_route",
        "map_snake_oasis", "map_desert_camp",
        "map_desert_salt_lake", "map_desert_ancient_well",
    ],
    "map_mo_city": [
        "map_tager", "map_mo_market", "map_mo_inn", "map_mo_trade_post",
    ],
    "map_mo_market": ["map_mo_city"],
    "map_mo_inn": ["map_mo_city"],
    "map_mo_trade_post": ["map_mo_city"],
    "map_stone_mo_city": [
        "map_tager", "map_stone_mo_market", "map_stone_mo_mercenary",
        "map_stone_mo_inn",
    ],
    "map_stone_mo_market": ["map_stone_mo_city"],
    "map_stone_mo_mercenary": ["map_stone_mo_city"],
    "map_stone_mo_inn": ["map_stone_mo_city"],
    "map_snake_temple_outer": ["map_tager"],
    "map_desert_trade_route": ["map_tager"],
    "map_snake_oasis": ["map_tager"],
    "map_desert_camp": ["map_tager"],
    "map_desert_salt_lake": ["map_tager"],
    "map_desert_ancient_well": ["map_tager"],

    # ═══════════════════════════════════════════════════════════
    # 沧澜帝国 —— 帝都 & 青岚宗
    # ═══════════════════════════════════════════════════════════
    "map_jia_ma_capital": [
        "map_jia_ma_road", "map_magic_mountains",
        "map_alchemist_guild", "map_miteer_auction",
        "map_capital_commercial", "map_imperial_palace",
        "map_capital_alchemist_market", "map_capital_nalan_mansion",
        "map_capital_miteer_hq", "map_capital_arena",
        "map_yunlan",
    ],
    "map_alchemist_guild": ["map_jia_ma_capital"],
    "map_capital_commercial": ["map_jia_ma_capital"],
    "map_imperial_palace": ["map_jia_ma_capital"],
    "map_capital_alchemist_market": ["map_jia_ma_capital"],
    "map_capital_nalan_mansion": ["map_jia_ma_capital"],
    "map_capital_miteer_hq": ["map_jia_ma_capital"],
    "map_capital_arena": ["map_jia_ma_capital"],
    "map_miteer_auction": [
        "map_jia_ma_capital", "map_wutan_commercial_street",
        "map_miteer_appraisal",
    ],
    "map_miteer_appraisal": ["map_miteer_auction"],
    "map_yunlan": [
        "map_jia_ma_capital", "map_yunlan_gate", "map_yunlan_stairs",
        "map_yunlan_square", "map_yunlan_back_cliff", "map_yunlan_elder_hall",
        "map_cloud_mountain_peak", "map_jia_ma_battle_front",
    ],
    "map_yunlan_gate": ["map_yunlan"],
    "map_yunlan_stairs": ["map_yunlan"],
    "map_yunlan_square": ["map_yunlan"],
    "map_yunlan_back_cliff": ["map_yunlan"],
    "map_yunlan_elder_hall": ["map_yunlan"],
    "map_cloud_mountain_peak": ["map_yunlan"],
    "map_yan_alliance_hq": ["map_jia_ma_battle_front", "map_jia_ma_border"],
    "map_jia_ma_battle_front": ["map_yunlan", "map_yan_alliance_hq"],

    # ═══════════════════════════════════════════════════════════
    # 沧澜帝国 —— 边境 → 暗角域
    # ═══════════════════════════════════════════════════════════
    "map_jia_ma_border": [
        "map_jia_ma_mountain_pass", "map_yan_alliance_hq",
        "map_peace_town",
    ],

    # ═══════════════════════════════════════════════════════════
    # 暗角域
    # ═══════════════════════════════════════════════════════════
    "map_peace_town": [
        "map_jia_ma_border", "map_black_corner", "map_canaan",
        "map_peace_town_inn", "map_peace_town_market",
    ],
    "map_peace_town_inn": ["map_peace_town"],
    "map_peace_town_market": ["map_peace_town"],
    "map_black_corner": [
        "map_peace_town", "map_canaan", "map_feng_city",
        "map_black_seal_city", "map_black_emperor_city",
        "map_black_domain_plain", "map_blood_sect", "map_eight_gates",
    ],
    "map_black_domain_plain": ["map_black_corner"],
    "map_blood_sect": ["map_black_corner"],
    "map_eight_gates": ["map_black_corner"],
    "map_black_seal_city": [
        "map_black_corner", "map_black_seal_auction",
        "map_black_seal_market", "map_black_seal_inn",
    ],
    "map_black_seal_auction": ["map_black_seal_city"],
    "map_black_seal_market": ["map_black_seal_city"],
    "map_black_seal_inn": ["map_black_seal_city"],
    "map_canaan": [
        "map_peace_town", "map_black_corner", "map_canaan_inner",
        "map_canaan_outer_square", "map_canaan_library",
        "map_canaan_dormitory", "map_canaan_mission_hall",
        "map_canaan_duel_arena", "map_canaan_trade_street",
    ],
    "map_canaan_outer_square": ["map_canaan"],
    "map_canaan_library": ["map_canaan"],
    "map_canaan_dormitory": ["map_canaan"],
    "map_canaan_mission_hall": ["map_canaan"],
    "map_canaan_duel_arena": ["map_canaan"],
    "map_canaan_trade_street": ["map_canaan"],
    "map_canaan_inner": [
        "map_canaan", "map_skyfire_tower",
        "map_inner_arena", "map_inner_trade_district",
        "map_inner_market", "map_pan_gate",
    ],
    "map_inner_arena": ["map_canaan_inner"],
    "map_inner_trade_district": ["map_canaan_inner"],
    "map_inner_market": ["map_canaan_inner"],
    "map_pan_gate": ["map_canaan_inner"],
    "map_skyfire_tower": [
        "map_canaan_inner", "map_skyfire_lower",
        "map_skyfire_seal_core", "map_skyfire_magma_world",
    ],
    "map_skyfire_lower": ["map_skyfire_tower"],
    "map_skyfire_seal_core": ["map_skyfire_tower"],
    "map_skyfire_magma_world": ["map_skyfire_tower"],
    "map_feng_city": [
        "map_black_corner", "map_black_emperor_city",
        "map_tianya_city", "map_feng_merchant_hall",
        "map_feng_alchemy_room", "map_feng_defense_wall",
        "map_feng_market", "map_black_herb_market", "map_black_inn",
    ],
    "map_feng_merchant_hall": ["map_feng_city"],
    "map_feng_alchemy_room": ["map_feng_city"],
    "map_feng_defense_wall": ["map_feng_city"],
    "map_feng_market": ["map_feng_city"],
    "map_black_herb_market": ["map_feng_city"],
    "map_black_inn": ["map_feng_city"],
    "map_black_emperor_city": [
        "map_black_corner", "map_feng_city", "map_tianya_city",
        "map_black_emperor_market", "map_black_emperor_square",
        "map_black_auction_lane", "map_black_emperor_pavilion",
        "map_xiao_gate",
    ],
    "map_black_emperor_market": ["map_black_emperor_city"],
    "map_black_emperor_square": ["map_black_emperor_city"],
    "map_black_auction_lane": ["map_black_emperor_city"],
    "map_black_emperor_pavilion": ["map_black_emperor_city"],
    "map_xiao_gate": ["map_black_emperor_city"],
    "map_demon_flame_valley": [
        "map_black_corner", "map_demon_valley_hall", "map_demon_valley_archive",
    ],
    "map_demon_valley_hall": ["map_demon_flame_valley"],
    "map_demon_valley_archive": ["map_demon_flame_valley"],
    "map_emperor_cave": [
        "map_black_corner", "map_strange_flame_square",
        "map_emperor_cave_gate", "map_emperor_cave_inner",
        "map_emperor_cave_treasure_room",
    ],
    "map_emperor_cave_gate": ["map_emperor_cave"],
    "map_emperor_cave_inner": ["map_emperor_cave"],
    "map_emperor_cave_treasure_room": ["map_emperor_cave"],

    # ═══════════════════════════════════════════════════════════
    # 天涯城 —— 连接暗角域 ↔ 中州的中转站
    # ═══════════════════════════════════════════════════════════
    "map_tianya_city": [
        "map_feng_city", "map_black_emperor_city",
        "map_zhongzhou",
        "map_tianya_wormhole_square", "map_tianya_market", "map_tianya_inn",
    ],
    "map_tianya_wormhole_square": ["map_tianya_city"],
    "map_tianya_market": ["map_tianya_city"],
    "map_tianya_inn": ["map_tianya_city"],

    # ═══════════════════════════════════════════════════════════
    # 中州
    # ═══════════════════════════════════════════════════════════
    "map_zhongzhou": [
        "map_tianya_city", "map_tianbei_city", "map_ye_city",
        "map_wind_lightning_pavilion", "map_huangquan_pavilion",
        "map_wanjian_pavilion", "map_burning_flame_valley",
        "map_star_pavilion", "map_dan_region",
        "map_soul_mountains", "map_beast_region",
        "map_ancient_realm", "map_wilderness",
        "map_demon_flame_space", "map_sky_demon_sect",
        "map_flower_sect", "map_ancient_ruins",
        "map_heavenly_gang_hall", "map_death_corpse_mountains",
        "map_tianmu_mountains", "map_yao_realm",
        "map_zhongzhou_transfer_square", "map_zhongzhou_inn_district",
        "map_zhongzhou_north_market", "map_zhongzhou_wormhole_station",
        "map_scorching_mountains", "map_qi_feng_mountain",
        "map_tianhuang_city", "map_black_fire_sect",
        "map_space_trade_fair",
    ],
    "map_zhongzhou_transfer_square": ["map_zhongzhou"],
    "map_zhongzhou_inn_district": ["map_zhongzhou"],
    "map_zhongzhou_north_market": ["map_zhongzhou"],
    "map_zhongzhou_wormhole_station": ["map_zhongzhou"],
    "map_scorching_mountains": ["map_zhongzhou"],
    "map_qi_feng_mountain": ["map_zhongzhou"],
    "map_tianhuang_city": [
        "map_zhongzhou", "map_tianhuang_market", "map_tianhuang_inn",
    ],
    "map_tianhuang_market": ["map_tianhuang_city"],
    "map_tianhuang_inn": ["map_tianhuang_city"],
    "map_black_fire_sect": ["map_zhongzhou"],

    # 天北城
    "map_tianbei_city": [
        "map_zhongzhou", "map_tianbei_han_clan",
        "map_tianbei_hong_clan", "map_tianbei_market", "map_tianbei_inn",
    ],
    "map_tianbei_han_clan": ["map_tianbei_city"],
    "map_tianbei_hong_clan": ["map_tianbei_city"],
    "map_tianbei_market": ["map_tianbei_city"],
    "map_tianbei_inn": ["map_tianbei_city"],

    # 叶城
    "map_ye_city": [
        "map_zhongzhou", "map_ice_river_valley",
        "map_ye_mansion", "map_ye_city_gate",
        "map_ye_alchemy_room", "map_ye_market",
    ],
    "map_ye_mansion": ["map_ye_city"],
    "map_ye_city_gate": ["map_ye_city"],
    "map_ye_alchemy_room": ["map_ye_city"],
    "map_ye_market": ["map_ye_city"],
    "map_ice_river_valley": ["map_ye_city"],

    # 四方阁
    "map_wind_lightning_pavilion": ["map_zhongzhou"],
    "map_huangquan_pavilion": ["map_zhongzhou"],
    "map_wanjian_pavilion": ["map_zhongzhou"],
    "map_burning_flame_valley": [
        "map_zhongzhou", "map_burning_valley_market",
    ],
    "map_burning_valley_market": ["map_burning_flame_valley"],
    "map_sky_demon_sect": [
        "map_zhongzhou", "map_sky_demon_gate", "map_sky_demon_hall",
    ],
    "map_sky_demon_gate": ["map_sky_demon_sect"],
    "map_sky_demon_hall": ["map_sky_demon_sect"],

    # 丹域
    "map_dan_region": [
        "map_zhongzhou", "map_sacred_dan_city",
        "map_dan_herb_street", "map_wan_yao_mountains",
        "map_small_dan_tower",
    ],
    "map_dan_herb_street": ["map_dan_region"],
    "map_wan_yao_mountains": ["map_dan_region"],
    "map_small_dan_tower": ["map_dan_region"],
    "map_sacred_dan_city": [
        "map_dan_region", "map_dan_tower",
        "map_sacred_dan_market",
    ],
    "map_sacred_dan_market": ["map_sacred_dan_city"],
    "map_dan_tower": [
        "map_sacred_dan_city", "map_dan_tower_outer_square",
        "map_dan_tower_trial_room", "map_dan_beast_enclosure",
    ],
    "map_dan_tower_outer_square": ["map_dan_tower"],
    "map_dan_tower_trial_room": ["map_dan_tower"],
    "map_dan_beast_enclosure": ["map_dan_tower"],

    # 星落阁
    "map_star_pavilion": [
        "map_zhongzhou", "map_star_realm",
        "map_star_pavilion_back_mountain", "map_star_pavilion_mission_hall",
        "map_star_pavilion_market", "map_star_pavilion_council",
        "map_star_pavilion_alliance_hub",
    ],
    "map_star_pavilion_back_mountain": ["map_star_pavilion"],
    "map_star_pavilion_mission_hall": ["map_star_pavilion"],
    "map_star_pavilion_market": ["map_star_pavilion"],
    "map_star_pavilion_council": ["map_star_pavilion"],
    "map_star_realm": [
        "map_star_pavilion", "map_star_realm_core",
        "map_star_realm_training_ground",
    ],
    "map_star_realm_core": ["map_star_realm"],
    "map_star_realm_training_ground": ["map_star_realm"],

    # 天元联盟
    "map_star_pavilion_alliance_hub": [
        "map_star_pavilion", "map_tianfu_council_hall",
        "map_alliance_war_room",
    ],
    "map_tianfu_council_hall": ["map_star_pavilion_alliance_hub"],
    "map_alliance_war_room": ["map_star_pavilion_alliance_hub"],

    # 花宗
    "map_flower_sect": [
        "map_zhongzhou", "map_flower_sect_gate",
        "map_flower_sect_garden", "map_flower_sect_heritage_hall",
        "map_flower_sect_market",
    ],
    "map_flower_sect_gate": ["map_flower_sect"],
    "map_flower_sect_garden": ["map_flower_sect"],
    "map_flower_sect_heritage_hall": ["map_flower_sect"],
    "map_flower_sect_market": ["map_flower_sect"],

    # 黑渊殿区域 —— 山脉→黑渊殿→魂界 链式
    "map_soul_mountains": ["map_zhongzhou", "map_soul_hall"],
    "map_soul_hall": [
        "map_soul_mountains", "map_soul_realm",
        "map_soul_hall_prison", "map_soul_hall_person_hall",
        "map_soul_hall_soul_well",
    ],
    "map_soul_hall_prison": ["map_soul_hall"],
    "map_soul_hall_person_hall": ["map_soul_hall"],
    "map_soul_hall_soul_well": ["map_soul_hall"],
    "map_soul_realm": [
        "map_soul_hall", "map_hun_clan_space",
        "map_soul_realm_battlefield", "map_soul_emperor_throne",
    ],
    "map_soul_realm_battlefield": ["map_soul_realm"],
    "map_soul_emperor_throne": ["map_soul_realm"],
    "map_hun_clan_space": [
        "map_soul_realm", "map_hun_clan_ritual_site",
        "map_ancient_alliance_camp",
    ],
    "map_hun_clan_ritual_site": ["map_hun_clan_space"],
    "map_ancient_alliance_camp": ["map_hun_clan_space"],
    "map_heavenly_gang_hall": [
        "map_soul_hall", "map_heavenly_gang_prison",
        "map_heavenly_gang_origin",
    ],
    "map_heavenly_gang_prison": ["map_heavenly_gang_hall"],
    "map_heavenly_gang_origin": ["map_heavenly_gang_hall"],

    # 云族区域
    "map_ancient_realm": [
        "map_zhongzhou", "map_ancient_sacred_city", "map_heaven_tomb",
    ],
    "map_ancient_sacred_city": [
        "map_ancient_realm", "map_ancient_city_market",
    ],
    "map_ancient_city_market": ["map_ancient_sacred_city"],
    "map_heaven_tomb": ["map_ancient_realm", "map_heaven_tomb_camp"],
    "map_heaven_tomb_camp": ["map_heaven_tomb"],

    # 远古遗迹 & 兽域
    "map_ancient_ruins": [
        "map_zhongzhou", "map_beast_region",
        "map_ancient_ruins_gate", "map_ancient_ruins_core",
    ],
    "map_ancient_ruins_gate": ["map_ancient_ruins"],
    "map_ancient_ruins_core": ["map_ancient_ruins"],
    "map_beast_region": [
        "map_zhongzhou", "map_ancient_ruins",
        "map_beast_bone_mountains", "map_beast_market",
        "map_beast_region_trade_hub",
    ],
    "map_beast_bone_mountains": ["map_beast_region"],
    "map_beast_market": ["map_beast_region"],
    "map_beast_region_trade_hub": ["map_beast_region"],

    # 莽荒古域 & 菩提古树
    "map_wilderness": [
        "map_zhongzhou", "map_bodhi_tree",
        "map_wilderness_outpost", "map_wilderness_poison_swamp",
        "map_manghuang_inn", "map_manghuang_town",
        "map_heaven_demon_blood_pool", "map_ancient_domain_platform",
    ],
    "map_wilderness_outpost": ["map_wilderness"],
    "map_wilderness_poison_swamp": ["map_wilderness"],
    "map_manghuang_inn": ["map_wilderness"],
    "map_manghuang_town": ["map_wilderness"],
    "map_heaven_demon_blood_pool": ["map_wilderness"],
    "map_ancient_domain_platform": ["map_wilderness"],
    "map_bodhi_tree": ["map_wilderness"],
    "map_space_trade_fair": ["map_zhongzhou"],

    # 天目山脉 & 死亡山脉
    "map_tianmu_mountains": [
        "map_zhongzhou", "map_heaven_mountain_blood_pool",
    ],
    "map_heaven_mountain_blood_pool": ["map_tianmu_mountains"],
    "map_death_corpse_mountains": ["map_zhongzhou"],

    # 药族 —— 药典→玄族袭击→逃亡路线
    "map_yao_realm": [
        "map_zhongzhou", "map_yao_realm_ceremony_square",
    ],
    "map_yao_realm_ceremony_square": [
        "map_yao_realm", "map_yao_realm_herb_garden",
    ],
    "map_yao_realm_herb_garden": [
        "map_yao_realm_ceremony_square", "map_yao_realm_survivor_camp",
    ],
    "map_yao_realm_survivor_camp": ["map_yao_realm_herb_garden"],

    # 源火广场 —— 古帝洞府内部，不直连中州
    "map_strange_flame_square": ["map_emperor_cave"],
    "map_star_domain": ["map_dan_tower"],

    # 净世白莲火空间
    "map_demon_flame_space": [
        "map_zhongzhou", "map_demon_flame_plain",
        "map_demon_flame_illusion_realm", "map_demon_flame_core",
        "map_demon_flame_saint_remains",
    ],
    "map_demon_flame_plain": ["map_demon_flame_space"],
    "map_demon_flame_illusion_realm": ["map_demon_flame_space"],
    "map_demon_flame_core": ["map_demon_flame_space"],
    "map_demon_flame_saint_remains": ["map_demon_flame_space"],

    "map_black_blood_plain": ["map_black_corner"],

    # ═══════════════════════════════════════════════════════════
    # 九幽黄泉
    # ═══════════════════════════════════════════════════════════
    "map_nether_spring": [
        "map_nether_spring_pool", "map_nether_python_tribe",
        "map_nether_underground_palace",
    ],
    "map_nether_spring_pool": ["map_nether_spring"],
    "map_nether_python_tribe": [
        "map_nether_spring", "map_nether_python_throne",
    ],
    "map_nether_python_throne": ["map_nether_python_tribe"],
    "map_nether_underground_palace": ["map_nether_spring"],
    "map_jia_ma": ["map_jia_ma_road", "map_jia_ma_capital"],

    # ═══════════════════════════════════════════════════════════
    # 葬天山脉（最终战连接）
    # ═══════════════════════════════════════════════════════════
    "map_burial_sky_mountains": ["map_double_emperor", "map_zhongzhou"],

    # ═══════════════════════════════════════════════════════════
    # 虚空/龙岛
    # ═══════════════════════════════════════════════════════════
    "map_dragon_island": [
        "map_east_dragon_island", "map_west_dragon_island",
        "map_south_dragon_island", "map_north_dragon_island",
        "map_ancient_dragon_island", "map_dragon_island_harbor",
    ],
    "map_dragon_island_harbor": ["map_dragon_island"],
    "map_east_dragon_island": ["map_dragon_island"],
    "map_west_dragon_island": [
        "map_dragon_island", "map_west_dragon_palace",
    ],
    "map_west_dragon_palace": ["map_west_dragon_island"],
    "map_south_dragon_island": [
        "map_dragon_island", "map_south_dragon_battlefield",
    ],
    "map_south_dragon_battlefield": ["map_south_dragon_island"],
    "map_north_dragon_island": [
        "map_dragon_island", "map_north_dragon_throne",
    ],
    "map_north_dragon_throne": ["map_north_dragon_island"],
    "map_ancient_dragon_island": ["map_dragon_island"],

    # ═══════════════════════════════════════════════════════════
    # 西北大陆
    # ═══════════════════════════════════════════════════════════
    "map_chuyun_empire": [
        "map_poison_sect", "map_golden_goose_sect",
        "map_mulan_valley", "map_scorpion_gate",
        "map_chuyun_border",
    ],
    "map_chuyun_border": ["map_chuyun_empire"],
    "map_poison_sect": [
        "map_chuyun_empire", "map_poison_sect_hall",
        "map_poison_sect_herb_cave",
    ],
    "map_poison_sect_hall": ["map_poison_sect"],
    "map_poison_sect_herb_cave": ["map_poison_sect"],
    "map_golden_goose_sect": ["map_chuyun_empire"],
    "map_mulan_valley": ["map_chuyun_empire"],
    "map_scorpion_gate": [
        "map_chuyun_empire", "map_scorpion_hall", "map_scorpion_cave",
    ],
    "map_scorpion_hall": ["map_scorpion_gate"],
    "map_scorpion_cave": ["map_scorpion_gate"],
    "map_xuanhuang_fortress": [
        "map_chuyun_empire", "map_northwest_battle_front",
        "map_xuanhuang_war_hall", "map_xuanhuang_defense_wall",
    ],
    "map_xuanhuang_war_hall": ["map_xuanhuang_fortress"],
    "map_xuanhuang_defense_wall": ["map_xuanhuang_fortress"],
    "map_northwest_battle_front": ["map_xuanhuang_fortress"],

    # ═══════════════════════════════════════════════════════════
    # 最终战场
    # ═══════════════════════════════════════════════════════════
    "map_double_emperor": [
        "map_double_emperor_peak", "map_allied_forces_camp",
    ],
    "map_double_emperor_peak": ["map_double_emperor"],
    "map_allied_forces_camp": ["map_double_emperor"],
    "map_emperor_memorial_peak": ["map_double_emperor"],
    "map_world_gate": ["map_double_emperor"],
    "map_emperor_ascension_platform": ["map_emperor_memorial_peak"],
}


_REGION_NPCS: Dict[str, List[str]] = {
    "沧澜": ["npc_lin_zhan", "npc_yun_xi", "npc_xuanlu_elder"],
    "暗角域": ["npc_hai_bodong", "npc_zi_yan"],
    "中州": ["npc_feng_xian", "npc_chi_lin", "npc_yun_xi"],
    "丹阁": ["npc_xuan_kongzi", "npc_cao_ying"],
    "云族": ["npc_yun_xi", "npc_yun_yuan"],
    "龙岛": ["npc_zi_yan", "npc_zhu_kun"],
    "西北": ["npc_chi_lin", "npc_xiao_ding"],
}


def _connected_maps(map_id: str) -> List[str]:
    """返回从当前地图可直接前往的地图 ID 列表。"""
    if map_id in _MAP_CONNECTIONS:
        return _MAP_CONNECTIONS[map_id]
    # 未在表中的地图：找同前缀地图互连
    prefix = "_".join(map_id.split("_")[:2])
    connected = []
    for mid in _MAP_CONNECTIONS:
        if mid.startswith(prefix) and mid != map_id:
            connected.append(mid)
    if connected:
        return connected
    # 最后回退：同区域
    region = REGION_BY_MAP.get(map_id, "")
    return [mid for mid, r in REGION_BY_MAP.items() if r == region and mid != map_id]

def _pick_npcs_for_map(map_id: str) -> List[str]:
    """根据地图所在区域返回可能出现的 NPC ID 列表。"""
    region = REGION_BY_MAP.get(map_id, "")
    for key, npcs in _REGION_NPCS.items():
        if key in region:
            return npcs
    return ["npc_lin_zhan"]  # 默认


# ── 地图分类 → 模板选择 ──────────────────────────────────────

_MAP_TEMPLATES = {
    # 城镇类
    "mansion": _mansion_template,           # 府邸
    "training": _training_ground_template,  # 演武场
    "market": _town_square_template,        # 商业街
    "inn": _town_square_template,           # 客栈区域
    "square": _town_square_template,        # 广场
    "hall": _mansion_template,              # 大厅
    "gate": _training_ground_template,      # 城门
    "garrison": _training_ground_template,  # 军营
    "library": _mansion_template,           # 藏书阁
    "dormitory": _mansion_template,         # 宿舍
    "arena": _training_ground_template,     # 竞技场
    "district": _town_square_template,      # 街区
    "chamber": _mansion_template,           # 密室
    "room": _mansion_template,              # 房间
    "pavilion": _mansion_template,          # 阁楼
    "tower": _wilderness_cave,              # 塔楼（类似洞穴）
    "council": _mansion_template,           # 议事厅
    # 野外类
    "forest": _wilderness_forest,
    "mountain": _wilderness_forest,
    "desert": _wilderness_desert,
    "cave": _wilderness_cave,
    "ruins": _wilderness_cave,
    "valley": _wilderness_forest,
    "plain": _wilderness_desert,
    "swamp": _wilderness_forest,
    "river": _wilderness_forest,
    "lake": _wilderness_forest,
    "sea": _wilderness_desert,
    "island": _wilderness_forest,
    "pass": _wilderness_desert,
    "road": _wilderness_desert,
}


def _pick_template(map_id: str, safe: bool, name: str) -> Tuple[int, int, list, list]:
    """根据地图属性选择/生成模板。"""
    name_lower = name + map_id
    if safe:
        for keyword, tmpl in _MAP_TEMPLATES.items():
            if keyword in name_lower and not tmpl.__name__.startswith("_wilderness_"):
                return tmpl(map_id)
        return _town_square_template(map_id)
    else:
        for keyword, tmpl in _MAP_TEMPLATES.items():
            if keyword in name_lower:
                w, h, tiles, entities = tmpl(map_id)
                return _auto_populate_wild(w, h, tiles, entities, name, map_id)
        w, h, tiles, entities = _wilderness_forest(map_id)
        return _auto_populate_wild(w, h, tiles, entities, name, map_id)


def _auto_populate_wild(w, h, tiles, entities, name, map_id):
    """Auto-add enemies and gathering nodes to wilderness maps."""
    import random as _rnd
    level_hint = 5
    for kw, lv in [
        ("magic_mountains",5),("inner",15),("deep",25),("black_corner",22),
        ("canaan",20),("tager",30),("dan_region",35),("skyfire",40),
        ("beast_region",45),("dragon_island",55),("soul_mountains",60),
        ("ancient_ruins",65),("heaven_tomb",70),("yao_realm",75),
        ("bodhi_tree",65),("gu_clan",70),("demon_flame",80),
        ("emperor_cave",90),("wilderness",15),("desert",10),("cave",8),
        ("mountain",12),("valley",18),("peak",25),("abyss",35),
        ("tundra",28),("swamp",20),("volcano",30),("ruins",40),("tomb",50),
    ]:
        if kw in map_id.lower() or kw in name.lower():
            level_hint = lv
            break
    existing_enemies = sum(1 for e in entities if e[2] == ENTITY_ENEMY)
    existing_gather = sum(1 for e in entities if e[2] in (ENTITY_TREASURE, ENTITY_GATHER))
    target_enemies = max(3, min(8, level_hint // 8))
    enemies_added = 0
    for _ in range(target_enemies - existing_enemies):
        for __ in range(30):
            x, y = _rnd.randint(1, w-2), _rnd.randint(1, h-3)
            blocked = False
            for e in entities:
                if e[0] == x and e[1] == y:
                    blocked = True
                    break
            if blocked:
                continue
            for t in tiles:
                if t[0] == x and t[1] == y and t[2] in (TILE_WALL, TILE_WATER):
                    blocked = True
                    break
            if not blocked:
                enemy_label = _rnd.choice(["\u9b54\u517d","\u86c7\u4eba","\u76d7\u532a","\u5996\u517d","\u4ea1\u7075","\u5b88\u536b"])
                entities.append((x, y, ENTITY_ENEMY, enemy_label))
                enemies_added += 1
                break
    target_gather = max(2, min(6, level_hint // 12))
    gather_added = 0
    for _ in range(target_gather - existing_gather):
        for __ in range(30):
            x, y = _rnd.randint(1, w-2), _rnd.randint(1, h-3)
            blocked = False
            for e in entities:
                if e[0] == x and e[1] == y:
                    blocked = True
                    break
            if blocked:
                continue
            for t in tiles:
                if t[0] == x and t[1] == y and t[2] in (TILE_WALL, TILE_WATER):
                    blocked = True
                    break
            if not blocked:
                gather_label = _rnd.choice(["\u836f\u6750","\u77ff\u77f3","\u517d\u6750","\u7075\u8349","\u9b54\u6838","\u6676\u77f3"])
                entities.append((x, y, ENTITY_GATHER, gather_label))
                gather_added += 1
                break
    return w, h, tiles, entities

def _build_tile_map(w, h, tile_defs, entity_defs):
    """根据模板定义构建瓦片网格和实体字典。"""
    grid = [[TILE_FLOOR for _ in range(w)] for _ in range(h)]
    for x, y, tile in tile_defs:
        if 0 <= x < w and 0 <= y < h:
            grid[y][x] = tile
    entities: Dict[Tuple[int, int], int] = {}
    entity_labels: Dict[Tuple[int, int], str] = {}
    for x, y, etype, label in entity_defs:
        if 0 <= x < w and 0 <= y < h and grid[y][x] != TILE_WALL:
            entities[(x, y)] = etype
            entity_labels[(x, y)] = label
    return grid, entities, entity_labels


# ═══════════════════════════════════════════════════════════════════
# 字体
# ═══════════════════════════════════════════════════════════════════

def _load_font(size: int) -> pygame.font.Font:
    for path in [
        "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]:
        if Path(path).exists():
            return pygame.font.Font(path, size)
    return pygame.font.Font(None, size)


def _wrap_text(font: pygame.font.Font, text: str, max_width: int) -> List[str]:
    """按实际渲染宽度拆分文本，避免中文名称超出面板。"""
    lines: List[str] = []
    current = ""
    for char in str(text):
        if char == "\n":
            lines.append(current)
            current = ""
            continue
        candidate = current + char
        if current and font.size(candidate)[0] > max_width:
            lines.append(current)
            current = char
        else:
            current = candidate
    if current or not lines:
        lines.append(current)
    return lines


# ═══════════════════════════════════════════════════════════════════
# 主游戏类
# ═══════════════════════════════════════════════════════════════════

class PygameGame:
    """残火长明 RPG — pygame 瓦片探索界面。"""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("残火长明 · 大陆历练")
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock = pygame.time.Clock()
        self.running = True

        # ── 音效 ──
        self.sound_enabled = True
        self.sound_volume = 0.6
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.ambient_sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.ambient_channel: Optional[pygame.mixer.Channel] = None
        self.current_ambient = ""
        try:
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            pygame.mixer.set_num_channels(16)
            pygame.mixer.set_reserved(1)
            self.ambient_channel = pygame.mixer.Channel(0)
            self._init_sounds()
        except Exception:
            self.sound_enabled = False

        self.font_title = _load_font(22)
        self.font_body = _load_font(16)
        self.font_small = _load_font(13)
        self.font_big = _load_font(28)

        self.engine = GameEngine()
        self.engine.new_game("林烬")

        # 地图数据
        self.tile_grid: List[List[int]] = []
        self.tile_entities: Dict[Tuple[int, int], int] = {}
        self.entity_labels: Dict[Tuple[int, int], str] = {}
        self.player_pos = (0, 0)
        self._load_map()

        # 消息
        self.messages: List[str] = []
        self._msg("灵玄大陆的故事由此开始。方向键移动，空格交互，M 菜单。")

        # 场景
        self.scene = SCENE_EXPLORE
        self.combat_ui: Optional[CombatView] = None
        self.shop_items: List[str] = []
        self.shop_sell_mode = False
        self.menu_idx = 0
        self.select_idx = 0
        self.gift_item_id: Optional[str] = None
        self.gift_target_idx = 0
        self.travel_options: List[Tuple[str, str, str]] = []  # (map_id, name, route)
        self.travel_idx = 0
        # 遭遇/对话框
        self.encounter_options_data: List[Tuple[int, Dict[str, Any]]] = []
        self.encounter_idx = 0
        self.encounter_text = ""
        # 战斗子菜单
        self.skill_list: List[Dict[str, Any]] = []
        self.skill_idx = 0
        self.item_list: List[str] = []
        self.item_idx = 0

    # ── 音效 ──────────────────────────────────────────────────

    def _init_sounds(self) -> None:
        """根据多段波形配方生成完整音效库。"""
        try:
            import struct
            sample_rate = 22050

            def _make_sound(
                recipe: List[Tuple[int, int, str, float]]
            ) -> Optional[pygame.mixer.Sound]:
                buf = bytearray()
                phase_offset = 0
                for freq, duration_ms, wave_type, volume in recipe:
                    n_samples = max(1, int(sample_rate * duration_ms / 1000))
                    for i in range(n_samples):
                        t = (phase_offset + i) / sample_rate
                        if wave_type == "square":
                            value = 1 if int(t * freq * 2) % 2 == 0 else -1
                        elif wave_type == "sine":
                            value = math.sin(2 * math.pi * freq * t)
                        elif wave_type == "noise":
                            value = random.Random(phase_offset + i).uniform(-1, 1)
                        else:
                            value = 0
                        attack = min(1.0, i / max(1, n_samples * 0.08))
                        decay = max(0.0, 1.0 - i / n_samples)
                        buf.extend(struct.pack("<h", int(value * attack * decay * volume * 24000)))
                    phase_offset += n_samples
                sound = pygame.mixer.Sound(buffer=bytes(buf))
                sound.set_volume(self.sound_volume)
                return sound

            def _make_ambient(
                base_freq: int, pulse_freq: int, noise_level: float
            ) -> Optional[pygame.mixer.Sound]:
                duration_seconds = 4
                n_samples = sample_rate * duration_seconds
                buf = bytearray()
                noise = random.Random(base_freq)
                for i in range(n_samples):
                    t = i / sample_rate
                    fade = min(1.0, i / (sample_rate * 0.25))
                    fade *= min(1.0, (n_samples - i) / (sample_rate * 0.25))
                    drone = math.sin(2 * math.pi * base_freq * t) * 0.45
                    overtone = math.sin(2 * math.pi * base_freq * 1.5 * t) * 0.18
                    pulse = math.sin(2 * math.pi * pulse_freq * t) * 0.12
                    texture = noise.uniform(-1, 1) * noise_level
                    value = (drone + overtone + pulse + texture) * fade
                    buf.extend(struct.pack("<h", int(value * 5000)))
                return pygame.mixer.Sound(buffer=bytes(buf))

            self.sounds = {
                name: _make_sound(recipe)
                for name, recipe in PROGRAMMATIC_SOUND_RECIPES.items()
            }
            self.ambient_sounds = {
                name: _make_ambient(*profile)
                for name, profile in PROGRAMMATIC_AMBIENT_PROFILES.items()
            }
        except Exception:
            self.sound_enabled = False

    def _play_sound(self, name: str) -> None:
        if not self.sound_enabled:
            return
        s = self.sounds.get(name)
        if s:
            s.play()

    def _set_sound_volume(self, delta: float) -> None:
        was_enabled = self.sound_enabled
        self.sound_volume = max(0.0, min(1.0, self.sound_volume + delta))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.sound_volume)
        if self.ambient_channel:
            self.ambient_channel.set_volume(self.sound_volume * 0.28)
        self.sound_enabled = self.sound_volume > 0
        if self.ambient_channel:
            if self.sound_enabled and not was_enabled:
                self.ambient_channel.unpause()
            elif not self.sound_enabled:
                self.ambient_channel.pause()
        self._msg(f"音效音量：{int(self.sound_volume * 100)}%")
        if self.sound_enabled:
            self._play_sound("confirm")

    def _toggle_sound(self) -> None:
        self.sound_enabled = not self.sound_enabled
        if self.ambient_channel:
            if self.sound_enabled:
                self.ambient_channel.unpause()
            else:
                self.ambient_channel.pause()
        self._msg("音效已开启。" if self.sound_enabled else "音效已静音。")
        if self.sound_enabled:
            self._play_sound("confirm")

    def _play_combat_result(self, result: str, action: str) -> None:
        if result == "won":
            self._play_sound("victory")
        elif result == "lost":
            self._play_sound("defeat")
        elif action == "escape":
            self._play_sound("escape")
        else:
            sound_by_action = {
                "attack": "critical" if "触发暴击" in self.engine.last_message else "hit",
                "skill": "skill",
                "item": "item",
                "defend": "defend",
                "charge": "charge",
                "auto": "confirm",
            }
            self._play_sound(sound_by_action.get(action, "confirm"))

    def _play_ambient(self, name: str) -> None:
        if name == self.current_ambient:
            return
        self.current_ambient = name
        if not self.ambient_channel:
            return
        sound = self.ambient_sounds.get(name)
        if sound:
            self.ambient_channel.set_volume(self.sound_volume * 0.28)
            self.ambient_channel.play(sound, loops=-1, fade_ms=350)
            if not self.sound_enabled:
                self.ambient_channel.pause()

    def _play_map_ambient(self) -> None:
        md = self.engine.current_map()
        if md.get("safe_zone", False):
            self._play_ambient("city")
        elif self._map_theme() in {"battlefield", "volcanic", "poison", "void"}:
            self._play_ambient("danger")
        else:
            self._play_ambient("wild")

    # ── 消息 ──────────────────────────────────────────────────

    def _msg(self, text: str) -> None:
        if self.engine.last_message:
            self.messages.append(self.engine.last_message)
        self.messages.append(text)
        if len(self.messages) > 8:
            self.messages = self.messages[-8:]

    # ── 地图 ──────────────────────────────────────────────────

    def _load_map(self) -> None:
        """根据当前地图数据生成瓦片布局。"""
        md = self.engine.current_map()
        mid = md.get("id", "map_wutan")
        safe = md.get("safe_zone", False)
        name = md.get("name", mid)

        w, h, tdefs, edefs = _pick_template(mid, safe, name)
        self.map_w, self.map_h = w, h
        self.tile_grid, self.tile_entities, self.entity_labels = _build_tile_map(
            w, h, tdefs, edefs
        )
        # 出生点优先靠近中心，但不会再覆盖城市地标或水景。
        preferred = (w // 2, h // 2)
        candidates = [
            (x, y)
            for y in range(h)
            for x in range(w)
            if not self._pos_blocked(x, y) and (x, y) not in self.tile_entities
        ]
        self.player_pos = min(
            candidates,
            key=lambda pos: (
                abs(pos[0] - preferred[0]) + abs(pos[1] - preferred[1]),
                abs(pos[1] - (h - 3)),
            ),
            default=preferred,
        )
        self._play_map_ambient()

    def _pos_blocked(self, x: int, y: int) -> bool:
        if not self.tile_grid:
            return True
        h = len(self.tile_grid)
        if not (0 <= y < h):
            return True
        w = len(self.tile_grid[y])
        if not (0 <= x < w):
            return True
        return self.tile_grid[y][x] in (TILE_WALL, TILE_WATER, TILE_GARDEN, TILE_LANDMARK)

    def _entity_at(self, x: int, y: int) -> Optional[int]:
        return self.tile_entities.get((x, y))

    def _label_at(self, x: int, y: int) -> str:
        return self.entity_labels.get((x, y), "")

    # ── 地图切换 ─────────────────────────────────────────────

    def _travel_to(self, map_id: str) -> None:
        if self.engine.travel(map_id):
            self._load_map()
            md = self.engine.current_map()
            self._play_sound("travel")
            self._msg(f"来到了 {md.get('name', map_id)}。")
        else:
            self._play_sound("bump")
            self._msg(self.engine.last_message)

    def _exit_map(self) -> None:
        """触发出口——只显示当前地图可直接到达的邻接地。

        每个路口只连接到特定的几张地图，不是全部区域。
        连接关系定义在 _MAP_CONNECTIONS 中。
        """
        cur = self.engine.player.get("last_map", "")
        connected = _connected_maps(cur)

        # 过滤：只保留已解锁的地图
        reachable = []
        for mid in connected:
            m = self.engine.maps.get(mid, {})
            if not m:
                continue
            # 检查剧情解锁
            if not self.engine.is_map_unlocked(mid):
                continue
            # 夜间不能去危险区域
            if self.engine.player["time_period"] == 3 and not m.get("safe_zone", False):
                continue
            region = REGION_BY_MAP.get(mid, "")
            reachable.append((mid, m.get("name", mid), f"「{region}」"))

        if not reachable:
            self._play_sound("bump")
            self._msg("此路暂时不通。也许需要推进剧情解锁新的区域？")
            return

        if len(reachable) == 1:
            self._travel_to(reachable[0][0])
            return

        self.scene = SCENE_TRAVEL
        self.travel_options = [(mid, name, route) for mid, name, route in reachable]
        self.travel_idx = 0

    # ── 事件处理 ────────────────────────────────────────────

    def run(self) -> None:
        while self.running:
            self.clock.tick(FPS)
            self._handle_events()
            self._render()
        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._on_key(event)

    def _on_key(self, e: pygame.event.Event) -> None:
        if e.key == pygame.K_F9:
            self._toggle_sound()
            return
        if e.key == pygame.K_F10:
            self._set_sound_volume(-0.1)
            return
        if e.key == pygame.K_F11:
            self._set_sound_volume(0.1)
            return
        if self.scene == SCENE_EXPLORE:
            self._key_explore(e)
        elif self.scene == SCENE_COMBAT and self.combat_ui:
            self.combat_ui.handle_key(e, self.engine, self)
            if self.engine.combat is None:
                self.scene = SCENE_EXPLORE
                self.combat_ui = None
                self._play_map_ambient()
                self._msg(self.engine.last_message)
        elif self.scene == SCENE_ENCOUNTER:
            self._key_encounter(e)
        elif self.scene == "dialogue":
            if e.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                self._play_sound("confirm" if e.key != pygame.K_ESCAPE else "cancel")
                self.scene = SCENE_EXPLORE
        elif self.scene == SCENE_SHOP:
            self._key_shop(e)
        elif self.scene == SCENE_INN:
            if e.key == pygame.K_SPACE or e.key == pygame.K_RETURN:
                if self.engine.rest():
                    self._play_sound("rest")
                    self._msg("休息完毕，生命与体力已恢复。")
                self.scene = SCENE_EXPLORE
            elif e.key == pygame.K_ESCAPE:
                self._play_sound("cancel")
                self.scene = SCENE_EXPLORE
        elif self.scene == SCENE_MENU:
            self._key_menu(e)
        elif self.scene == SCENE_INVENTORY:
            self._key_inventory(e)
        elif self.scene == SCENE_TRAVEL:
            self._key_travel(e)

    def _key_travel(self, e: pygame.event.Event) -> None:
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_EXPLORE
        elif e.key == pygame.K_UP:
            self.travel_idx = max(0, self.travel_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.travel_idx = min(len(self.travel_options) - 1, self.travel_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.travel_options:
                mid = self.travel_options[self.travel_idx][0]
                self._travel_to(mid)
                self.scene = SCENE_EXPLORE

    def _key_explore(self, e: pygame.event.Event) -> None:
        k = e.key
        dx = dy = 0
        if k in (pygame.K_UP, pygame.K_w):       dy = -1
        elif k in (pygame.K_DOWN, pygame.K_s):    dy = 1
        elif k in (pygame.K_LEFT, pygame.K_a):    dx = -1
        elif k in (pygame.K_RIGHT, pygame.K_d):   dx = 1
        elif k in (pygame.K_SPACE, pygame.K_RETURN):
            self._interact_nearby()
            return
        elif k == pygame.K_r:    self._do_rest(); return
        elif k == pygame.K_c:    self._do_cultivate(); return
        elif k == pygame.K_i:
            self._play_sound("confirm")
            self.scene = SCENE_INVENTORY
            self.select_idx = 0
            return
        elif k == pygame.K_m:
            self._play_sound("confirm")
            self.scene = SCENE_MENU
            self.menu_idx = 0
            return
        elif k == pygame.K_ESCAPE: self.running = False; return

        if dx or dy:
            nx, ny = self.player_pos[0] + dx, self.player_pos[1] + dy
            if self._pos_blocked(nx, ny):
                self._play_sound("bump")
                return  # 撞墙
            ent = self._entity_at(nx, ny)
            if ent is not None:
                dp = self.defeated_tiles.get((nx, ny), -999)
                cp = self.engine._current_period()
                if cp - dp >= 6:
                    self._trigger_entity(nx, ny, ent)
                elif ent != ENTITY_EXIT:
                    remaining = 6 - (cp - dp)
                    self._msg(f"This spot will refresh in {remaining} periods")
                return
            self.player_pos = (nx, ny)
            self._on_step()

    def _on_step(self) -> None:
        """每步触发可能遭遇（战斗或剧情奇遇）。"""
        self._play_sound("step")
        r = random.random()
        # 剧情奇遇: 20% 概率触发
        if r < 0.06 and self.engine.encounters:
            self._trigger_random_encounter()
        # 随机战斗: 4% 概率再判定
        elif r < 0.10:
            level = int(self.engine.player["level"])
            candidates = [
                eid for eid, ed in self.engine.enemies.items()
                if abs(ed.get("level", 1) - level) <= 4
            ]
            if candidates and random.random() < 0.4:
                self.engine.begin_combat(random.choice(candidates))
                if self.engine.combat:
                    self._play_sound("alert")
                    self._play_ambient("battle")
                    self.scene = SCENE_COMBAT
                    self.combat_ui = CombatView()
                    self._msg(f"遭遇了 {self.engine.combat['name']}！")

    def _trigger_random_encounter(self) -> None:
        """触发当前地图的随机剧情奇遇。"""
        cur = self.engine.player.get("last_map", "")
        map_encounters = [
            enc for enc in self.engine.encounters
            if enc["map_id"] == cur
            and self.engine.check_conditions(enc.get("conditions"))
        ]
        if not map_encounters:
            return
        enc = random.choice(map_encounters)
        self.engine.active_encounter = enc
        self.encounter_text = enc.get("text", "")
        self.encounter_options_data = self.engine.encounter_options()
        self.encounter_idx = 0
        self.scene = SCENE_ENCOUNTER
        self._play_sound("alert")

    def _interact_nearby(self) -> None:
        """与相邻格或玩家位置上的实体交互。"""
        px, py = self.player_pos
        for (ex, ey), etype in self.tile_entities.items():
            if max(abs(ex - px), abs(ey - py)) <= 1:
                self._trigger_entity(ex, ey, etype)
                return
        self._msg("附近没有可交互的对象。")

    def _trigger_entity(self, x: int, y: int, etype: int) -> None:
        """触发指定实体。"""
        self._play_sound("confirm")
        if etype == ENTITY_EXIT:
            self._exit_map()
        elif etype == ENTITY_ENEMY:
            self._start_combat_at(x, y)
        elif etype == ENTITY_TREASURE:
            self._open_treasure(x, y)
        elif etype == ENTITY_SHOP:
            self._open_shop()
        elif etype == ENTITY_INN:
            self._open_inn()
        elif etype == ENTITY_GUILD:
            self._open_guild()
        elif etype == ENTITY_NPC:
            self._talk_npc(x, y)

    def _start_combat_at(self, x: int, y: int) -> None:
        """根据地图难度匹配敌人。"""
        md = self.engine.current_map()
        map_level = md.get("recommend_level", 1)
        level = int(self.engine.player["level"])
        candidates = [
            eid for eid, ed in self.engine.enemies.items()
            if abs(ed.get("level", 1) - max(level, map_level)) <= 5
            and abs(ed.get("level", 1) - level) <= 6
            and ed.get("type", "") not in ("boss", "final_boss")
        ]
        if not candidates:
            candidates = list(self.engine.enemies.keys())
        if candidates:
            self.engine.begin_combat(random.choice(candidates))
            if self.engine.combat:
                self._play_sound("alert")
                self._play_ambient("battle")
                self.scene = SCENE_COMBAT
                self.combat_ui = CombatView()
                self._msg(f"与 {self.engine.combat['name']} 展开了战斗！")
                # Mark for respawn instead of permanent removal
                self.defeated_tiles[(x, y)] = self.engine._current_period()


    def _open_gather(self, x: int, y: int) -> None:
        """Collect materials from a gathering node."""
        import random as _rnd
        from wordworld.core.engine import GameEngine
        from wordworld.data.loot_table import LOOT_TABLE
        map_lv = self.engine.current_map().get("recommend_level", 1)
        tier = GameEngine._tier_for_level(map_lv)
        pool = LOOT_TABLE.get(tier, [])
        mat_ids, mat_weights = [], []
        for pid, weight in pool:
            rule = self.engine.item_rules.get(pid, {})
            itype = rule.get("type", "")
            if itype in ("material", "consumable") and not pid.startswith("eq_"):
                mat_ids.append(pid)
                mat_weights.append(weight)
        if not mat_ids:
            self._msg("Nothing here...")
            return
        count = _rnd.randint(1, 3)
        total_w = max(1, sum(mat_weights))
        found = []
        for _ in range(count):
            r = _rnd.randint(1, total_w)
            cum = 0
            for i, w in enumerate(mat_weights):
                cum += w
                if r <= cum:
                    lid = mat_ids[i]
                    if lid not in self.engine.player.get("items", []):
                        self.engine.player["items"].append(lid)
                    found.append(self.engine.item_name(lid))
                    break
        if found:
            self._msg("Gathered: " + ", ".join(found))
        self.engine.advance_time(1)
        self.defeated_tiles[(x, y)] = self.engine._current_period()

    def _open_treasure(self, x: int, y: int) -> None:
        copper = random.randint(50, 250)
        self.engine.apply_effects(f"silver:+{copper}")
        wtext = wallet_display(wallet_normalize({"copper":copper,"silver":0,"gold":0,"ancient":0}))
        # 随机给个道具
        items = list(self.engine.item_rules.keys())
        if items and random.random() < 0.4:
            pick = random.choice(items)
            if pick not in self.engine.player["items"]:
                self.engine.player["items"].append(pick)
                self._msg(f"发现宝箱！获得 {wtext} 和 {self.engine.item_name(pick)}。")
            else:
                self._msg(f"发现宝箱！获得 {wtext}。")
        else:
            self._msg(f"发现宝箱！获得 {wtext}。")
        self._play_sound("treasure")
        self.tile_entities.pop((x, y), None)
        self.entity_labels.pop((x, y), None)

    # ── 城镇功能 ─────────────────────────────────────────────

    def _open_shop(self) -> None:
        """打开商店——基于 Excel 物品类型定价。"""
        self.scene = SCENE_SHOP
        self.shop_sell_mode = False
        # 商店出售消耗品和装备（排除 quest/currency/key 类）
        shop_types = {"consumable", "equipment", "book", "material", "heavenly_flame"}
        self.shop_items = [
            iid for iid, rule in self.engine.item_rules.items()
            if rule.get("type", "") in shop_types
        ]
        self.select_idx = 0

    def _key_shop(self, e: pygame.event.Event) -> None:
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_EXPLORE
        elif e.key == pygame.K_TAB:
            self.shop_sell_mode = not self.shop_sell_mode
            self.select_idx = 0
            self._play_sound("confirm")
        elif e.key in (pygame.K_UP, pygame.K_w):
            self.select_idx = max(0, self.select_idx - 1)
            self._play_sound("select")
        elif e.key in (pygame.K_DOWN, pygame.K_s):
            items = self.shop_items if not self.shop_sell_mode else self.engine.player.get("items", [])
            self.select_idx = min(max(0, len(items) - 1), self.select_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.shop_sell_mode:
                self._sell_item()
            else:
                self._buy_item()

    def _buy_item(self) -> None:
        if self.select_idx >= len(self.shop_items):
            return
        item_id = self.shop_items[self.select_idx]
        rule = self.engine.item_rules[item_id]
        buy_price, _ = item_price(rule.get("type", ""))
        if wallet_can_afford(self.engine.player.get("wallet", {}), buy_price):
            self.engine.player["wallet"] = wallet_add(self.engine.player["wallet"], -buy_price)
            if item_id not in self.engine.player["items"]:
                self.engine.player["items"].append(item_id)
            self._play_sound("buy")
            self._msg(f"购买了 {self.engine.item_name(item_id)}，花费 {buy_price} 银两。")
        else:
            self._play_sound("bump")
            self._msg(f"资金不足！需要 {buy_price} 铜币。")

    def _sell_item(self) -> None:
        inv = self.engine.player.get("items", [])
        if self.select_idx >= len(inv):
            return
        item_id = inv[self.select_idx]
        rule = self.engine.item_rules.get(item_id, {})
        _, sell_price = item_price(rule.get("type", ""))
        self.engine.player["items"].remove(item_id)
        self.engine.player["wallet"] = wallet_add(self.engine.player["wallet"], sell_price)
        self._play_sound("sell")
        self._msg(f"出售了 {self.engine.item_name(item_id)}，获得 {sell_price} 银两。")

    def _open_inn(self) -> None:
        self.scene = SCENE_INN
        md = self.engine.current_map()
        self._msg(f"欢迎来到 {md.get('name', '客栈')}。按空格休息（恢复生命和体力），Esc 离开。")

    def _open_guild(self) -> None:
        self.scene = "dialogue"
        self._msg("公会管事：「少侠，当前暂无适合你的任务。继续历练吧。」")

    def _talk_npc(self, x: int, y: int) -> None:
        label = self._label_at(x, y)
        # 从 Excel NPC 数据取真实名字
        npc_name = self.engine.npc_names.get(label, label)
        # 关系感知对话
        rel_value = 0
        try:
            rel_value = self.engine.relation_value(label)
        except KeyError:
            pass

        intro = self.engine.npc_profiles.get(label, {}).get("Dialogue_Intro", "")
        if intro:
            text = f"{npc_name}：「{intro}」"
        elif rel_value >= 40:
            text = f"{npc_name}：「少侠，好久不见！有你在，我们安心多了。」"
        elif rel_value <= -20:
            text = f"{npc_name}：「哼，你还敢来这里？」"
        else:
            md = self.engine.current_map()
            if md.get("safe_zone", False):
                text = f"{npc_name}：「这里是{md.get('name', '本地')}，少侠若需要补给，坊市就在附近。」"
            else:
                text = f"{npc_name}：「此处凶险，少侠千万小心。」"
        self._msg(text)
        self.scene = "dialogue"

    # ── 剧情奇遇 ─────────────────────────────────────────────

    def _key_encounter(self, e: pygame.event.Event) -> None:
        if e.key == pygame.K_UP:
            self.encounter_idx = max(0, self.encounter_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.encounter_idx = min(len(self.encounter_options_data) - 1, self.encounter_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            opt_num = self.encounter_options_data[self.encounter_idx][0]
            ok = self.engine.choose_encounter_option(opt_num)
            self._play_sound("story" if ok else "bump")
            self._msg(self.engine.last_message)
            self.scene = SCENE_EXPLORE
        elif e.key == pygame.K_ESCAPE:
            self.engine.leave_encounter()
            self._play_sound("cancel")
            self._msg(self.engine.last_message)
            self.scene = SCENE_EXPLORE

    def _do_rest(self) -> None:
        if self.engine.rest():
            self._play_sound("rest")
            self._msg("休息完毕，生命与体力已恢复。")
        else:
            self._play_sound("bump")
            self._msg(self.engine.last_message)

    def _do_cultivate(self) -> None:
        if self.engine.cultivate():
            self._play_sound("cultivate")
            self._msg(self.engine.last_message)
        else:
            self._play_sound("bump")
            self._msg(self.engine.last_message)

    # ── 菜单 ─────────────────────────────────────────────────

    def _key_menu(self, e: pygame.event.Event) -> None:
        items = ["返回游戏", "状态详情", "物品背包", "技能列表", "保存游戏", "读取存档", "退出游戏"]
        if e.key == pygame.K_UP:
            self.menu_idx = max(0, self.menu_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.menu_idx = min(len(items) - 1, self.menu_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._play_sound("confirm")
            if self.menu_idx == 0:
                self.scene = SCENE_EXPLORE
            elif self.menu_idx == 1:
                self.scene = SCENE_EXPLORE  # 状态在右侧面板
            elif self.menu_idx == 2:
                self.scene = SCENE_INVENTORY
                self.select_idx = 0
            elif self.menu_idx == 3:
                self.scene = SCENE_EXPLORE
                skills = self.engine.player.get("known_skills", [])
                names = [self.engine.skills.get(s, {}).get("name", s) for s in skills]
                self._msg(f"已学灵技：{'、'.join(names) if names else '无'}")
            elif self.menu_idx == 4:
                self.engine.save()
                self._play_sound("save")
                self._msg("游戏已保存。")
                self.scene = SCENE_EXPLORE
            elif self.menu_idx == 5:
                if self.engine.load():
                    self._load_map()
                    self._play_sound("load")
                    self._msg("存档已读取。")
                else:
                    self._play_sound("bump")
                    self._msg("没有找到存档文件。")
                self.scene = SCENE_EXPLORE
            elif self.menu_idx == 6:
                self.running = False
        elif e.key in (pygame.K_ESCAPE, pygame.K_m):
            self._play_sound("cancel")
            self.scene = SCENE_EXPLORE

    def _key_inventory(self, e: pygame.event.Event) -> None:
        inv = self.engine.player.get("items", [])
        if self.gift_item_id:
            targets = self.engine.gift_targets()
            if e.key == pygame.K_ESCAPE:
                self.gift_item_id = None
            elif e.key == pygame.K_UP:
                self.gift_target_idx = max(0, self.gift_target_idx - 1)
            elif e.key == pygame.K_DOWN:
                self.gift_target_idx = min(max(0, len(targets) - 1), self.gift_target_idx + 1)
            elif e.key in (pygame.K_RETURN, pygame.K_SPACE) and targets:
                self.engine.give_gift(
                    self.gift_item_id, targets[self.gift_target_idx]["id"]
                )
                self._msg(self.engine.last_message)
                self.gift_item_id = None
            return
        if e.key == pygame.K_ESCAPE or e.key == pygame.K_i:
            self._play_sound("cancel")
            self.scene = SCENE_EXPLORE
        elif e.key == pygame.K_UP:
            self.select_idx = max(0, self.select_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.select_idx = min(max(0, len(inv) - 1), self.select_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if inv and self.select_idx < len(inv):
                item_id = inv[self.select_idx]
                eq = EQUIPMENT_DATA.get(item_id)
                if eq:
                    self.engine.equip_item(item_id)
                    self._play_sound("equip")
                    self._msg(self.engine.last_message)
                else:
                    rule = self.engine.item_rules.get(item_id, {})
                    use_effect = rule.get("use_effect", "")
                    if use_effect:
                        if use_effect == "gift":
                            self.gift_item_id = item_id
                            self.gift_target_idx = 0
                        else:
                            self.engine.use_item(item_id)
                            self._msg(self.engine.last_message)
                        self._play_sound("item")
                    else:
                        self._msg(f"{self.engine.item_name(item_id)}：{rule.get('description', '无描述')}")
        elif e.key == pygame.K_u:
            # 卸下装备快捷键
            if inv and self.select_idx < len(inv):
                item_id = inv[self.select_idx]
                eq = EQUIPMENT_DATA.get(item_id)
                if eq:
                    self.engine.unequip_item(eq["slot"])
                    self._play_sound("equip")
                    self._msg(self.engine.last_message)

    # ══════════════════════════════════════════════════════════
    # 渲染
    # ══════════════════════════════════════════════════════════

    def _render(self) -> None:
        self.screen.fill(C_BG)
        if self.scene == SCENE_COMBAT and self.combat_ui:
            self.combat_ui.render(self.screen, self.engine, self.font_title, self.font_body)
        elif self.scene == SCENE_ENCOUNTER:
            self._render_encounter()
        elif self.scene == SCENE_SHOP:
            self._render_shop()
        elif self.scene == SCENE_INN:
            self._render_inn()
        elif self.scene == SCENE_MENU:
            self._render_menu()
        elif self.scene == SCENE_INVENTORY:
            self._render_inventory()
        elif self.scene == SCENE_TRAVEL:
            self._render_travel()
        else:
            self._render_explore()
        pygame.display.flip()

    def _render_explore(self) -> None:
        self._render_tilemap()
        self._render_info_panel()
        self._render_messages()
        hint_x = MAP_VIEW_W * TILE_SIZE + 8
        hint_width = PANEL_W - 16
        hint_lines = _wrap_text(
            self.font_small,
            "方向键:移动 空格:交互 I:物品 R:休息 C:修炼 M:菜单 F9:静音 F10/F11:音量",
            hint_width,
        )
        line_height = self.font_small.get_linesize()
        hint_y = WIN_H - 8 - line_height * len(hint_lines)
        for line in hint_lines:
            hint = self.font_small.render(line, True, (120, 120, 130))
            self.screen.blit(hint, (hint_x, hint_y))
            hint_y += line_height

    # ── 瓦片渲染 ────────────────────────────────────────────

    def _map_theme(self) -> str:
        """根据地图信息选择像素场景主题。"""
        md = self.engine.current_map()
        text = f"{md.get('id', '')} {md.get('name', '')} {md.get('region', '')}".lower()
        if md.get("safe_zone", False):
            return _city_identity(str(md.get("id", "")))["theme"]
        if any(key in text for key in ("flame", "fire", "volcano", "炎", "火", "焚", "熔")):
            return "volcanic"
        if any(key in text for key in ("ice", "snow", "frost", "冰", "雪", "寒")):
            return "ice"
        if any(key in text for key in ("poison", "swamp", "毒", "沼", "幽冥")):
            return "poison"
        if any(key in text for key in ("void", "space", "sky", "dragon", "虚空", "天墓", "龙岛", "星")):
            return "void"
        if any(key in text for key in ("sea", "river", "lake", "spring", "海", "河", "湖", "泉")):
            return "water"
        if any(key in text for key in ("battle", "fortress", "front", "战", "要塞", "葬天")):
            return "battlefield"
        if any(key in text for key in ("desert", "plain", "road", "沙", "荒", "平原")):
            return "desert"
        if any(key in text for key in ("cave", "ruins", "tower", "遗迹", "洞", "塔")):
            return "cave"
        if not md.get("safe_zone", False):
            return "forest"
        return "town"

    @staticmethod
    def _pixel_rect(
        surface: pygame.Surface, color: Tuple[int, int, int],
        x: int, y: int, w: int, h: int,
    ) -> None:
        pygame.draw.rect(surface, color, (x, y, w, h))

    def _draw_landmark_tile(
        self, sx: int, sy: int, landmark: str, theme: str,
    ) -> None:
        """绘制城市专属地标，让不同城市在一眼内可辨认。"""
        cx = sx + TILE_SIZE // 2
        if landmark == "wormhole":
            pygame.draw.circle(self.screen, (49, 39, 78), (cx, sy + 17), 14)
            pygame.draw.circle(self.screen, (113, 91, 184), (cx, sy + 17), 12, 3)
            pygame.draw.circle(self.screen, (101, 198, 228), (cx, sy + 17), 7, 2)
            pygame.draw.arc(self.screen, (229, 207, 255), (sx + 5, sy + 6, 22, 22), 0.2, 4.4, 2)
        elif landmark == "great_cauldron":
            pygame.draw.polygon(self.screen, (65, 40, 39), [(sx + 7, sy + 11), (sx + 25, sy + 11), (sx + 22, sy + 25), (sx + 10, sy + 25)])
            pygame.draw.rect(self.screen, (190, 103, 58), (sx + 6, sy + 9, 20, 5))
            pygame.draw.line(self.screen, (238, 166, 74), (sx + 10, sy + 26), (sx + 7, sy + 30), 2)
            pygame.draw.line(self.screen, (238, 166, 74), (sx + 22, sy + 26), (sx + 25, sy + 30), 2)
            pygame.draw.circle(self.screen, (247, 126, 48), (cx, sy + 6), 4)
            pygame.draw.circle(self.screen, (255, 213, 81), (cx + 2, sy + 4), 2)
        elif landmark in ("oasis_well", "medicine_tree"):
            if landmark == "medicine_tree":
                pygame.draw.rect(self.screen, (100, 69, 44), (sx + 14, sy + 15, 5, 15))
                pygame.draw.circle(self.screen, (55, 112, 68), (cx, sy + 13), 11)
                pygame.draw.circle(self.screen, (103, 164, 94), (sx + 11, sy + 10), 6)
                pygame.draw.circle(self.screen, (192, 218, 139), (sx + 21, sy + 12), 3)
            else:
                pygame.draw.ellipse(self.screen, (91, 62, 39), (sx + 3, sy + 11, 26, 17))
                pygame.draw.ellipse(self.screen, (205, 151, 78), (sx + 4, sy + 8, 24, 15), 3)
                pygame.draw.ellipse(self.screen, (77, 154, 166), (sx + 8, sy + 12, 16, 8))
                pygame.draw.line(self.screen, (113, 75, 45), (sx + 8, sy + 9), (sx + 8, sy + 2), 2)
                pygame.draw.line(self.screen, (113, 75, 45), (sx + 24, sy + 9), (sx + 24, sy + 2), 2)
        elif landmark in ("beacon", "mercenary_standard", "salt_crane"):
            if landmark == "beacon":
                pygame.draw.polygon(self.screen, (78, 64, 58), [(sx + 8, sy + 29), (sx + 24, sy + 29), (sx + 21, sy + 8), (sx + 11, sy + 8)])
                pygame.draw.rect(self.screen, (159, 119, 73), (sx + 10, sy + 15, 12, 3))
                pygame.draw.circle(self.screen, (246, 113, 47), (cx, sy + 6), 5)
                pygame.draw.circle(self.screen, (255, 205, 73), (cx + 1, sy + 4), 2)
            elif landmark == "salt_crane":
                pygame.draw.line(self.screen, (111, 77, 52), (sx + 8, sy + 28), (sx + 8, sy + 5), 3)
                pygame.draw.line(self.screen, (111, 77, 52), (sx + 8, sy + 6), (sx + 26, sy + 6), 3)
                pygame.draw.line(self.screen, (181, 154, 110), (sx + 24, sy + 7), (sx + 24, sy + 22), 1)
                pygame.draw.polygon(self.screen, (228, 220, 194), [(sx + 15, sy + 28), (sx + 29, sy + 28), (sx + 23, sy + 18)])
            else:
                pygame.draw.line(self.screen, (91, 65, 47), (sx + 11, sy + 29), (sx + 11, sy + 4), 3)
                pygame.draw.polygon(self.screen, (162, 65, 51), [(sx + 12, sy + 5), (sx + 28, sy + 9), (sx + 12, sy + 16)])
                pygame.draw.line(self.screen, (231, 176, 74), (sx + 15, sy + 9), (sx + 23, sy + 11), 2)
        elif landmark in ("auction_bell", "alchemy_guild", "academy_crest"):
            if landmark == "auction_bell":
                pygame.draw.polygon(self.screen, (156, 91, 52), [(sx + 7, sy + 24), (sx + 25, sy + 24), (sx + 22, sy + 9), (sx + 10, sy + 9)])
                pygame.draw.rect(self.screen, (230, 172, 70), (sx + 6, sy + 23, 20, 4))
                pygame.draw.circle(self.screen, (239, 190, 80), (cx, sy + 28), 3)
            elif landmark == "alchemy_guild":
                pygame.draw.rect(self.screen, (82, 62, 59), (sx + 9, sy + 9, 14, 20))
                pygame.draw.polygon(self.screen, (182, 103, 64), [(sx + 6, sy + 10), (cx, sy + 2), (sx + 26, sy + 10)])
                pygame.draw.circle(self.screen, (95, 202, 171), (cx, sy + 18), 5, 2)
                pygame.draw.line(self.screen, (230, 173, 78), (cx, sy + 13), (cx, sy + 23), 1)
            else:
                pygame.draw.circle(self.screen, (56, 79, 83), (cx, sy + 17), 12)
                pygame.draw.circle(self.screen, (149, 211, 196), (cx, sy + 17), 10, 2)
                pygame.draw.polygon(self.screen, (213, 229, 216), [(cx, sy + 8), (cx + 7, sy + 20), (cx, sy + 17), (cx - 7, sy + 20)])
        else:
            base = (57, 53, 69) if theme in ("dark_town", "void_town") else (93, 79, 65)
            accent = (196, 76, 79) if landmark == "black_obelisk" else (219, 174, 83)
            pygame.draw.rect(self.screen, base, (sx + 8, sy + 8, 16, 21))
            pygame.draw.polygon(self.screen, base, [(sx + 8, sy + 8), (cx, sy + 2), (sx + 24, sy + 8)])
            pygame.draw.rect(self.screen, accent, (sx + 14, sy + 11, 4, 12))
            pygame.draw.rect(self.screen, (46, 43, 46), (sx + 5, sy + 28, 22, 3))

    def _draw_tile(
        self, sx: int, sy: int, tile: int, mx: int, my: int,
        theme: str, identity: Dict[str, str],
    ) -> None:
        """绘制带有材质和边缘层次的程序化像素瓦片。"""
        seed = (mx * 92821 + my * 68917) & 0xFFFF
        r = pygame.Rect(sx, sy, TILE_SIZE, TILE_SIZE)

        if theme == "town":
            floor = (92, 99, 105) if seed % 3 else (98, 105, 109)
            wall = ((76, 64, 70), (112, 83, 70), (151, 108, 78))
        elif theme == "wutan_town":
            floor = (101, 108, 106) if seed % 3 else (110, 116, 112)
            wall = ((68, 70, 71), (104, 91, 78), (171, 131, 84))
        elif theme == "black_rock_town":
            floor = (82, 83, 86) if seed % 3 else (91, 91, 93)
            wall = ((55, 51, 54), (91, 74, 69), (178, 112, 69))
        elif theme == "salt_town":
            floor = (143, 147, 142) if seed % 3 else (154, 157, 150)
            wall = ((81, 83, 82), (130, 117, 99), (223, 211, 176))
        elif theme == "frontier_town":
            floor = (116, 101, 82) if seed % 3 else (126, 109, 88)
            wall = ((67, 61, 57), (113, 83, 62), (177, 126, 76))
        elif theme == "forest_town":
            floor = (91, 112, 90) if seed % 3 else (100, 121, 96)
            wall = ((58, 73, 62), (93, 104, 78), (161, 139, 83))
        elif theme == "sand_town":
            floor = (174, 143, 91) if seed % 3 else (187, 154, 98)
            wall = ((105, 76, 48), (157, 107, 62), (212, 153, 79))
        elif theme == "dark_town":
            floor = (66, 61, 68) if seed % 3 else (73, 66, 72)
            wall = ((47, 39, 47), (82, 56, 61), (145, 79, 65))
        elif theme == "academy_town":
            floor = (81, 101, 105) if seed % 3 else (89, 111, 112)
            wall = ((57, 66, 72), (81, 110, 115), (132, 169, 157))
        elif theme == "dan_town":
            floor = (112, 90, 83) if seed % 3 else (122, 98, 88)
            wall = ((76, 48, 48), (131, 72, 58), (207, 132, 73))
        elif theme == "jade_town":
            floor = (85, 109, 91) if seed % 3 else (93, 120, 99)
            wall = ((52, 73, 62), (81, 116, 91), (142, 177, 124))
        elif theme == "void_town":
            floor = (72, 72, 105) if seed % 3 else (80, 80, 116)
            wall = ((48, 45, 73), (88, 76, 122), (164, 137, 190))
        elif theme == "capital_town":
            floor = (111, 105, 101) if seed % 3 else (121, 115, 109)
            wall = ((76, 62, 58), (130, 92, 71), (202, 155, 91))
        elif theme == "desert":
            floor = (173, 139, 82) if seed % 3 else (184, 149, 89)
            wall = ((102, 78, 53), (139, 105, 66), (179, 139, 78))
        elif theme == "cave":
            floor = (48, 47, 57) if seed % 3 else (55, 52, 62)
            wall = ((37, 35, 47), (62, 58, 72), (92, 82, 91))
        elif theme == "volcanic":
            floor = (72, 42, 39) if seed % 3 else (83, 47, 40)
            wall = ((49, 29, 32), (87, 42, 38), (167, 66, 39))
        elif theme == "ice":
            floor = (127, 170, 180) if seed % 3 else (142, 185, 193)
            wall = ((65, 98, 123), (104, 158, 177), (192, 229, 228))
        elif theme == "poison":
            floor = (55, 75, 53) if seed % 3 else (62, 84, 57)
            wall = ((37, 49, 39), (69, 91, 53), (127, 155, 70))
        elif theme == "void":
            floor = (42, 43, 76) if seed % 3 else (48, 49, 88)
            wall = ((31, 28, 57), (74, 62, 112), (151, 121, 190))
        elif theme == "water":
            floor = (45, 101, 119) if seed % 3 else (51, 113, 130)
            wall = ((38, 67, 79), (74, 121, 128), (133, 172, 164))
        elif theme == "battlefield":
            floor = (92, 79, 67) if seed % 3 else (101, 86, 70)
            wall = ((54, 49, 48), (91, 75, 65), (142, 105, 75))
        else:
            floor = (59, 101, 69) if seed % 3 else (65, 111, 72)
            wall = ((36, 65, 45), (53, 96, 58), (76, 126, 68))

        pygame.draw.rect(self.screen, floor, r)

        if tile == TILE_ROAD:
            inset = pygame.Rect(sx + 1, sy + 1, TILE_SIZE - 2, TILE_SIZE - 2)
            road = tuple(max(0, c - 18) for c in floor)
            pygame.draw.rect(self.screen, road, inset)
            pygame.draw.line(self.screen, tuple(min(255, c + 22) for c in road), (sx + 3, sy + 7), (sx + 28, sy + 7))
            pygame.draw.line(self.screen, tuple(max(0, c - 18) for c in road), (sx + 3, sy + 25), (sx + 28, sy + 25))
            if mx % 2 == my % 2:
                pygame.draw.rect(self.screen, tuple(min(255, c + 14) for c in road), (sx + 14, sy + 10, 4, 12))
        elif tile == TILE_PLAZA:
            plaza = tuple(min(255, c + 9) for c in floor)
            pygame.draw.rect(self.screen, plaza, (sx + 1, sy + 1, 30, 30))
            pygame.draw.rect(self.screen, tuple(max(0, c - 25) for c in plaza), (sx + 3, sy + 3, 26, 26), 1)
            pygame.draw.line(self.screen, tuple(min(255, c + 35) for c in plaza), (sx + 5, sy + 16), (sx + 27, sy + 16))
            pygame.draw.line(self.screen, tuple(min(255, c + 35) for c in plaza), (sx + 16, sy + 5), (sx + 16, sy + 27))
        elif tile == TILE_WATER:
            water = (72, 139, 156) if theme != "void_town" else (92, 76, 147)
            pygame.draw.rect(self.screen, tuple(max(0, c - 35) for c in water), r)
            pygame.draw.rect(self.screen, water, (sx + 2, sy + 3, 28, 27))
            pygame.draw.arc(self.screen, tuple(min(255, c + 58) for c in water), (sx + 3, sy + 7, 20, 8), 0, math.pi, 1)
            pygame.draw.arc(self.screen, tuple(min(255, c + 32) for c in water), (sx + 10, sy + 19, 20, 7), 0, math.pi, 1)
        elif tile == TILE_GARDEN:
            pygame.draw.rect(self.screen, tuple(max(0, c - 16) for c in floor), r)
            if theme == "dan_town":
                pygame.draw.circle(self.screen, (72, 121, 68), (sx + 11, sy + 20), 7)
                pygame.draw.circle(self.screen, (102, 154, 79), (sx + 21, sy + 17), 8)
                pygame.draw.circle(self.screen, (225, 162, 81), (sx + 19, sy + 13), 2)
                pygame.draw.circle(self.screen, (203, 103, 96), (sx + 9, sy + 18), 2)
            elif theme == "void_town":
                pygame.draw.polygon(self.screen, (124, 101, 181), [(sx + 7, sy + 28), (sx + 12, sy + 8), (sx + 17, sy + 28)])
                pygame.draw.polygon(self.screen, (97, 172, 202), [(sx + 16, sy + 28), (sx + 22, sy + 13), (sx + 27, sy + 28)])
                pygame.draw.line(self.screen, (218, 205, 247), (sx + 12, sy + 10), (sx + 11, sy + 24), 1)
            else:
                pygame.draw.rect(self.screen, (78, 58, 40), (sx + 14, sy + 18, 4, 12))
                pygame.draw.circle(self.screen, (55, 103, 64), (sx + 16, sy + 14), 10)
                pygame.draw.circle(self.screen, (91, 143, 78), (sx + 10, sy + 12), 6)
                pygame.draw.circle(self.screen, (110, 158, 83), (sx + 22, sy + 13), 6)
        elif tile == TILE_LANDMARK:
            pygame.draw.rect(self.screen, tuple(max(0, c - 12) for c in floor), r)
            self._draw_landmark_tile(sx, sy, identity["landmark"], theme)
        elif tile == TILE_FLOOR:
            if theme == "town" or theme.endswith("_town"):
                pygame.draw.line(self.screen, (70, 77, 82), (sx, sy + 15), (sx + 31, sy + 15))
                offset = 7 if my % 2 else 16
                pygame.draw.line(self.screen, (75, 82, 87), (sx + offset, sy), (sx + offset, sy + 15))
                pygame.draw.line(self.screen, (75, 82, 87), (sx + 31 - offset, sy + 16), (sx + 31 - offset, sy + 31))
                pygame.draw.line(self.screen, (126, 132, 132), (sx + 2, sy + 2), (sx + 28, sy + 2))
            elif theme == "desert":
                pygame.draw.line(self.screen, (151, 117, 68), (sx + 3, sy + 10), (sx + 14, sy + 8))
                pygame.draw.line(self.screen, (198, 165, 100), (sx + 17, sy + 24), (sx + 29, sy + 22))
                if seed % 5 == 0:
                    self._pixel_rect(self.screen, (112, 104, 58), sx + 8, sy + 18, 2, 3)
            elif theme == "cave":
                pygame.draw.line(self.screen, (38, 36, 46), (sx + 3, sy + 24), (sx + 12, sy + 17))
                pygame.draw.line(self.screen, (75, 68, 78), (sx + 12, sy + 17), (sx + 20, sy + 20))
                self._pixel_rect(self.screen, (92, 112, 112), sx + 25, sy + 7, 2, 2)
            elif theme == "volcanic":
                pygame.draw.line(self.screen, (194, 66, 32), (sx + 2, sy + 25), (sx + 12, sy + 18), 2)
                pygame.draw.line(self.screen, (244, 135, 43), (sx + 12, sy + 18), (sx + 20, sy + 21))
                self._pixel_rect(self.screen, (255, 190, 57), sx + 25, sy + 7, 2, 2)
            elif theme == "ice":
                pygame.draw.line(self.screen, (211, 240, 239), (sx + 3, sy + 25), (sx + 15, sy + 7))
                pygame.draw.line(self.screen, (91, 143, 169), (sx + 15, sy + 7), (sx + 26, sy + 19))
            elif theme == "poison":
                pygame.draw.circle(self.screen, (116, 145, 61), (sx + 8, sy + 22), 3)
                pygame.draw.circle(self.screen, (88, 111, 57), (sx + 25, sy + 8), 2)
            elif theme == "void":
                self._pixel_rect(self.screen, (192, 177, 229), sx + 8, sy + 8, 2, 2)
                self._pixel_rect(self.screen, (115, 186, 220), sx + 25, sy + 21, 2, 2)
                pygame.draw.line(self.screen, (81, 71, 123), (sx + 4, sy + 25), (sx + 18, sy + 11))
            elif theme == "water":
                pygame.draw.arc(self.screen, (103, 173, 186), (sx + 3, sy + 5, 20, 12), 0, math.pi, 1)
                pygame.draw.arc(self.screen, (80, 151, 169), (sx + 10, sy + 18, 20, 10), 0, math.pi, 1)
            elif theme == "battlefield":
                pygame.draw.line(self.screen, (69, 57, 51), (sx + 4, sy + 25), (sx + 15, sy + 12), 2)
                pygame.draw.rect(self.screen, (125, 91, 58), (sx + 23, sy + 6, 3, 8))
            else:
                if seed % 2:
                    pygame.draw.line(self.screen, (84, 132, 72), (sx + 8, sy + 24), (sx + 10, sy + 18))
                    pygame.draw.line(self.screen, (84, 132, 72), (sx + 10, sy + 24), (sx + 14, sy + 20))
                self._pixel_rect(self.screen, (44, 84, 55), sx + 25, sy + 8, 2, 2)
        elif tile == TILE_WALL:
            pygame.draw.rect(self.screen, wall[0], r)
            if theme == "forest":
                pygame.draw.ellipse(self.screen, wall[0], (sx + 3, sy + 20, 26, 10))
                pygame.draw.rect(self.screen, (91, 67, 45), (sx + 13, sy + 18, 6, 13))
                pygame.draw.circle(self.screen, wall[1], (sx + 16, sy + 14), 12)
                pygame.draw.circle(self.screen, wall[2], (sx + 10, sy + 12), 7)
                pygame.draw.circle(self.screen, (91, 145, 74), (sx + 21, sy + 10), 7)
            elif theme == "town" or theme.endswith("_town"):
                pygame.draw.rect(self.screen, wall[1], (sx + 1, sy + 6, 30, 25))
                pygame.draw.rect(self.screen, wall[2], (sx + 1, sy + 5, 30, 5))
                for by in (12, 21):
                    pygame.draw.line(self.screen, wall[0], (sx + 2, sy + by), (sx + 30, sy + by))
                pygame.draw.line(self.screen, wall[0], (sx + 10, sy + 12), (sx + 10, sy + 21))
                pygame.draw.line(self.screen, wall[0], (sx + 22, sy + 12), (sx + 22, sy + 21))
                pygame.draw.line(self.screen, wall[0], (sx + 16, sy + 21), (sx + 16, sy + 30))
                pygame.draw.line(self.screen, (194, 139, 91), (sx + 3, sy + 7), (sx + 28, sy + 7))
                roof_accent = {
                    "wutan_town": (194, 151, 83), "black_rock_town": (212, 121, 70),
                    "salt_town": (235, 224, 192), "frontier_town": (204, 142, 78),
                    "forest_town": (151, 174, 105), "sand_town": (232, 177, 91),
                    "dark_town": (188, 87, 72), "academy_town": (151, 211, 196),
                    "dan_town": (235, 151, 75), "jade_town": (169, 201, 139),
                    "void_town": (189, 154, 222), "capital_town": (230, 180, 99),
                }.get(theme, (194, 139, 91))
                pygame.draw.line(self.screen, roof_accent, (sx + 2, sy + 5), (sx + 29, sy + 5), 2)
            else:
                pygame.draw.polygon(
                    self.screen, wall[1],
                    [(sx + 2, sy + 27), (sx + 5, sy + 10), (sx + 13, sy + 3),
                     (sx + 25, sy + 7), (sx + 30, sy + 27)],
                )
                pygame.draw.line(self.screen, wall[2], (sx + 6, sy + 11), (sx + 14, sy + 5), 2)
                pygame.draw.line(self.screen, wall[0], (sx + 17, sy + 8), (sx + 22, sy + 24), 2)
        elif tile == TILE_COUNTER:
            counter = {
                "salt_town": ((111, 89, 62), (228, 218, 188)),
                "dan_town": ((91, 48, 43), (215, 126, 65)),
                "dark_town": ((55, 42, 44), (151, 75, 61)),
                "sand_town": ((105, 69, 39), (211, 151, 73)),
                "academy_town": ((50, 80, 80), (126, 181, 159)),
            }.get(theme, ((74, 48, 33), (157, 103, 54)))
            pygame.draw.rect(self.screen, counter[0], (sx + 1, sy + 8, 30, 22))
            pygame.draw.rect(self.screen, counter[1], (sx, sy + 7, 32, 7))
            pygame.draw.line(self.screen, tuple(min(255, c + 45) for c in counter[1]), (sx + 2, sy + 8), (sx + 29, sy + 8), 2)
            pygame.draw.rect(self.screen, tuple(max(0, c - 18) for c in counter[0]), (sx + 5, sy + 17, 22, 10), 2)
        elif tile == TILE_DOOR:
            pygame.draw.rect(self.screen, (91, 54, 34), (sx + 5, sy + 2, 22, 30))
            pygame.draw.rect(self.screen, (174, 112, 57), (sx + 7, sy + 4, 18, 28), 2)
            pygame.draw.circle(self.screen, (224, 185, 87), (sx + 21, sy + 18), 2)

        pygame.draw.line(self.screen, (25, 28, 31), (sx, sy + 31), (sx + 31, sy + 31))
        pygame.draw.line(self.screen, (25, 28, 31), (sx + 31, sy), (sx + 31, sy + 31))

    def _render_tilemap(self) -> None:
        px, py = self.player_pos
        h, w = self.map_h, self.map_w
        vw, vh = MAP_VIEW_W, MAP_VIEW_H
        if w == 0 or h == 0:
            return
        theme = self._map_theme()
        md = self.engine.current_map()
        identity = _city_identity(str(md.get("id", "")))

        ox = max(0, min(px - vw // 2, w - vw))
        oy = max(0, min(py - vh // 2, h - vh))
        if w <= vw:
            ox = -(vw - w) // 2
        if h <= vh:
            oy = -(vh - h) // 2

        for gy in range(vh):
            for gx in range(vw):
                mx, my = gx + ox, gy + oy
                sx, sy = gx * TILE_SIZE, gy * TILE_SIZE
                if 0 <= mx < w and 0 <= my < h:
                    tile = self.tile_grid[my][mx]
                    self._draw_tile(sx, sy, tile, mx, my, theme, identity)
                else:
                    pygame.draw.rect(self.screen, (10, 10, 18), (sx, sy, TILE_SIZE, TILE_SIZE))

        if md.get("safe_zone", False):
            self._render_city_signature(identity, str(md.get("name", identity["name"])))

        # 实体和名称统一在瓦片之后绘制，避免名称被相邻瓦片覆盖。
        for gy in range(vh):
            for gx in range(vw):
                mx, my = gx + ox, gy + oy
                if not (0 <= mx < w and 0 <= my < h):
                    continue
                ent = self.tile_entities.get((mx, my))
                if ent is not None:
                    self._draw_entity_icon(
                        gx * TILE_SIZE,
                        gy * TILE_SIZE,
                        ent,
                        self.entity_labels.get((mx, my), ""),
                    )

        # 玩家
        psx = (px - ox) * TILE_SIZE
        psy = (py - oy) * TILE_SIZE
        self._draw_player_icon(psx, psy)

    def _render_city_signature(self, identity: Dict[str, str], map_name: str) -> None:
        """在城市画面角落展示简洁的地点印章与城市气质。"""
        title = map_name if len(map_name) <= 8 else identity["name"]
        subtitle = identity["motto"]
        title_surface = self.font_body.render(title, True, (247, 232, 198))
        subtitle_surface = self.font_small.render(subtitle, True, (208, 185, 142))
        width = max(title_surface.get_width(), subtitle_surface.get_width()) + 20
        plaque = pygame.Surface((width, 48), pygame.SRCALPHA)
        plaque.fill((16, 18, 22, 198))
        pygame.draw.rect(plaque, (218, 178, 96, 210), (0, 0, width, 48), 1)
        pygame.draw.rect(plaque, (218, 178, 96, 150), (5, 5, 3, 38))
        plaque.blit(title_surface, (12, 5))
        plaque.blit(subtitle_surface, (12, 27))
        self.screen.blit(plaque, (8, 8))

    def _draw_entity_icon(self, sx: int, sy: int, etype: int, label: str) -> None:
        cx, cy = sx + TILE_SIZE // 2, sy + TILE_SIZE // 2
        pygame.draw.ellipse(self.screen, (25, 28, 31), (sx + 6, sy + 25, 20, 5))

        if etype == ENTITY_NPC:
            self._draw_npc_icon(sx, sy, label)
        elif etype == ENTITY_ENEMY:
            robe = (153, 52, 48)
            trim = (239, 131, 69)
            skin = (226, 180, 139)
            pygame.draw.rect(self.screen, robe, (cx - 7, sy + 15, 14, 12))
            pygame.draw.polygon(self.screen, robe, [(cx - 9, sy + 28), (cx + 9, sy + 28), (cx + 6, sy + 19), (cx - 6, sy + 19)])
            pygame.draw.line(self.screen, trim, (cx, sy + 17), (cx, sy + 27), 2)
            pygame.draw.rect(self.screen, skin, (cx - 5, sy + 7, 10, 9))
            hair = (73, 29, 29)
            pygame.draw.rect(self.screen, hair, (cx - 6, sy + 5, 12, 5))
            pygame.draw.rect(self.screen, hair, (cx - 7, sy + 8, 3, 8))
            pygame.draw.rect(self.screen, (30, 29, 35), (cx - 3, sy + 11, 2, 2))
            pygame.draw.rect(self.screen, (30, 29, 35), (cx + 2, sy + 11, 2, 2))
            pygame.draw.line(self.screen, (243, 102, 58), (sx + 4, sy + 22), (sx + 10, sy + 12), 2)
        elif etype in (ENTITY_SHOP, ENTITY_INN, ENTITY_GUILD):
            roof = {
                ENTITY_SHOP: (181, 77, 48), ENTITY_INN: (48, 120, 128),
                ENTITY_GUILD: (100, 73, 145),
            }[etype]
            pygame.draw.rect(self.screen, (120, 83, 54), (sx + 6, sy + 14, 20, 15))
            pygame.draw.polygon(self.screen, roof, [(sx + 3, sy + 14), (cx, sy + 4), (sx + 29, sy + 14)])
            pygame.draw.line(self.screen, (226, 176, 89), (sx + 4, sy + 14), (sx + 28, sy + 14), 2)
            pygame.draw.rect(self.screen, (56, 39, 35), (cx - 3, sy + 20, 6, 9))
            pygame.draw.rect(self.screen, (236, 199, 103), (sx + 8, sy + 17, 4, 4))
            pygame.draw.rect(self.screen, (236, 199, 103), (sx + 20, sy + 17, 4, 4))
        elif etype == ENTITY_TREASURE:
            pygame.draw.rect(self.screen, (111, 58, 31), (sx + 6, sy + 15, 20, 13))
            pygame.draw.rect(self.screen, (178, 99, 41), (sx + 6, sy + 11, 20, 8))
            pygame.draw.rect(self.screen, (246, 191, 62), (cx - 2, sy + 17, 4, 7))
            pygame.draw.line(self.screen, (255, 222, 111), (sx + 8, sy + 12), (sx + 23, sy + 12), 2)
        elif etype == ENTITY_GATHER:
            self._draw_gather_icon(sx, sy, cx, cy, label)
        elif etype == ENTITY_EXIT:
            pulse = 2 + int((math.sin(pygame.time.get_ticks() / 260) + 1) * 2)
            pygame.draw.circle(self.screen, (38, 88, 86), (cx, cy), 11 + pulse, 2)
            pygame.draw.circle(self.screen, (91, 220, 176), (cx, cy), 9, 2)
            pygame.draw.line(self.screen, (208, 255, 225), (cx, sy + 9), (cx, sy + 23), 2)
            pygame.draw.polygon(self.screen, (208, 255, 225), [(cx, sy + 7), (cx - 4, sy + 13), (cx + 4, sy + 13)])

        if label:
            if label.startswith("npc_"):
                short_label = self.engine.npc_names.get(label, label)
            else:
                short_label = label if len(label) <= 4 else label[:4]
            if len(short_label) > 4:
                short_label = short_label[:4]
            lb = self.font_small.render(short_label, True, (238, 228, 203))
            bg = pygame.Surface((lb.get_width() + 4, lb.get_height()), pygame.SRCALPHA)
            bg.fill((18, 20, 24, 185))
            map_pixel_width = MAP_VIEW_W * TILE_SIZE
            lx = max(2, min(cx - lb.get_width() // 2, map_pixel_width - lb.get_width() - 2))
            ly = sy + TILE_SIZE - lb.get_height()
            self.screen.blit(bg, (lx - 2, ly))
            self.screen.blit(lb, (lx, ly))


    def _draw_gather_icon(self, sx: int, sy: int, cx: int, cy: int, label: str) -> None:
        """Pixel art for gathering nodes: herb/ore/beast/spirit/core/crystal."""
        tick = pygame.time.get_ticks()
        glow = abs(int((tick / 400 % 2.0 - 1) * 60))
        if "\u836f\u6750" in label or "herb" in label.lower():
            pygame.draw.line(self.screen, (60, 160, 40), (cx, sy + 26), (cx, sy + 14), 3)
            pygame.draw.ellipse(self.screen, (40, 200, 50), (cx - 2, sy + 6, 10, 10))
            pygame.draw.ellipse(self.screen, (20, 180, 30), (cx - 10, sy + 12, 8, 6))
            pygame.draw.ellipse(self.screen, (100 + glow, 255, 100 + glow), (cx - 3, sy + 4, 4, 4))
            pygame.draw.circle(self.screen, (200, 255, 120, 180), (cx, sy + 8), 2, 1)
        elif "\u77ff\u77f3" in label or "ore" in label.lower():
            dark, mid = (80, 70, 60), (140, 120, 90)
            light = (200 + glow, 180 + glow, 140 + glow)
            pygame.draw.polygon(self.screen, dark, [(cx-6, sy+24), (cx+2, sy+26), (cx+4, sy+18), (cx-4, sy+12)])
            pygame.draw.polygon(self.screen, mid, [(cx-4, sy+12), (cx+4, sy+18), (cx+8, sy+8), (cx-2, sy+6)])
            pygame.draw.polygon(self.screen, light, [(cx-2, sy+6), (cx+8, sy+8), (cx+4, sy+2)])
            pygame.draw.circle(self.screen, (255, 240, 180, 150), (cx + 3, sy + 4), 2)
        elif "\u517d\u6750" in label or "beast" in label.lower():
            bone = (230, 220, 190)
            pygame.draw.line(self.screen, bone, (cx - 3, sy + 26), (cx + 4, sy + 10), 4)
            pygame.draw.circle(self.screen, (240, 235, 210), (cx - 4, sy + 24), 3, 2)
            pygame.draw.circle(self.screen, (240, 235, 210), (cx + 5, sy + 10), 3, 2)
            pygame.draw.line(self.screen, (200, 190, 160), (cx - 6, sy + 20), (cx - 2, sy + 26), 3)
        elif "\u7075\u8349" in label or "spirit" in label.lower():
            pygame.draw.rect(self.screen, (80, 40, 140), (cx - 1, sy + 12, 3, 14))
            for off in [(3, 4), (-8, 10), (5, 16)]:
                pulsing = (120 + glow, 80 + glow, 220 + glow)
                pygame.draw.ellipse(self.screen, pulsing, (cx + off[0] - 5, sy + off[1] - 4, 10, 8))
            pygame.draw.ellipse(self.screen, (200, 160, 255), (cx - 2, sy + 5, 6, 6))
        elif "\u9b54\u6838" in label or "core" in label.lower():
            pygame.draw.circle(self.screen, (60, 20, 80), (cx, sy + 15), 8)
            pygame.draw.circle(self.screen, (140 + glow, 40 + glow, 200 + glow), (cx, sy + 15), 5)
            pygame.draw.circle(self.screen, (220, 180, 255, 100), (cx - 1, sy + 13), 2)
            pygame.draw.circle(self.screen, (255, 255, 255, 80), (cx + 2, sy + 14), 1)
        elif "\u6676\u77f3" in label or "crystal" in label.lower():
            for i, (dx, dy, s) in enumerate([(-4, 22, 6), (3, 14, 5), (-2, 8, 4), (5, 20, 3)]):
                hue = (100 + i * 30, 200 + glow, 240 + i * 5)
                pygame.draw.polygon(self.screen, hue, [(cx+dx-s, sy+dy), (cx+dx+s, sy+dy), (cx+dx, sy+dy-s*2)])
            pygame.draw.circle(self.screen, (200, 255, 255, 150), (cx, sy + 12), 2)
        else:
            pygame.draw.rect(self.screen, (100, 160, 80), (sx + 8, sy + 14, 16, 12))
            pygame.draw.ellipse(self.screen, (140, 220, 100), (sx + 6, sy + 6, 20, 12))
            pygame.draw.circle(self.screen, (200, 255, 160, 120), (cx, sy + 10), 3, 1)

    def _draw_npc_icon(self, sx: int, sy: int, npc_id: str) -> None:
        """绘制由人物表身份与原文档案共同决定的 NPC 像素造型。"""
        cx = sx + TILE_SIZE // 2
        profile = self.engine.npc_profiles.get(npc_id, {})
        visual = _npc_visual(npc_id, profile)
        robe = visual["robe"]
        trim = visual["trim"]
        hair = visual["hair"]
        hair_style = visual["hair_style"]
        accessory = visual["accessory"]
        skin = (230, 185, 143)

        pygame.draw.polygon(
            self.screen, robe,
            [(cx - 8, sy + 28), (cx + 8, sy + 28), (cx + 6, sy + 17), (cx - 6, sy + 17)],
        )
        pygame.draw.rect(self.screen, robe, (cx - 7, sy + 15, 14, 8))
        pygame.draw.line(self.screen, trim, (cx, sy + 17), (cx, sy + 27), 2)
        emblem_seed = _town_seed(npc_id)
        emblem = (
            150 + emblem_seed % 90,
            140 + (emblem_seed >> 7) % 100,
            130 + (emblem_seed >> 14) % 110,
        )
        pygame.draw.rect(self.screen, emblem, (cx - 5 + emblem_seed % 8, sy + 20, 2, 2))
        pygame.draw.rect(self.screen, skin, (cx - 5, sy + 7, 10, 9))

        pygame.draw.rect(self.screen, hair, (cx - 6, sy + 4, 12, 5))
        if hair_style in ("long", "elder"):
            pygame.draw.rect(self.screen, hair, (cx - 7, sy + 7, 3, 12))
            pygame.draw.rect(self.screen, hair, (cx + 4, sy + 7, 3, 12))
        elif hair_style == "twin":
            pygame.draw.rect(self.screen, hair, (cx - 9, sy + 7, 4, 7))
            pygame.draw.rect(self.screen, hair, (cx + 5, sy + 7, 4, 7))
        else:
            pygame.draw.rect(self.screen, hair, (cx - 7, sy + 7, 3, 6))

        eye = (37, 34, 38)
        if accessory == "snake_eye":
            eye = (71, 210, 139)
        pygame.draw.rect(self.screen, eye, (cx - 3, sy + 11, 2, 2))
        pygame.draw.rect(self.screen, eye, (cx + 2, sy + 11, 2, 2))

        if accessory in ("sword", "staff"):
            color = (205, 213, 219) if accessory == "sword" else (139, 100, 62)
            pygame.draw.line(self.screen, color, (cx + 7, sy + 27), (cx + 11, sy + 7), 2)
        elif accessory == "crown":
            pygame.draw.polygon(self.screen, trim, [(cx - 5, sy + 5), (cx - 2, sy + 1), (cx, sy + 5), (cx + 3, sy + 1), (cx + 5, sy + 5)])
        elif accessory in ("gold_flame", "blue_flame", "ice", "red_aura"):
            color = {
                "gold_flame": (246, 205, 66),
                "blue_flame": (74, 205, 231),
                "ice": (183, 235, 245),
                "red_aura": (213, 65, 74),
            }[accessory]
            pygame.draw.circle(self.screen, color, (cx + 10, sy + 12), 3, 1)
            pygame.draw.line(self.screen, color, (cx + 10, sy + 15), (cx + 12, sy + 7), 1)
        elif accessory == "medicine":
            pygame.draw.rect(self.screen, (222, 234, 218), (cx + 7, sy + 20, 5, 7))
            pygame.draw.rect(self.screen, trim, (cx + 8, sy + 18, 3, 2))
        elif accessory == "jewel":
            pygame.draw.circle(self.screen, trim, (cx, sy + 18), 2)
        elif accessory == "dragon":
            pygame.draw.polygon(self.screen, trim, [(cx - 7, sy + 6), (cx - 10, sy + 2), (cx - 4, sy + 5)])
            pygame.draw.polygon(self.screen, trim, [(cx + 7, sy + 6), (cx + 10, sy + 2), (cx + 4, sy + 5)])
        elif accessory == "brows":
            pygame.draw.line(self.screen, hair, (cx - 4, sy + 10), (cx - 1, sy + 9), 1)
            pygame.draw.line(self.screen, hair, (cx + 1, sy + 9), (cx + 4, sy + 10), 1)

    def _draw_player_icon(self, sx: int, sy: int) -> None:
        cx, cy = sx + TILE_SIZE // 2, sy + TILE_SIZE // 2
        aura = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(aura, (72, 214, 162, 42), (16, 17), 13)
        pygame.draw.circle(aura, (116, 239, 185, 80), (16, 17), 11, 2)
        self.screen.blit(aura, (sx, sy))
        pygame.draw.ellipse(self.screen, (26, 33, 32), (sx + 6, sy + 26, 20, 5))
        pygame.draw.polygon(self.screen, (28, 75, 82), [(cx - 8, sy + 28), (cx + 8, sy + 28), (cx + 6, sy + 17), (cx - 6, sy + 17)])
        pygame.draw.rect(self.screen, (39, 114, 113), (cx - 7, sy + 15, 14, 8))
        pygame.draw.line(self.screen, (103, 226, 174), (cx, sy + 17), (cx, sy + 27), 2)
        pygame.draw.rect(self.screen, (231, 184, 139), (cx - 5, sy + 7, 10, 9))
        pygame.draw.rect(self.screen, (29, 27, 35), (cx - 6, sy + 5, 12, 5))
        pygame.draw.rect(self.screen, (29, 27, 35), (cx - 7, sy + 8, 3, 8))
        pygame.draw.rect(self.screen, (29, 27, 35), (cx + 4, sy + 8, 3, 8))
        pygame.draw.rect(self.screen, (41, 38, 40), (cx - 3, sy + 11, 2, 2))
        pygame.draw.rect(self.screen, (41, 38, 40), (cx + 2, sy + 11, 2, 2))
        pygame.draw.line(self.screen, (211, 155, 62), (cx + 7, sy + 23), (cx + 11, sy + 10), 2)

    # ── 信息面板 ────────────────────────────────────────────

    def _render_info_panel(self) -> None:
        px = MAP_VIEW_W * TILE_SIZE
        pygame.draw.rect(self.screen, C_PANEL, (px, 0, PANEL_W, WIN_H))
        p = self.engine.player
        x, y = px + 12, 14
        bw = PANEL_W - 24

        # 标题
        t = self.font_title.render("萧 炎", True, C_ACCENT)
        self.screen.blit(t, (x, y))
        y += 30

        # 境界等级
        realm = self.engine.realm_name()
        rt = self.font_body.render(f"{realm}  Lv.{p['level']}", True, C_TEXT)
        self.screen.blit(rt, (x, y))
        y += 8

        # 修炼进度
        prog = float(p.get("progress", 0))
        pygame.draw.rect(self.screen, (40, 40, 55), (x, y + 12, bw, 6))
        pygame.draw.rect(self.screen, C_ACCENT, (x, y + 12, int(bw * prog / 100), 6))
        pt = self.font_small.render(f"修炼进度 {prog:.1f}%", True, (180, 160, 100))
        self.screen.blit(pt, (x, y + 20))
        y += 34

        # HP
        ht = self.font_body.render(f"生命 {p['hp']}/{p['max_hp']}", True, C_TEXT)
        self.screen.blit(ht, (x, y))
        y += ht.get_height() + 3
        hr = max(0, min(1, p["hp"] / max(1, p["max_hp"])))
        pygame.draw.rect(self.screen, C_HP_BG, (x, y, bw, 5))
        pygame.draw.rect(self.screen, C_HP_BAR, (x, y, int(bw * hr), 5))
        y += 10

        # 灵力
        qt = self.font_body.render(f"灵力 {p.get('douqi', 0)}", True, C_TEXT)
        self.screen.blit(qt, (x, y))
        y += qt.get_height() + 3
        q_max = max(1, int(p.get("douqi", 0)) + 50)
        qr = max(0, min(1, int(p.get("douqi", 0)) / q_max))
        pygame.draw.rect(self.screen, C_QI_BG, (x, y, bw, 5))
        pygame.draw.rect(self.screen, C_QI_BAR, (x, y, int(bw * qr), 5))
        y += 12

        # 属性（含装备加成）
        for name, key in [
            ("攻击", "atk"), ("防御", "def"), ("速度", "spd"),
            ("灵魂", "soul"), ("声望", "reputation"),
        ]:
            val = p.get(key, 0)
            bonus = self.engine.get_equipped_bonus(key)
            if bonus:
                ln = self.font_small.render(f"{name}: {val}(+{bonus})", True, C_ACCENT)
            else:
                ln = self.font_small.render(f"{name}: {val}", True, C_TEXT)
            self.screen.blit(ln, (x, y))
            y += 16
        # 钱包
        wallet = p.get("wallet", {})
        wtext = wallet_display(wallet)
        ln = self.font_small.render(f"资金: {wtext}", True, C_ACCENT)
        self.screen.blit(ln, (x, y)); y += 16
        # 阅历
        ln = self.font_small.render(f"阅历: {p.get('adventure_points', 0)}", True, C_TEXT)
        self.screen.blit(ln, (x, y)); y += 16

        y += 6
        md = self.engine.current_map()
        location_label = self.font_small.render("地点：", True, C_ACCENT)
        self.screen.blit(location_label, (x, y))
        location_x = x + location_label.get_width()
        location_width = max(1, bw - location_label.get_width())
        location_lines = _wrap_text(
            self.font_small, str(md.get("name", "未知")), location_width
        )
        for index, line in enumerate(location_lines):
            line_x = location_x if index == 0 else x
            mn = self.font_small.render(line, True, C_ACCENT)
            self.screen.blit(mn, (line_x, y))
            y += 16
        y += 2
        tt = self.font_small.render(self.engine.time_text(), True, (140, 140, 150))
        self.screen.blit(tt, (x, y))

        if int(p["story_stage"]) < len(STORY_PHASES):
            ph = STORY_PHASES[int(p["story_stage"])]
            y += 20
            st = self.font_small.render(f"📖 {ph['title']}", True, (180, 140, 200))
            self.screen.blit(st, (x, y))

    def _render_messages(self) -> None:
        my = WIN_H - 120
        mx = MAP_VIEW_W * TILE_SIZE + 8
        for msg in reversed(self.messages[-6:]):
            if len(msg) > 32:
                msg = msg[:30] + "…"
            t = self.font_small.render(msg, True, (170, 170, 180))
            self.screen.blit(t, (mx, my))
            my -= 16

    # ── 剧情奇遇界面 ───────────────────────────────────────

    def _render_encounter(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        t = self.font_title.render("⚡ 奇 遇", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 30))
        # 遭遇文本
        lines = _wrap_text(self.font_body, self.encounter_text, w - 80)
        for i, line in enumerate(lines):
            tl = self.font_body.render(line, True, C_TEXT)
            self.screen.blit(tl, (40, 80 + i * 24))
        # 选项
        oy = 80 + len(lines) * 24 + 20
        self.screen.blit(
            self.font_small.render("[↑↓]选择  [空格]确认  [Esc]离开", True, (120, 120, 130)),
            (40, oy)
        )
        oy += 30
        for i, (num, opt) in enumerate(self.encounter_options_data):
            icon = "▶ " if i == self.encounter_idx else "  "
            color = C_ACCENT if i == self.encounter_idx else C_TEXT
            ot = self.font_body.render(f"{icon}{opt['text']}", True, color)
            self.screen.blit(ot, (60, oy + i * 28))

    # ── 地图切换界面 ───────────────────────────────────────

    def _render_travel(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        t = self.font_title.render("前 往 何 处", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 40))
        t2 = self.font_small.render("[↑↓]选择  [空格]确认  [Esc]取消", True, (120, 120, 130))
        self.screen.blit(t2, (w // 2 - t2.get_width() // 2, 74))

        for i, (mid, name, route) in enumerate(self.travel_options):
            icon = "▶ " if i == self.travel_idx else "  "
            color = C_ACCENT if i == self.travel_idx else C_TEXT
            line = f"{icon}{name}  {route}"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (w // 4, 110 + i * 32))

    # ── 商店界面 ────────────────────────────────────────────

    def _render_shop(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        # 标题
        mode = "出售" if self.shop_sell_mode else "购买"
        title = self.font_title.render(f"坊市 — {mode}", True, C_ACCENT)
        self.screen.blit(title, (w // 2 - title.get_width() // 2, 20))
        silver = self.font_body.render(
            f"资金: {wallet_display(self.engine.player.get('wallet',{}))}  [Tab]切换买卖  [Esc]离开",
            True, C_TEXT
        )
        self.screen.blit(silver, (w // 2 - silver.get_width() // 2, 56))

        if self.shop_sell_mode:
            items = self.engine.player.get("items", [])
        else:
            items = self.shop_items

        list_y = 90
        for i, item_id in enumerate(items):
            rule = self.engine.item_rules.get(item_id, {})
            name = self.engine.item_name(item_id)
            itype = rule.get("type", "")
            buy_p, sell_p = item_price(itype)
            icon = "▶ " if i == self.select_idx else "  "
            color = C_ACCENT if i == self.select_idx else C_TEXT
            if self.shop_sell_mode:
                line = f"{icon}{name} [{itype}]  出售: {sell_p}银两"
            else:
                line = f"{icon}{name} [{itype}]  {buy_p}银两"
            t = self.font_body.render(line, True, color)
            draw_item_icon(
                self.screen, item_id, rule, 74, list_y + i * 28 - 2, 24,
                i == self.select_idx,
            )
            self.screen.blit(t, (104, list_y + i * 28))
            if i >= 14:
                break

    # ── 客栈界面 ────────────────────────────────────────────

    def _render_inn(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        t = self.font_title.render("客栈", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, h // 3))
        t2 = self.font_body.render("按 空格 休息（恢复生命体力）  Esc 离开", True, C_TEXT)
        self.screen.blit(t2, (w // 2 - t2.get_width() // 2, h // 3 + 50))
        p = self.engine.player
        t3 = self.font_small.render(
            f"当前: 生命 {p['hp']}/{p['max_hp']}"
            f"  资金: {wallet_display(p.get('wallet', {}))}",
            True, (150, 150, 160)
        )
        self.screen.blit(t3, (w // 2 - t3.get_width() // 2, h // 3 + 80))

    # ── 菜单界面 ────────────────────────────────────────────


    # ── 炼药界面 ─────────────────────────────────────────────

    def _key_alchemy(self, e: pygame.event.Event) -> None:
        recipes = self.engine.available_recipes()
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.alchemy_idx = max(0, self.alchemy_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.alchemy_idx = min(max(0, len(recipes) - 1), self.alchemy_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if recipes and self.alchemy_idx < len(recipes):
                rid = recipes[self.alchemy_idx]["id"]
                self.engine.craft_pill(rid)
                self._play_sound("confirm")
        elif e.key == pygame.K_r:
            inv = self.engine.player.get("items", [])
            pills = [i for i in inv if self.engine.item_rules.get(i, {}).get("type") == "consumable"]
            if pills and self.select_idx < len(pills):
                self.engine.reverse_engineer(pills[self.select_idx])
                self._play_sound("confirm")
        elif e.key == pygame.K_d:
            self.engine.study_alchemy()
            self._play_sound("confirm")

    def _render_alchemy(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        fdata = self.engine._get_furnace_data()
        grade = self.engine.alchemy_grade_name()
        progress = self.engine.alchemy_progress_text()
        header = f"炼药术: {grade} [{progress}]  |  药鼎: {fdata.get('name', '无')} (加成+{fdata['bonus']}%)"
        t = self.font_small.render(header, True, (160, 160, 180))
        self.screen.blit(t, (20, 10))
        hint = self.font_small.render("[Up/Down]选择丹方 [Space]炼制 [R]逆向研究 [D]研读 [Esc]返回", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 180, 36))
        recipes = self.engine.available_recipes()
        y_pos = 70
        for i, r in enumerate(recipes):
            icon = "> " if i == self.alchemy_idx else "  "
            color = C_ACCENT if i == self.alchemy_idx else C_TEXT
            line = f"{icon}{r['name']} -> {r['output']} ({r['grade']}p, rate {r['rate']}%)"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 24
            if i == self.alchemy_idx and r.get("materials"):
                mats = ", ".join(r["materials"])
                mt = self.font_small.render(f"    Materials: {mats}", True, (140, 140, 160))
                self.screen.blit(mt, (20, y_pos))
                y_pos += 20
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))

    # ── 拍卖行界面 ───────────────────────────────────────────

    def _update_auction_listings(self) -> None:
        self.engine.get_auction_listings()
        self.auction_listings = self.engine.auction_listings
        self.auction_idx = 0

    def _key_auction(self, e: pygame.event.Event) -> None:
        listings = self.engine.auction_listings
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.auction_idx = max(0, self.auction_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.auction_idx = min(max(0, len(listings) - 1), self.auction_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if listings and self.auction_idx < len(listings):
                self.engine.auction_buy(self.auction_idx)
                self._play_sound("confirm")
                self._update_auction_listings()
        elif e.key == pygame.K_s:
            inv = self.engine.player.get("items", [])
            if inv and self.select_idx < len(inv):
                item_id = inv[self.select_idx]
                price = self.engine.item_rules.get(item_id, {}).get("price_sell", 100)
                self.engine.auction_sell(self.select_idx, max(1, price))
                self._play_sound("confirm")
                self._update_auction_listings()

    def _render_auction(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        wallet = self.engine.wallet_display(self.engine.player.get("wallet", {}))
        t = self.font_title.render(f"Auction  |  Funds: {wallet}", True, C_ACCENT)
        self.screen.blit(t, (20, 10))
        hint = self.font_small.render("[Up/Down]Select [Space]Buy [S]Sell selected [Esc]Back", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 170, 44))
        listings = self.engine.auction_listings
        y_pos = 70
        for i, item in enumerate(listings):
            icon = "> " if i == self.auction_idx else "  "
            color = C_ACCENT if i == self.auction_idx else C_TEXT
            cur = "Ancient" if item.get("currency") == "ancient" else "Copper"
            sold = " [Yours]" if item.get("player_sold") else ""
            left = item.get("time_left", 0)
            line = f"{icon}{item['name']} - {item['price']}{cur} ({left} periods left){sold}"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 26
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))

    # ── 功法界面 ─────────────────────────────────────────────

    def _key_technique(self, e: pygame.event.Event) -> None:
        known = self.engine.player.get("known_techniques", [])
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.technique_idx = max(0, self.technique_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.technique_idx = min(max(0, len(known) - 1), self.technique_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if known and self.technique_idx < len(known):
                tid = known[self.technique_idx]
                if self.engine.player.get("equipped_technique") == tid:
                    self.engine.unequip_technique()
                else:
                    self.engine.equip_technique(tid)
                self._play_sound("confirm")
        elif e.key == pygame.K_u:
            self.engine.unequip_technique()
            self._play_sound("confirm")

    def _render_technique(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        t = self.font_title.render("Techniques", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 10))
        current = self.engine.player.get("equipped_technique")
        cur_name = "None"
        if current:
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == current), None)
            cur_name = f"{tech['name']} ({tech['element']} tier:{tech['tier']})" if tech else current
        ct = self.font_small.render(f"Active: {cur_name}", True, (160, 200, 160))
        self.screen.blit(ct, (20, 36))
        hint = self.font_small.render("[Up/Down]Select [Space]Equip/Switch [U]Unequip [Esc]Back", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 160, 62))
        known = self.engine.player.get("known_techniques", [])
        y_pos = 90
        for i, tid in enumerate(known):
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
            if not tech:
                continue
            icon = "> " if i == self.technique_idx else "  "
            equipped = " [ACTIVE]" if tid == current else ""
            color = C_ACCENT if i == self.technique_idx else C_TEXT
            line = f"{icon}{tech['name']} ({tech['element']} {tech['tier']}){equipped}"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 22
            if i == self.technique_idx:
                eff = self.font_small.render(f"    Effect: {tech.get('effect', 'none')}  |  {tech.get('desc', '')}", True, (140, 140, 160))
                self.screen.blit(eff, (20, y_pos))
                y_pos += 20
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))

    # ── 源火界面 ─────────────────────────────────────────────

    def _key_flame(self, e: pygame.event.Event) -> None:
        collected = self.engine.player.get("collected_flames", [])
        if e.key == pygame.K_ESCAPE:
            self._play_sound("cancel")
            self.scene = SCENE_MENU
        elif e.key == pygame.K_UP:
            self.flame_idx = max(0, self.flame_idx - 1)
            self._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.flame_idx = min(len(HEAVENLY_FLAMES_FULL) - 1, self.flame_idx + 1)
            self._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.flame_idx < len(HEAVENLY_FLAMES_FULL):
                fid = HEAVENLY_FLAMES_FULL[self.flame_idx]["id"]
                if fid in self.engine.player.get("items", []):
                    self.engine.equip_flame(fid)
                elif self.engine.player.get("equipped_flame") == fid:
                    self.engine.unequip_flame()
                self._play_sound("confirm")
        elif e.key == pygame.K_u:
            self.engine.unequip_flame()
            self._play_sound("confirm")

    def _render_flame(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        collected = self.engine.player.get("collected_flames", [])
        current = self.engine.player.get("equipped_flame")
        t = self.font_title.render(f"Flames [{len(collected)}/23]", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 10))
        cur_name = "None"
        if current:
            f = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == current), None)
            cur_name = f"{f['name']} ({f['tier']})" if f else current
        ct = self.font_small.render(f"Active: {cur_name}", True, (160, 200, 160))
        self.screen.blit(ct, (20, 36))
        hint = self.font_small.render("[Up/Down]Select [Space]Equip/Store [U]Unequip [Esc]Back", True, (120, 120, 130))
        self.screen.blit(hint, (w // 2 - 160, 62))
        y_pos = 90
        for i, flame in enumerate(HEAVENLY_FLAMES_FULL):
            fid = flame["id"]
            owned = fid in collected or fid in self.engine.player.get("items", [])
            equipped = fid == current
            icon = "> " if i == self.flame_idx else "  "
            status = " [ACTIVE]" if equipped else (" [OWNED]" if owned else " [LOST]")
            color = C_ACCENT if i == self.flame_idx else (C_TEXT if owned else (100, 100, 110))
            line = f"{icon}#{flame['rank']} {flame['name']} ({flame['tier']}){status}"
            text = self.font_body.render(line, True, color)
            self.screen.blit(text, (20, y_pos))
            y_pos += 22
            if i == self.flame_idx:
                bonus = FLAME_TIER_BONUS.get(flame['tier'], {})
                abonus = FLAME_ALCHEMY_BONUS.get(flame['tier'], {})
                detail = f"    Combat: ATK+{bonus.get('atk',0)} SPD+{bonus.get('spd',0)} Fire+{bonus.get('fire_power',0)}  |  Alchemy: Success+{abonus.get('success',0)}% EXP+{abonus.get('exp',0)}"
                eff = self.font_small.render(detail, True, (140, 140, 160))
                self.screen.blit(eff, (20, y_pos))
                y_pos += 20
                desc = self.font_small.render(f"    {flame.get('desc', '')}", True, (120, 120, 140))
                self.screen.blit(desc, (20, y_pos))
                y_pos += 20
            if y_pos > h - 40:
                break
        msg = self.engine.last_message
        if msg:
            mt = self.font_small.render(msg, True, (200, 200, 100))
            self.screen.blit(mt, (20, h - 30))

    def _render_menu(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        t = self.font_title.render("游 戏 菜 单", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 40))
        items = ["返回游戏", "状态详情", "物品背包", "技能列表", "保存游戏", "读取存档", "退出游戏"]
        for i, item in enumerate(items):
            icon = "▶ " if i == self.menu_idx else "  "
            color = C_ACCENT if i == self.menu_idx else C_TEXT
            line = self.font_body.render(f"{icon}{item}", True, color)
            self.screen.blit(line, (w // 2 - 60, 100 + i * 36))

    # ── 背包界面 ────────────────────────────────────────────

    def _render_inventory(self) -> None:
        self.screen.fill((20, 20, 30))
        w, h = self.screen.get_size()
        if self.gift_item_id:
            targets = self.engine.gift_targets()
            title = self.font_title.render(
                f"赠送 {self.engine.item_name(self.gift_item_id)}", True, C_ACCENT
            )
            self.screen.blit(title, (w // 2 - title.get_width() // 2, 30))
            for index, target in enumerate(targets):
                color = C_ACCENT if index == self.gift_target_idx else C_TEXT
                prefix = "▶ " if index == self.gift_target_idx else "  "
                line = self.font_body.render(
                    f"{prefix}{target['name']}（{target['stage']}）", True, color
                )
                self.screen.blit(line, (w // 2 - 130, 100 + index * 28))
            return

        # 标题 + 操作提示
        t = self.font_title.render("背 包", True, C_ACCENT)
        self.screen.blit(t, (w // 2 - t.get_width() // 2, 10))
        self.screen.blit(
            self.font_small.render("[↑↓]选择 [空格]装备/使用 [U]卸下 [I/Esc]返回", True, (120, 120, 130)),
            (w // 2 - 160, 44)
        )

        # ── 装备槽（左侧） ──
        equipped = self.engine.player.get("equipped", {})
        slot_names = {"weapon": "武器", "armor": "防具", "accessory": "饰品"}
        sy = 75
        pygame.draw.rect(self.screen, (30, 30, 40), (30, sy - 5, 240, 95), border_radius=6)
        self.screen.blit(self.font_small.render("── 已装备 ──", True, C_ACCENT), (42, sy))
        for j, slot in enumerate(EQUIPMENT_SLOTS):
            item_id = equipped.get(slot)
            name = EQUIPMENT_DATA.get(item_id, {}).get("name", "空") if item_id else "空"
            eq_color = C_ACCENT if item_id else (100, 100, 110)
            eq_line = self.font_small.render(f"{slot_names[slot]}: {name}", True, eq_color)
            if item_id:
                draw_item_icon(
                    self.screen, item_id, self.engine.item_rules.get(item_id, {}),
                    40, sy + 18 + j * 22, 20,
                )
            self.screen.blit(eq_line, (64, sy + 22 + j * 22))

        # ── 背包物品（右侧） ──
        inv = self.engine.player.get("items", [])
        if not inv:
            mt = self.font_body.render("背包空空如也", True, (100, 100, 110))
            self.screen.blit(mt, (320, h // 2))
        else:
            for i, item_id in enumerate(inv):
                rule = self.engine.item_rules.get(item_id, {})
                name = self.engine.item_name(item_id)
                eq = EQUIPMENT_DATA.get(item_id)
                is_equippable = eq is not None
                icon = "▶ " if i == self.select_idx else "  "
                color = C_ACCENT if i == self.select_idx else C_TEXT
                line = f"{icon}{name}"
                if is_equippable:
                    line += f" [+{eq.get('atk',0) or eq.get('def',0) or eq.get('hp',0)}{'攻' if eq.get('atk') else '防' if eq.get('def') else '命'}]"
                elif rule.get("use_effect"):
                    line += " [可使用]"
                t2 = self.font_body.render(line, True, color)
                draw_item_icon(
                    self.screen, item_id, rule, 304, 72 + i * 26, 24,
                    i == self.select_idx,
                )
                self.screen.blit(t2, (330, 75 + i * 26))
                if i >= 16:
                    break
            # 提示
            if self.select_idx < len(inv):
                sid = inv[self.select_idx]
                srule = self.engine.item_rules.get(sid, {})
                sdesc = srule.get("description", "")
                seq = EQUIPMENT_DATA.get(sid)
                if seq:
                    sdesc = f"装备: {seq['name']} ({seq['slot']}) ATK+{seq['atk']} DEF+{seq['def']} HP+{seq['hp']}"
                if sdesc:
                    dt = self.font_small.render(f"  {sdesc}", True, (150, 150, 160))
                    self.screen.blit(dt, (310, h - 28))


# ═══════════════════════════════════════════════════════════════════
# 战斗视图
# ═══════════════════════════════════════════════════════════════════

class CombatView:
    """回合制战斗画面。"""

    def __init__(self) -> None:
        self.actions = ["普通攻击", "施展灵技", "防御", "使用丹药", "蓄力", "逃跑", "自动战斗"]
        self.selected = 0
        self.sub_mode = ""  # "" | "skill" | "item"
        self.sub_idx = 0

    def handle_key(self, e: pygame.event.Event, engine: GameEngine, game: Any = None) -> None:
        if self.sub_mode == "skill":
            self._handle_skill_select(e, engine, game)
            return
        if self.sub_mode == "item":
            self._handle_item_select(e, engine, game)
            return

        if e.key == pygame.K_UP:
            self.selected = max(0, self.selected - 1)
            if game:
                game._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.selected = min(len(self.actions) - 1, self.selected + 1)
            if game:
                game._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            act = self.actions[self.selected]
            if act == "施展灵技":
                skills = engine.combat_skills()
                if skills:
                    self.sub_mode = "skill"
                    self.sub_idx = 0
                    if game:
                        game._play_sound("confirm")
                else:
                    engine.last_message = "尚未习得任何灵技。"
                    if game:
                        game._play_sound("bump")
            elif act == "使用丹药":
                items = self._combat_usable_items(engine)
                if items:
                    self.sub_mode = "item"
                    self.sub_idx = 0
                    if game:
                        game._play_sound("confirm")
                else:
                    engine.last_message = "没有可用的丹药。"
                    if game:
                        game._play_sound("bump")
            else:
                cmd_map = {
                    "普通攻击": "attack", "防御": "defend",
                    "蓄力": "charge", "逃跑": "escape", "自动战斗": "auto",
                }
                cmd = cmd_map.get(act, "attack")
                result = engine.combat_action(cmd)
                if game:
                    game._play_combat_result(result, cmd)
        elif e.key == pygame.K_ESCAPE:
            if game:
                result = engine.combat_action("escape")
                game._play_combat_result(result, "escape")
                if engine.combat is None:
                    game.scene = SCENE_EXPLORE

    def _handle_skill_select(
        self, e: pygame.event.Event, engine: GameEngine, game: Any = None
    ) -> None:
        skills = engine.combat_skills()
        if e.key == pygame.K_ESCAPE:
            self.sub_mode = ""
            if game:
                game._play_sound("cancel")
        elif e.key == pygame.K_UP:
            self.sub_idx = max(0, self.sub_idx - 1)
            if game:
                game._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.sub_idx = min(len(skills) - 1, self.sub_idx + 1)
            if game:
                game._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if skills:
                result = engine.combat_action("skill", skill_id=skills[self.sub_idx]["id"])
                if game:
                    game._play_combat_result(result, "skill")
                self.sub_mode = ""

    def _handle_item_select(
        self, e: pygame.event.Event, engine: GameEngine, game: Any = None
    ) -> None:
        items = self._combat_usable_items(engine)
        if e.key == pygame.K_ESCAPE:
            self.sub_mode = ""
            if game:
                game._play_sound("cancel")
        elif e.key == pygame.K_UP:
            self.sub_idx = max(0, self.sub_idx - 1)
            if game:
                game._play_sound("select")
        elif e.key == pygame.K_DOWN:
            self.sub_idx = min(len(items) - 1, self.sub_idx + 1)
            if game:
                game._play_sound("select")
        elif e.key in (pygame.K_RETURN, pygame.K_SPACE):
            if items:
                result = engine.combat_action("item", skill_id=items[self.sub_idx])
                if game:
                    game._play_combat_result(result, "item")
                self.sub_mode = ""

    @staticmethod
    def _combat_usable_items(engine: GameEngine) -> List[str]:
        """返回战斗中可使用的物品列表。"""
        return engine.combat_usable_items()

    @staticmethod
    def _element_color(element: str) -> Tuple[int, int, int]:
        return {
            "火": (239, 91, 45), "冰": (111, 204, 229), "雷": (189, 143, 245),
            "风": (104, 205, 153), "毒": (145, 187, 70), "木": (76, 175, 80),
            "土": (190, 142, 76),
        }.get(element, (205, 72, 72))

    def _draw_battle_background(
        self, screen: pygame.Surface, element: str, enemy_type: str,
    ) -> None:
        """按属性与敌人级别绘制战斗舞台。"""
        w, h = screen.get_size()
        accent = self._element_color(element)
        top = tuple(max(8, value // 7) for value in accent)
        bottom = tuple(max(12, value // 4) for value in accent)
        for y in range(h):
            ratio = y / max(1, h - 1)
            color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
            pygame.draw.line(screen, color, (0, y), (w, y))

        pygame.draw.circle(screen, tuple(min(255, c + 55) for c in accent), (w // 2, 165), 92, 2)
        pygame.draw.circle(screen, accent, (w // 2, 165), 74, 1)
        for i in range(12):
            angle = i * math.pi / 6
            x1 = w // 2 + int(math.cos(angle) * 78)
            y1 = 165 + int(math.sin(angle) * 78)
            x2 = w // 2 + int(math.cos(angle) * 88)
            y2 = 165 + int(math.sin(angle) * 88)
            pygame.draw.line(screen, accent, (x1, y1), (x2, y2), 2)

        ground_y = h - 205
        pygame.draw.polygon(
            screen, tuple(max(10, c // 3) for c in accent),
            [(0, ground_y + 50), (w // 2, ground_y), (w, ground_y + 50), (w, h), (0, h)],
        )
        if enemy_type in ("boss", "final_boss"):
            pygame.draw.rect(screen, accent, (0, 0, w, 4))
            pygame.draw.rect(screen, accent, (0, h - 4, w, 4))

    def _draw_enemy_portrait(
        self, screen: pygame.Surface, combat: Dict[str, Any], enemy_data: Dict[str, Any],
        cx: int, cy: int,
    ) -> None:
        """为每个敌人生成稳定且有类型差异的像素立绘。"""
        enemy_id = combat.get("enemy_id", "")
        enemy_type = enemy_data.get("type", combat.get("type", "normal"))
        element = combat.get("element", "")
        accent = self._element_color(element)
        seed = sum((index + 1) * ord(ch) for index, ch in enumerate(enemy_id))
        is_boss = enemy_type in ("boss", "final_boss")
        is_elite = enemy_type == "elite"
        scale = 1
        body = tuple(max(35, min(220, c - 35 + seed % 45)) for c in accent)
        dark = tuple(max(18, c // 3) for c in body)
        light = tuple(min(255, c + 70) for c in body)

        aura = pygame.Surface((190, 170), pygame.SRCALPHA)
        aura_alpha = 75 if is_boss else 48
        for radius in range(72, 38, -10):
            pygame.draw.circle(aura, (*accent, max(8, aura_alpha - radius // 2)), (95, 86), radius, 3)
        screen.blit(aura, (cx - 95, cy - 86))

        beast_tokens = ("beast", "wolf", "lion", "snake", "python", "dragon", "兽", "狼", "狮", "蛇", "龙")
        spirit_tokens = ("soul", "spirit", "flame", "ghost", "魂", "灵", "火")
        text = f"{enemy_id} {combat.get('name', '')}".lower()
        if any(token in text for token in beast_tokens):
            pygame.draw.ellipse(screen, dark, (cx - 40 * scale, cy - 18, 80 * scale, 45))
            pygame.draw.circle(screen, body, (cx + 22 * scale, cy - 17), 25 * scale)
            pygame.draw.polygon(screen, dark, [(cx + 5, cy - 34), (cx + 13, cy - 60), (cx + 25, cy - 32)])
            pygame.draw.polygon(screen, dark, [(cx + 28, cy - 34), (cx + 44, cy - 58), (cx + 48, cy - 27)])
            pygame.draw.circle(screen, light, (cx + 15 * scale, cy - 20), 4 * scale)
            pygame.draw.circle(screen, light, (cx + 31 * scale, cy - 20), 4 * scale)
            pygame.draw.line(screen, light, (cx - 32 * scale, cy + 7), (cx - 55 * scale, cy + 28), 6)
        elif any(token in text for token in spirit_tokens):
            pygame.draw.polygon(
                screen, body,
                [(cx, cy - 66 * scale), (cx - 34 * scale, cy + 35), (cx, cy + 22), (cx + 34 * scale, cy + 35)],
            )
            for offset in (-24, 0, 24):
                pygame.draw.polygon(
                    screen, light,
                    [(cx + offset, cy + 28), (cx + offset - 8, cy + 52), (cx + offset + 8, cy + 40)],
                )
            pygame.draw.circle(screen, dark, (cx, cy - 20 * scale), 21 * scale)
            pygame.draw.circle(screen, light, (cx - 7, cy - 23 * scale), 4 * scale)
            pygame.draw.circle(screen, light, (cx + 7, cy - 23 * scale), 4 * scale)
        else:
            shoulder = 33 * scale
            pygame.draw.polygon(
                screen, dark,
                [(cx - shoulder, cy + 35), (cx + shoulder, cy + 35),
                 (cx + 24 * scale, cy - 24), (cx - 24 * scale, cy - 24)],
            )
            pygame.draw.rect(screen, body, (cx - 24 * scale, cy - 26 * scale, 48 * scale, 52 * scale))
            pygame.draw.rect(screen, (214, 166, 129), (cx - 16 * scale, cy - 58 * scale, 32 * scale, 30 * scale))
            pygame.draw.rect(screen, dark, (cx - 19 * scale, cy - 65 * scale, 38 * scale, 13 * scale))
            pygame.draw.rect(screen, light, (cx - 10 * scale, cy - 47 * scale, 6 * scale, 4 * scale))
            pygame.draw.rect(screen, light, (cx + 5 * scale, cy - 47 * scale, 6 * scale, 4 * scale))
            if seed % 2:
                pygame.draw.line(screen, light, (cx + 28 * scale, cy + 22), (cx + 48 * scale, cy - 70), 6)
            else:
                pygame.draw.circle(screen, light, (cx + 42 * scale, cy - 28), 13, 4)

        if is_elite or is_boss:
            wing = 42 if is_elite else 62
            pygame.draw.polygon(screen, accent, [(cx - 22, cy - 20), (cx - wing, cy - 48), (cx - 38, cy + 12)], 3)
            pygame.draw.polygon(screen, accent, [(cx + 22, cy - 20), (cx + wing, cy - 48), (cx + 38, cy + 12)], 3)
        if is_boss:
            pygame.draw.polygon(
                screen, (244, 199, 73),
                [(cx - 23, cy - 72 * scale), (cx - 12, cy - 91 * scale), (cx, cy - 76 * scale),
                 (cx + 12, cy - 91 * scale), (cx + 23, cy - 72 * scale)],
            )
        if enemy_type == "final_boss":
            pygame.draw.circle(screen, (255, 238, 154), (cx, cy - 8), 82, 3)
            pygame.draw.circle(screen, accent, (cx, cy - 8), 95, 2)

    def render(self, screen, engine, font_title, font_body) -> None:
        if engine.combat is None:
            return
        c = engine.combat
        p = engine.player
        w, h = screen.get_size()
        enemy_data = engine.enemies.get(c.get("enemy_id", ""), {})
        enemy_type = enemy_data.get("type", c.get("type", "normal"))
        self._draw_battle_background(screen, c.get("element", ""), enemy_type)
        soul = int(p.get("soul", 0))

        bw, bx = 360, w // 2 - 180

        # ── 敌人 ──
        ey = 48
        en = font_title.render(c["name"], True, (220, 60, 60))
        screen.blit(en, (w // 2 - en.get_width() // 2, ey))
        el = font_body.render(
            f"[{c.get('element', '?')}属性]  弱点: {c.get('weakness', '?')}"
            + ("  护盾已破" if c.get("shield_broken") else ""),
            True, (200, 140, 60)
        )
        screen.blit(el, (w // 2 - el.get_width() // 2, ey + 28))

        hp_r = max(0, c["hp"] / max(1, c["max_hp"]))
        pygame.draw.rect(screen, (40, 15, 15), (bx, ey + 52, bw, 12))
        pygame.draw.rect(screen, (200, 50, 50), (bx, ey + 52, int(bw * hp_r), 12))
        hp_t = font_body.render(f"HP {c['hp']}/{c['max_hp']}", True, (220, 220, 230))
        screen.blit(hp_t, (bx, ey + 66))

        # 敌人像素立绘
        ecx, ecy = w // 2, ey + 154
        self._draw_enemy_portrait(screen, c, enemy_data, ecx, ecy)
        rank_text = {"elite": "精英", "boss": "首领", "final_boss": "最终首领"}.get(enemy_type, "")
        if rank_text:
            badge = font_body.render(rank_text, True, (255, 224, 134))
            screen.blit(badge, (ecx - badge.get_width() // 2, ecy + 55))

        # ── 意图预判 ──
        if soul >= 20:
            intent = engine.combat_intent_text()
            ic = {"攻击": (255, 80, 80), "防御": (80, 160, 255)}.get(
                intent[:2] if intent.startswith("灵技") else intent, (255, 180, 60))
            # 如果以 "灵技「" 开头就用技能颜色
            if intent.startswith("灵技"):
                ic = (255, 180, 60)
            it = font_body.render(f"👁 下回合: {intent}", True, ic)
            screen.blit(it, (18, ey + 104))
        else:
            it = font_body.render(f"灵魂感知 {soul}/20 可预判", True, (100, 100, 120))
            screen.blit(it, (18, ey + 104))

        # ── 敌人技能列表 ──
        enemy_skills = engine.enemy_skill_list()
        if enemy_skills:
            sk = font_body.render(f"技能: {'、'.join(enemy_skills[:3])}", True, (180, 140, 100))
            screen.blit(sk, (bx, ey + 226))

        # ── 玩家 ──
        py_ = h - 170
        pn = font_title.render(p.get("name", "林烬"), True, (80, 210, 120))
        screen.blit(pn, (w // 2 - pn.get_width() // 2, py_))

        hp_rp = max(0, p["hp"] / max(1, p["max_hp"]))
        pygame.draw.rect(screen, (40, 15, 15), (bx, py_ + 30, bw, 10))
        pygame.draw.rect(screen, (200, 50, 50), (bx, py_ + 30, int(bw * hp_rp), 10))
        pt = font_body.render(
            f"HP {p['hp']}/{p['max_hp']}  灵力 {p.get('douqi', 0)}", True, (220, 220, 230)
        )
        screen.blit(pt, (bx, py_ + 42))

        # 连击/蓄力/中毒
        combo = engine.combat_combo()
        if combo >= 2:
            ct = font_body.render(f"🔥 {combo}连击 +{int(min(combo,COMBO_MAX)*COMBO_DAMAGE_PER_STACK*100)}%", True, (255,180,40))
            screen.blit(ct, (bx, py_+56))
        if engine.combat_charged():
            screen.blit(font_body.render("⚡ 蓄力就绪 x2.0", True, (180,220,100)), (bx+180, py_+56))
        poison = engine.combat.get("poison",0) if engine.combat else 0
        if poison > 0:
            pt = font_body.render(f"☠️ 中毒 {poison}层(-{engine.combat.get('poison_dmg',0)}/回)", True, (180,80,200))
            screen.blit(pt, (bx, py_+56))

        # 回合
        rt = font_body.render(f"第 {c['round']} 回合", True, (200, 160, 40))
        screen.blit(rt, (w - rt.get_width() - 18, ey + 104))

        # ── CTB action gauge ──
        p_gauge = c.get("player_gauge", 0)
        e_gauge = c.get("enemy_gauge", 0)
        p_pct = min(1.0, p_gauge / 1000.0)
        e_pct = min(1.0, e_gauge / 1000.0)
        gx, gy, gw, gh = 10, ey + 84, w - 20, 8
        pygame.draw.rect(screen, (30, 30, 40), (gx, gy, gw, gh), border_radius=2)
        pygame.draw.rect(screen, (220, 80, 80), (gx, gy, int(gw * e_pct), gh), border_radius=2)
        el = font_body.render(f"Gauge {e_gauge}/1000", True, (180, 180, 190))
        screen.blit(el, (gx + 4, gy - 2))
        pyg = py_ + 70
        pygame.draw.rect(screen, (30, 30, 40), (gx, pyg, gw, gh), border_radius=2)
        pygame.draw.rect(screen, (60, 200, 100), (gx, pyg, int(gw * p_pct), gh), border_radius=2)
        pl = font_body.render(f"Gauge {p_gauge}/1000", True, (180, 180, 190))
        screen.blit(pl, (gx + 4, pyg - 2))

        # menu
        my_ = py_ + 80
        if self.sub_mode:
            # 子菜单：技能选择或物品选择
            sub_title = "选择灵技" if self.sub_mode == "skill" else "选择丹药"
            sub_label = font_title.render(sub_title, True, C_ACCENT)
            screen.blit(sub_label, (bx, my_ - 28))
            sub_items: List[str] = []
            if self.sub_mode == "skill":
                sub_items = [f"{s['name']} [{SKILL_ELEMENTS.get(s['id'], '?')}] {engine._skill_cost(s)}灵力"
                             for s in engine.combat_skills()]
            else:
                combat_item_ids = self._combat_usable_items(engine)
                sub_items = [f"{engine.item_name(iid)} {'+' + engine.item_rules.get(iid, {}).get('use_effect', '')}"
                             for iid in combat_item_ids]
            for i, line in enumerate(sub_items):
                icon = "▶ " if i == self.sub_idx else "  "
                color = C_ACCENT if i == self.sub_idx else C_TEXT
                t = font_body.render(f"{icon}{line}", True, color)
                text_x = bx + 10
                if self.sub_mode == "item":
                    item_id = combat_item_ids[i]
                    draw_item_icon(
                        screen, item_id, engine.item_rules.get(item_id, {}),
                        bx + 8, my_ + i * 24 - 2, 22, i == self.sub_idx,
                    )
                    text_x = bx + 32
                screen.blit(t, (text_x, my_ + i * 24))
                if i >= 6:
                    break
        else:
            for i, act in enumerate(self.actions):
                icon = "▶ " if i == self.selected else "  "
                color = (200, 160, 40) if i == self.selected else (220, 220, 230)
                t = font_body.render(f"{icon}{act}", True, color)
                col = i % 4
                row = i // 4
                screen.blit(t, (bx + col * 95, my_ + row * 26))

        if engine.last_message:
            msg = engine.last_message[:55]
            mt = font_body.render(msg, True, (200, 200, 100))
            screen.blit(mt, (w // 2 - mt.get_width() // 2, h - 24))


def main() -> None:
    PygameGame().run()


if __name__ == "__main__":
    main()
