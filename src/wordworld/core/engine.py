import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from wordworld.data.workbook import load_game_data
from wordworld.data.equipment_data import EQUIPMENT_DATA as _GEN_EQUIPMENT
from wordworld.data.item_data import ITEM_DATA as _GEN_ITEMS
from wordworld.data.loot_table import LOOT_TABLE
from wordworld.data.flame_data import HEAVENLY_FLAMES_FULL
from wordworld.data.technique_data import TECHNIQUE_DATA
from wordworld.data.skill_book_data import SKILL_BOOK_DATA
from wordworld.data.skill_elements_full import SKILL_ELEMENTS_FULL
from wordworld.data.elemental_rules import ELEMENTAL_RULES
from wordworld.data.skill_mastery_data import build_skill_mastery
from wordworld.data.enemy_skill_fallbacks import ENEMY_SKILL_FALLBACKS
from wordworld.data.furnace_data import FURNACE_DATA
from wordworld.data.recipe_data import ALCHEMY_RECIPE_DATA
from wordworld.config.paths import SAVE_PATH, WORKBOOK_PATH


LEGACY_STAT_ALIASES = {
    "attack": "atk",
    "defense": "def",
    "neili": "douqi",
}

LEGACY_FLAG_ALIASES = {
    "ancient_emperor_jade": "emperor_cave_opened",
}

# ── 四币货币系统 ───────────────────────────────────────────
# 100铜=1银, 100银=1金, 1000金=1远古币
COPPER_PER_SILVER = 100
SILVER_PER_GOLD = 100
GOLD_PER_ANCIENT = 1000

def wallet_display(wallet: Dict[str, int]) -> str:
    """格式化显示钱包。"""
    parts = []
    if wallet.get("ancient", 0) > 0:
        parts.append(f"{wallet['ancient']}远古币")
    if wallet.get("gold", 0) > 0:
        parts.append(f"{wallet['gold']}金")
    if wallet.get("silver", 0) > 0:
        parts.append(f"{wallet['silver']}银")
    parts.append(f"{wallet.get('copper', 0)}铜")
    return " ".join(parts) if parts else "0铜"

def wallet_total(wallet: Dict[str, int]) -> int:
    """钱包总和（铜币等价）。"""
    return (wallet.get("copper", 0) +
            wallet.get("silver", 0) * COPPER_PER_SILVER +
            wallet.get("gold", 0) * COPPER_PER_SILVER * SILVER_PER_GOLD +
            wallet.get("ancient", 0) * COPPER_PER_SILVER * SILVER_PER_GOLD * GOLD_PER_ANCIENT)

def wallet_normalize(wallet: Dict[str, int]) -> Dict[str, int]:
    """自动进位规范化钱包。"""
    total = wallet_total(wallet)
    ancient = total // (COPPER_PER_SILVER * SILVER_PER_GOLD * GOLD_PER_ANCIENT)
    total %= (COPPER_PER_SILVER * SILVER_PER_GOLD * GOLD_PER_ANCIENT)
    gold = total // (COPPER_PER_SILVER * SILVER_PER_GOLD)
    total %= (COPPER_PER_SILVER * SILVER_PER_GOLD)
    silver = total // COPPER_PER_SILVER
    copper = total % COPPER_PER_SILVER
    return {"copper": copper, "silver": silver, "gold": gold, "ancient": ancient}

def wallet_add(wallet: Dict[str, int], copper_amount: int) -> Dict[str, int]:
    """钱包加铜币（可负数为扣减），自动进位。"""
    total = wallet_total(wallet) + copper_amount
    return wallet_normalize({"copper": max(0, total), "silver": 0, "gold": 0, "ancient": 0})

def wallet_can_afford(wallet: Dict[str, int], copper_price: int) -> bool:
    return wallet_total(wallet) >= copper_price

# 不受任何事件影响的满值关系（家人与导师）
IMMUNE_RELATIONSHIPS = {
    "rel_player_xiao_zhan",  # 萧战-父亲
    "rel_player_xiao_ding",  # 萧鼎-二哥
    "rel_player_xiao_li",    # 萧厉-三哥
    "rel_player_xun_er",     # 萧薰儿
    "rel_player_yao_lao",    # 药老-导师
}

COMPARISON_PATTERN = re.compile(r"^(.+?)(>=|<=|==|!=|>|<)(-?\d+)$")
RELATION_EFFECT_PATTERN = re.compile(r"^rel:([^:=]+):([+-]\d+)$")
RELATION_SET_PATTERN = re.compile(r"^rel:([^:=]+)=(-?\d+)$")
ON_REACH_PATTERN = re.compile(r"^(rel:.+?(?:>=|<=|==|!=|>|<)-?\d+):(.*)$")
EXP_FORMULA_PATTERN = re.compile(r"^level\*(\d+)$")

LEVEL_SKILL_MILESTONES = {
    10: "skill_alchemy",
    20: "skill_wind_thunder",
    30: "skill_flame",
    40: "skill_healing",
    50: "skill_gold_flame",
}

# 境界突破的 level 分界点（每个境界的最后一级）
REALM_BOUNDARY_LEVELS = {9, 19, 29, 39, 49, 59, 69, 79, 89, 94, 99}

# 境界突破成功率表：realm_index → chance%
REALM_BREAKTHROUGH_CHANCE_BP = {
    # 境界突破概率（万分之一为单位，1bp = 0.01%）
    0: 5000,  # 斗之气→斗者: 50%
    1: 3500,  # 斗者→斗师: 35%
    2: 2500,  # 斗师→大斗师: 25%
    3: 1500,  # 大斗师→斗灵: 15%  ← 大幅下降起点
    4: 800,   # 斗灵→斗王: 8%
    5: 400,   # 斗王→斗皇: 4%
    6: 200,   # 斗皇→斗宗: 2%
    7: 80,    # 斗宗→斗尊: 0.8%
    8: 30,    # 斗尊→斗圣: 0.3%
    9: 5,     # 斗圣→斗圣高阶: 0.05%
    10: 1,    # 斗圣高阶→斗帝: 0.01%
}

# ── 炼药术系统 ─────────────────────────────────────────────
# 十品炼药术：一品→九品→帝品
ALCHEMY_GRADES = ["一品", "二品", "三品", "四品", "五品", "六品", "七品", "八品", "九品", "帝品"]
ALCHEMY_SUB_PER_GRADE = 10       # 每品10个小进度
ALCHEMY_EXP_PER_SUB = 100        # 每个小进度需要100经验
ALCHEMY_EXP_PER_GRADE = ALCHEMY_SUB_PER_GRADE * ALCHEMY_EXP_PER_SUB  # 1000

# 炼药配方（从生成数据导入，504种）
ALCHEMY_RECIPES = ALCHEMY_RECIPE_DATA

REMOVED_ITEM_IDS = {
    "item_repair_hammer",
    "item_identify_scroll",
    "item_pet_food",
    "item_pet_taming_reins",
    "item_enchant_stone_1",
    "item_enchant_stone_2",
    "item_enchant_stone_3",
    "item_enchant_stone_4",
    "item_enchant_stone_5",
}

ELEMENT_ITEM_NAMES = {
    "fire": "火", "ice": "冰", "thunder": "雷", "wind": "风",
    "wood": "木", "earth": "土", "poison": "毒",
}

TIME_PERIODS = ["清晨", "午后", "傍晚", "深夜"]

EXPLORATION_ACTIONS = {
    "roam": {
        "name": "随性游历",
        "description": "均衡探索当前区域，遭遇类型不受偏向影响。",
        "cost_modifier": 0,
    },
    "scout": {
        "name": "侦察地形",
        "description": "少消耗 1 点体力，优先发现尚未处理过的遭遇，并锤炼灵魂感知。",
        "cost_modifier": -1,
    },
    "gather": {
        "name": "采集资源",
        "description": "多消耗 1 点体力，优先寻找非战斗机会，并收集可交易素材。",
        "cost_modifier": 1,
    },
    "hunt": {
        "name": "追猎强敌",
        "description": "多消耗 2 点体力，优先触发战斗遭遇。",
        "cost_modifier": 2,
    },
    "investigate": {
        "name": "调查线索",
        "description": "多消耗 1 点体力，优先调查较少处理的事件，并积累额外阅历。",
        "cost_modifier": 1,
    },
}

# 自动战斗中的终结类斗技只会在敌方生命不高于该比例时使用。
# ── 属性克制系统 ───────────────────────────────────────────
# 七元素克制链：火→木→土→雷→冰→风→毒→火
ELEMENT_TYPES = ["火", "冰", "雷", "风", "毒", "木", "土"]
ELEMENT_WEAKNESS = {
    "火": "木", "木": "土", "土": "雷", "雷": "冰",
    "冰": "风", "风": "毒", "毒": "火",
}
ELEMENT_ADVANTAGE = {v: k for k, v in ELEMENT_WEAKNESS.items()}

# ── 技能元素自动分配 ───────────────────────────────────────
_ELEMENT_KW = {
    "火": ["火","炎","焚","焰","烧","熔","烬","灼","阳","热","赤","烈","flame","fire","burn","inferno","magma","meteor"],
    "冰": ["冰","寒","冻","霜","雪","凝","冷","晶","ice","frost","frozen","blizzard","chill"],
    "雷": ["雷","电","霆","闪","霹","雳","轰","thunder","lightning","bolt","arc"],
    "风": ["风","云","飘","岚","飓","卷","翔","wind","gale","tempest","cyclone","gust"],
    "毒": ["毒","蛇","蝎","蛊","腐","瘴","瘟","紫","poison","venom","toxic","corrosive"],
    "木": ["木","树","林","森","藤","叶","花","草","根","芽","wood","forest","leaf","vine","plant"],
    "土": ["土","地","岩","石","山","沙","泥","尘","earth","rock","stone","sand","ground"],
}
_HAND_ASSIGNED = {
    "skill_bajibang": "火", "skill_flame_mantra": "火",
    "skill_alchemy": "毒", "skill_wind_thunder": "雷",
    "skill_flame": "火", "skill_healing": "冰", "skill_gold_flame": "火",
}

def _build_skill_elements(skills: Dict[str, Any]) -> Dict[str, str]:
    result = dict(_HAND_ASSIGNED)
    for sid, s in skills.items():
        if sid not in result:
            combined = s.get("name","") + s.get("description","")
            for elem, kws in _ELEMENT_KW.items():
                if any(kw in combined for kw in kws):
                    result[sid] = elem
                    break
    return result

SKILL_ELEMENTS: Dict[str, str] = {}

ENEMY_ELEMENTS: Dict[str, Dict[str, str]] = {}

# ── 纳戒系统 ───────────────────────────────────────────────
BASE_INVENTORY_CAPACITY = 50
STORAGE_RINGS = [
    {"id": "item_storage_ring_1", "name": "低阶纳戒", "tier": "spirit", "capacity": 100,
     "desc": "低阶纳戒，内含100格空间。", "price_buy": 50000, "price_sell": 10000},
    {"id": "item_storage_ring_2", "name": "中阶纳戒", "tier": "earth", "capacity": 200,
     "desc": "中阶纳戒，内含200格空间。", "price_buy": 150000, "price_sell": 30000},
    {"id": "item_storage_ring_3", "name": "高阶纳戒", "tier": "heaven", "capacity": 400,
     "desc": "高阶纳戒，内含400格空间。", "price_buy": 500000, "price_sell": 100000},
    {"id": "item_storage_ring_4", "name": "顶级纳戒", "tier": "saint", "capacity": 1000,
     "desc": "顶级纳戒，内含1000格空间，可纳山河。", "price_buy": 2000000, "price_sell": 400000},
]

# ── 拍卖行 ─────────────────────────────────────────────────
AUCTION_MARKUP_MIN = 1.5   # 最低加价倍数
AUCTION_MARKUP_MAX = 5.0   # 最高加价倍数
AUCTION_REFRESH_PERIODS = 4  # 每4个时段刷新一次
AUCTION_LISTING_COUNT = 8    # 每次刷新上架数量

# ── 物品定价（按类型） ─────────────────────────────────────
ITEM_PRICE_TABLE: Dict[str, Tuple[int, int]] = {
    "consumable": (10, 15),     # 消耗品：(买价, 卖价) 基础
    "equipment": (50, 25),
    "book": (40, 20),
    "quest": (100, 50),
    "heavenly_flame": (500, 250),
    "material": (15, 7),
    "currency": (1, 1),
    "key": (30, 15),
}
ITEM_PRICE_DEFAULT = (20, 10)

def item_price(item_type: str) -> Tuple[int, int]:
    """返回物品的 (买入价, 卖出价)。"""
    return ITEM_PRICE_TABLE.get(item_type, ITEM_PRICE_DEFAULT)

# ── 连击 & 蓄力 ───────────────────────────────────────────
COMBO_MAX = 10
COMBO_DAMAGE_PER_STACK = 0.12
CHARGE_DAMAGE_MULTIPLIER = 2.0

# ── 行动条（CTB） ───────────────────────────────────────────
GAUGE_MAX = 1000  # 行动条满值，达到后可行动

# ── 野外遇敌系统 ─────────────────────────────────────────
WILD_COMBAT_BASE_CHANCE = 0.35
WILD_COMBAT_HUNT_MULT = 2.0
WILD_COMBAT_SCOUT_MULT = 0.5
WILD_COMBAT_GATHER_MULT = 0.15
WILD_COMBAT_ROAM_MULT = 1.0
WILD_ELITE_WEIGHT = 0.15
WILD_MOB_WEIGHT = 0.85
RESPAWN_COOLDOWN_PERIODS = 3
BEAST_NAME_KEYWORDS = [
    "beast", "snake", "wolf", "tiger", "eagle", "spider", "scorpion", "insect",
    "dragon", "phoenix", "bear", "leopard", "fox", "lion", "elephant", "crocodile",
    "turtle", "frog", "monster", "serpent", "hawk", "hound", "ape",
]
CHARGE_DOUQI_PER_TURN = 5

FINISHER_SKILLS = {
    "skill_buddha_lotus": 0.30,
    "skill_great_silence_finger": 0.30,
    "skill_huangquan_finger": 0.30,
    "skill_annihilate_sky_seal": 0.30,
}

# ── 装备系统 ───────────────────────────────────────────────
EQUIPMENT_SLOTS = ["weapon", "armor", "accessory"]
EQUIPMENT_DATA: Dict[str, Dict[str, Any]] = _GEN_EQUIPMENT  # 2142件

# ── 异火系统 ───────────────────────────────────────────────
FLAME_TIER_BONUS: Dict[str, Dict[str, int]] = {
    "iron":     {"atk": 2, "spd": 1, "fire_power": 5},
    "refined":  {"atk": 4, "spd": 2, "fire_power": 8},
    "spirit":   {"atk": 6, "spd": 3, "fire_power": 12},
    "treasure": {"atk": 8, "spd": 4, "fire_power": 15},
    "earth":    {"atk": 10, "spd": 5, "fire_power": 18},
    "heaven":   {"atk": 14, "spd": 7, "fire_power": 22},
    "mystic":   {"atk": 18, "spd": 9, "fire_power": 28},
    "saint":    {"atk": 22, "spd": 11, "fire_power": 35},
    "emperor":  {"atk": 28, "spd": 14, "fire_power": 45},
    "divine":   {"atk": 35, "spd": 18, "fire_power": 60},
}
FLAME_ALCHEMY_BONUS: Dict[str, Dict[str, int]] = {
    "iron":     {"success": 1, "exp": 0, "quality": 0},
    "refined":  {"success": 2, "exp": 5, "quality": 0},
    "spirit":   {"success": 3, "exp": 8, "quality": 1},
    "treasure": {"success": 5, "exp": 12, "quality": 2},
    "earth":    {"success": 7, "exp": 15, "quality": 3},
    "heaven":   {"success": 9, "exp": 20, "quality": 5},
    "mystic":   {"success": 12, "exp": 25, "quality": 7},
    "saint":    {"success": 15, "exp": 30, "quality": 10},
    "emperor":  {"success": 18, "exp": 40, "quality": 14},
    "divine":   {"success": 22, "exp": 50, "quality": 20},
}
MAX_STORAGE_OVERFLOW = 200

# 上一版存档只保存数字阶段。该列表用于把旧数字位置迁移到稳定阶段 ID。
LEGACY_STORY_PHASE_IDS_V2 = [
    "fallen_genius", "three_year_pact", "ring_awakening", "wutan_growth",
    "mountain_training", "desert_flame", "alchemy_conference", "yunlan_duel",
    "canaan_outer", "canaan_inner", "fallen_heart", "black_corner_war",
    "yunlan_war", "zhongzhou_arrival", "dan_meeting_flame", "save_mentor",
    "ancient_ruins", "gu_clan_tomb", "bodhi_tree", "tianfu_alliance",
    "demon_flame", "medicine_ceremony", "ancient_clan_war", "ancient_emperor",
    "final_war", "five_emperors",
]


def _story_phase(
    phase_id: str,
    title: str,
    background: str,
    objective: str,
    risk: str,
    requirement: int,
    condition: str,
    effect: str,
    subnodes: List[Tuple[str, str, str, str]],
) -> Dict[str, Any]:
    return {
        "id": phase_id,
        "title": title,
        "background": background,
        "objective": objective,
        "risk": risk,
        "requirement": requirement,
        "condition": condition,
        "effect": effect,
        "subnodes": [
            {
                "title": node_title,
                "objective": node_objective,
                "condition": node_condition,
                "effect": node_effect,
            }
            for node_title, node_objective, node_condition, node_effect in subnodes
        ],
    }


# 主线必须按因果顺序显式排列，禁止再通过列表插入拼接时间线。
STORY_PHASES = [
    _story_phase("fallen_genius", "天才陨落", "斗气持续衰退，族内试炼迫近。", "稳住根基并重新证明自己。", "失败会失去族内资源与信任。", 2, "level>=2", "reputation:+3,rel:npc_xiao_zhan:+3", [
        ("查明斗气衰退", "观察身体与戒指的异常。", "soul>=5", "soul:+1"),
        ("族内试炼翻身", "在演武场重新证明实力。", "training_wins>=1", "reputation:+3"),
    ]),
    _story_phase("three_year_pact", "退婚与三年之约", "云岚宗登门退婚，萧家尊严受到挑战。", "维护家族尊严并立下三年之约。", "软弱回应会让萧家声望受损。", 3, "reputation>=5", "flag:three_year_pact=1,rel:npc_nalan_yanran:-10", [
        ("应对退婚", "在大厅冲突中维护萧家尊严。", "reputation>=5", "rel:npc_xiao_zhan:+5"),
        ("立下三年之约", "公开承担未来决战的责任。", "level>=3", "flag:three_year_pact=1,reputation:+5"),
    ]),
    _story_phase("ring_awakening", "戒中导师", "退婚风波后，戒中的神秘灵魂终于现身。", "建立师徒关系并获得成长道路。", "无法取得信任会失去关键指导。", 3, "soul>=6,flag:three_year_pact=1", "flag:ring_awakened=1,rel:npc_yao_lao:+10,douqi:+5", [
        ("药老现身", "确认斗气流失的真正原因。", "soul>=6", "flag:ring_awakened=1"),
        ("学习炼药与焚决", "建立师徒信任并选择成长路线。", "adventure_points>=3", "rel:npc_yao_lao:+10,alchemy:+3"),
    ]),
    _story_phase("wutan_growth", "乌坦城成长", "离开家族前，你需要功法、资金与实战经验。", "解决坊市冲突并完成离家准备。", "基础不足会使后续历练举步维艰。", 4, "level>=4", "flag:left_wutan=1,reputation:+5", [
        ("经营坊市资源", "通过炼药、交易或探索筹集资源。", "silver>=20", "alchemy:+2"),
        ("解决家族冲突", "保护萧家利益并赢得成人认可。", "training_wins>=2", "reputation:+5"),
        ("告别家族", "准备独自踏上历练之路。", "adventure_points>=5", "flag:left_wutan=1"),
    ]),
    _story_phase("mountain_training", "魔兽山脉历练", "魔兽山脉中有药材、强敌与新的伙伴。", "完成独立生存训练并穿越山脉。", "缺乏实战会无法深入沙漠。", 5, "level>=6,flag:left_wutan=1", "rel:npc_xiao_yixian:+10,exp:+50", [
        ("青山镇立足", "建立补给点并了解山脉情报。", "adventure_points>=6", "reputation:+3"),
        ("结识小医仙", "共同探索遗迹并建立信任。", "reputation>=10", "rel:npc_xiao_yixian:+10"),
        ("面对厄难毒体", "帮助伙伴控制危险体质。", "rel:npc_xiao_yixian>=35", "flag:poison_companion=1"),
    ]),
    _story_phase("desert_flame", "塔戈尔沙漠与青莲地心火", "异火线索指向蛇人族领地。", "深入沙漠并夺取青莲地心火。", "异火争夺失败会严重拖慢成长。", 6, "level>=10", "item:+item_green_lotus_flame,rel:npc_cai_lin:+15,douqi:+20", [
        ("保护青鳞", "解决石漠城危机并保护青鳞。", "reputation>=10", "rel:npc_qing_lin:+10"),
        ("寻找青莲地心火", "追踪地穴中的异火线索。", "soul>=12", "flag:green_lotus_found=1"),
        ("美杜莎神殿争夺", "在多方冲突中取得异火并保留转圜余地。", "level>=10,rel:npc_cai_lin>=-40", "rel:npc_cai_lin:+10"),
    ]),
    _story_phase("alchemy_conference", "炼药师大会", "返回加玛帝国后，炼药师大会成为积累声望的关键机会。", "通过考核、解决丹王势力威胁并夺得大会认可。", "失败会失去帝都盟友与公开声望。", 7, "alchemy>=12,soul>=12", "reputation:+10,alchemy:+5,item:+item_elixir", [
        ("取得炼药师资格", "通过公会测试并获得参赛身份。", "alchemy>=10", "reputation:+3"),
        ("处理纳兰家烙毒", "以异火与炼药能力换取关键人脉。", "soul>=12", "reputation:+4"),
        ("赢得炼药师大会", "在大会决赛中挫败敌对炼药师。", "alchemy>=12", "alchemy:+5,reputation:+8"),
    ]),
    _story_phase("yunlan_duel", "三年之约决战", "约定期限已至，你必须登上云岚宗。", "击败纳兰嫣然并从宗门追击中脱身。", "失败会让三年努力失去意义。", 8, "level>=15,flag:three_year_pact=1", "flag:rival_resolved=1,flag:yunlan_hostile=1,reputation:+20", [
        ("登上云岚宗", "突破宗门压力并抵达决战场。", "level>=15", "reputation:+5"),
        ("击败纳兰嫣然", "兑现三年之约。", "flag:three_year_pact=1", "rel:npc_nalan_yanran:+20,reputation:+10"),
        ("再上云岚宗击杀云棱", "处理萧家遇袭的直接责任人。", "reputation>=20", "flag:yunleng_defeated=1"),
        ("逃离加玛帝国", "在云山追击下保全自己并前往黑角域。", "soul>=15", "flag:first_yunlan_escape=1"),
    ]),
    _story_phase("canaan_outer", "迦南学院外院", "离开加玛帝国后，你终于前往迦南学院。", "完成入院与外院成长，为进入内院做准备。", "无法进入内院会错失核心修炼资源。", 9, "level>=18", "flag:joined_canaan=1,reputation:+8", [
        ("穿越黑角域", "通过黑域大平原与拍卖争夺抵达学院。", "adventure_points>=10,flag:first_yunlan_escape=1", "flag:first_black_corner_crossing=1"),
        ("抵达迦南学院", "完成迟到后的入院考验。", "level>=18", "flag:joined_canaan=1"),
        ("建立新生队伍", "与同伴形成可靠的小队。", "reputation>=25", "reputation:+5"),
        ("通过内院选拔赛", "赢得进入内院的资格。", "training_wins>=3", "flag:entered_inner_academy=1"),
    ]),
    _story_phase("canaan_inner", "内院磐门与强榜", "内院资源竞争激烈，新生必须抱团立足。", "建立磐门并在强榜大赛中取得资格。", "没有自己的势力将持续受到压制。", 10, "flag:entered_inner_academy=1,reputation>=25", "flag:pan_gate_founded=1,reputation:+10", [
        ("建立磐门", "团结新生并建立稳定据点。", "reputation>=25", "flag:pan_gate_founded=1"),
        ("结识紫研", "通过内院任务与紫研建立信任。", "adventure_points>=12", "rel:npc_ziyan:+10"),
        ("挑战强榜大赛", "取得进入天焚炼气塔核心区域的资格。", "training_wins>=4", "flag:strong_rank_won=1"),
    ]),
    _story_phase("fallen_heart", "炼气塔暴动与黑盟入侵", "强榜大赛后，陨落心炎冲破封印，韩枫也趁乱召集黑盟进攻内院。", "协助学院抵挡黑盟，并在封印崩溃时直面陨落心炎。", "黑盟与异火同时失控会彻底摧毁内院。", 11, "level>=25,flag:strong_rank_won=1", "flag:xiao_yan_trapped_in_tower=1,flag:han_feng_hostile=1,reputation:+10", [
        ("调查炼气塔异动", "确认陨落心炎暴动征兆。", "soul>=20", "flag:fallen_heart_unstable=1"),
        ("进入塔底修炼", "在封印彻底崩溃前进入塔底。", "level>=25", "exp:+80"),
        ("黑盟趁乱入侵", "协助苏千与内院长老抵挡韩枫和黑盟。", "reputation>=35,flag:fallen_heart_unstable=1", "flag:black_alliance_invaded=1"),
        ("被陨落心炎吞入塔底", "在混战与封印崩溃中跌入岩浆世界。", "flag:black_alliance_invaded=1", "flag:xiao_yan_trapped_in_tower=1"),
    ]),
    _story_phase("black_corner_war", "收服陨落心炎与清算韩枫", "被困塔底两年后，你必须炼化陨落心炎、破塔归来，并清算韩枫与黑盟。", "带着异火重返内院，反攻枫城并摧毁韩枫肉身。", "若无法脱困，内院和萧门都将长期承受黑盟威胁。", 12, "level>=28,flag:xiao_yan_trapped_in_tower=1", "flag:han_feng_escaped=1,flag:soul_hall_exposed=1,reputation:+15,douqi:+30", [
        ("炼化陨落心炎", "在岩浆世界承受异火炼体并完成融合。", "soul>=25,flag:fallen_heart_unstable=1", "item:+item_fallen_heart_flame"),
        ("破塔重返内院", "结束两年闭关，返回内院与萧门。", "item:item_fallen_heart_flame", "flag:return_from_tower=1,reputation:+5"),
        ("反攻枫城击溃韩枫", "联合学院强者摧毁韩枫肉身。", "level>=28,flag:han_feng_hostile=1", "flag:han_feng_body_destroyed=1"),
        ("发现魂殿接应", "确认韩枫灵魂被魂殿救走。", "soul>=25,flag:han_feng_body_destroyed=1", "flag:han_feng_escaped=1,flag:soul_hall_exposed=1"),
    ]),
    _story_phase("yunlan_war", "重返加玛与云岚宗大战", "父亲失踪、萧家遭难，线索指向云岚宗与魂殿。", "救援萧家、击败云山并重建故土秩序。", "拖延会让萧家与盟友被逐个击破。", 13, "level>=30,flag:first_yunlan_escape=1", "flag:yan_alliance_founded=1,reputation:+20", [
        ("追查父亲失踪", "确认萧家危机与魂殿介入。", "reputation>=35", "flag:xiao_family_crisis=1"),
        ("击败云山，药老被掳", "终结云岚宗威胁，但魂殿护法趁乱掳走药老。", "level>=30,flag:yunlan_hostile=1", "flag:yunlan_defeated=1,flag:yao_lao_captured=1"),
        ("建立炎盟", "联合加玛帝国盟友保护萧家。", "reputation>=45", "flag:yan_alliance_founded=1"),
    ]),
    _story_phase("poison_sect_war", "出云帝国与毒宗之战", "炎盟刚刚建立，毒宗、金雁宗与慕兰谷便入侵加玛帝国。", "守住炎盟、重逢小医仙并解决厄难毒体危机。", "联盟初战失败会让故土再次陷入战乱。", 14, "level>=33,flag:yan_alliance_founded=1", "flag:northwest_stabilized=1,rel:npc_xiao_yixian:+15,reputation:+15", [
        ("守卫加玛帝国", "带领炎盟击退三宗联军。", "reputation>=50", "flag:yan_alliance_defended=1"),
        ("重逢毒宗宗主", "确认小医仙身份并避免双方死战。", "rel:npc_xiao_yixian>=40", "rel:npc_xiao_yixian:+10"),
        ("暂时封印厄难毒体", "寻找毒丹之法，暂时压制小医仙的毒体。", "alchemy>=20,flag:poison_companion=1", "flag:poison_body_sealed=1"),
    ]),
    _story_phase("return_black_corner", "重返黑角域", "魂殿线索与韩枫逃亡方向都指向黑角域。", "清算魔炎谷、擒获韩枫并取得前往中州的线索。", "缺少魂殿情报便无法继续追查药老。", 15, "level>=35,flag:han_feng_escaped=1", "flag:han_feng_captured=1,flag:mentor_prison_known=1,reputation:+15", [
        ("清算魔炎谷", "摧毁黑角域中敌对势力的核心据点。", "reputation>=55", "flag:demon_flame_valley_defeated=1"),
        ("擒获韩枫灵魂", "击败韩枫与魂殿接应者。", "level>=35,flag:han_feng_escaped=1", "flag:han_feng_captured=1"),
        ("取得药老去向线索", "从韩枫与魂殿护法处确认药老被带往中州。", "soul>=30", "flag:mentor_prison_known=1"),
    ]),
    _story_phase("revisit_tower", "再探塔底与天火尊者", "黑角域清算后，炼气塔底的岩浆世界仍隐藏着第二朵心炎、火焰蜥蜴人与神秘存在。", "再入塔底、救出天火尊者并记录古帝玉的异常反应。", "忽略塔底异动会让后续追查古帝洞府时失去重要参照。", 16, "level>=36,flag:han_feng_captured=1", "flag:magma_depths_sensed=1,reputation:+8", [
        ("返回迦南学院", "安置萧门与磐门并准备再入塔底。", "reputation>=58", "reputation:+3"),
        ("救出天火尊者", "深入岩浆世界并帮助残魂脱困。", "soul>=32", "flag:tianhuo_rescued=1"),
        ("记录古帝玉异动", "面对岩浆深处的神秘存在，记录古帝玉的异常反应。", "flag:tianhuo_rescued=1", "flag:magma_depths_sensed=1"),
    ]),
    _story_phase("zhongzhou_arrival", "进入中州", "药老被魂殿掳走，新的线索指向强者云集的中州。", "在中州立足、寻找星陨阁并追查魂殿。", "没有据点与情报便无法展开营救。", 16, "level>=36,flag:mentor_prison_known=1", "flag:star_pavilion_found=1,reputation:+15", [
        ("穿越空间虫洞", "经历空间风暴后抵达中州，并随韩家车队前往天北城。", "level>=35", "flag:han_family_helped=1,exp:+100"),
        ("解决天北城冲突", "帮助韩家抵挡洪家与风雷北阁追杀。", "flag:han_family_helped=1", "flag:tianbei_conflict_resolved=1,reputation:+5"),
        ("进入天目山血潭", "穿过鼠潮音波阵并借血潭完成突破。", "flag:tianbei_conflict_resolved=1", "flag:tianmu_blood_pool_crossed=1,douqi:+10"),
        ("四方阁大会立威", "在大会中击败王尘并与风尊者建立联系。", "training_wins>=5,flag:tianmu_blood_pool_crossed=1", "reputation:+10"),
        ("找到风尊者与星陨阁", "联系药老旧友并建立营救据点。", "reputation>=50", "flag:star_pavilion_found=1,rel:npc_feng_zunzhe:+15"),
    ]),
    _story_phase("ye_ice_valley", "叶城与冰河谷", "中州丹塔选拔将近，小医仙的厄难毒体也引来冰河谷追杀。", "帮助叶家取得资格，并彻底解决厄难毒体。", "毒体失控会危及小医仙与周围所有人。", 17, "level>=38,flag:poison_body_sealed=1", "flag:poison_body_resolved=1,reputation:+12", [
        ("帮助叶家通过考核", "取得参加丹会的正式资格。", "alchemy>=28", "flag:dan_meeting_qualified=1"),
        ("迎战冰河谷", "保护小医仙并击退冰河谷追兵。", "level>=38,rel:npc_xiao_yixian>=50", "reputation:+5"),
        ("凝聚毒丹", "彻底控制厄难毒体而非继续封印。", "alchemy>=30,flag:poison_body_sealed=1", "flag:poison_body_resolved=1"),
    ]),
    _story_phase("dan_meeting_flame", "丹会与三千焱炎火", "丹塔大会能提供声望、盟友与接近三千焱炎火的机会。", "赢得丹会并收服星域异火。", "失败会失去营救药老的重要支援。", 18, "level>=40,alchemy>=30,soul>=30,flag:dan_meeting_qualified=1", "alchemy:+15,reputation:+20", [
        ("通过丹会选拔", "证明炼药与灵魂能力。", "alchemy>=30,soul>=30", "reputation:+10"),
        ("赢得丹会", "在顶尖炼药师竞争中夺得名次。", "alchemy>=35", "flag:dan_meeting_won=1"),
        ("进入星域收服异火", "处理魂殿干扰并取得三千焱炎火。", "level>=40,flag:dan_meeting_won=1", "item:+item_three_thousand_flame"),
    ]),
    _story_phase("save_mentor", "营救药老", "魂殿囚禁着药老，营救时机终于成熟。", "突袭亡魂山脉并救回药老灵魂。", "失败将失去导师和对抗魂殿的核心盟友。", 19, "level>=45,flag:star_pavilion_found=1,rel:npc_yao_lao>=60", "flag:yao_lao_rescued=1,rel:npc_yao_lao:+20,reputation:+20", [
        ("突袭魂殿分殿", "依靠丹塔与星陨阁情报展开营救。", "reputation>=60", "flag:yao_lao_rescued=1"),
        ("撤回星陨阁", "保护重伤的药老灵魂撤离。", "soul>=40,flag:yao_lao_rescued=1", "flag:mentor_soul_secured=1"),
        ("准备复活材料", "确认重塑躯体仍缺少斗圣骸骨。", "alchemy>=40", "flag:saint_bones_needed=1"),
    ]),
    _story_phase("ancient_ruins", "远古遗迹", "远古遗迹现世，其中的斗圣骸骨是复活药老的关键。", "探索遗迹、取得龙凰本源果与斗圣骸骨。", "无法取得骸骨便不能为药老重塑躯体。", 20, "level>=48,soul>=35,flag:saint_bones_needed=1", "soul:+10", [
        ("定位遗迹入口", "识别空间波动并准备探索队伍。", "soul>=35", "exp:+50"),
        ("重逢青鳞", "在遗迹中与青鳞会合并应对远古天蛇力量。", "rel:npc_qing_lin>=35", "rel:npc_qing_lin:+10"),
        ("取得龙凰本源果", "为紫研后续的龙皇血脉觉醒准备机缘。", "level>=48", "flag:dragon_phoenix_fruit_acquired=1"),
        ("夺取斗圣骸骨", "击退争夺者并带回重塑躯体的核心材料。", "reputation>=70", "item:+item_earth_skill,flag:saint_bones_acquired=1"),
    ]),
    _story_phase("revive_mentor", "复活药老", "斗圣骨骸已经到手，可以为药老重塑躯体。", "炼制新躯体并让药老完成灵魂融合。", "拖延会让魂殿再次找到虚弱的药老灵魂。", 21, "alchemy>=42,flag:saint_bones_acquired=1,flag:mentor_soul_secured=1", "flag:yao_lao_revived=1,reputation:+20", [
        ("炼制斗圣躯体", "使用斗圣骸骨与异火完成躯体炼制。", "alchemy>=42,flag:saint_bones_acquired=1", "flag:saint_body_refined=1"),
        ("药老复活", "让药老灵魂与新躯体完成融合。", "soul>=45,flag:saint_body_refined=1", "flag:yao_lao_revived=1,rel:npc_yao_lao:+15"),
    ]),
    _story_phase("flower_sect", "花宗与云韵传承", "药老复活后，花宗传承纷争将云韵卷入危机，也影响中州盟友格局。", "帮助云韵取得花宗传承并争取花宗支持。", "花宗落入敌对势力会削弱未来联盟。", 22, "level>=50,flag:yao_lao_revived=1", "flag:flower_sect_allied=1,rel:npc_yun_yun:+15,reputation:+10", [
        ("赶往花宗", "响应云韵求援并查明宗主传承争议。", "reputation>=75", "rel:npc_yun_yun:+5"),
        ("击败花宗敌手", "保护云韵完成传承。", "level>=50", "exp:+120"),
        ("争取花宗支持", "让花宗成为星陨阁的盟友。", "rel:npc_yun_yun>=30", "flag:flower_sect_allied=1"),
    ]),
    _story_phase("dragon_island_legacy", "龙岛与龙皇血脉", "龙凰本源果被送往分裂的古龙岛，紫研需要完成血脉觉醒。", "帮助紫研觉醒龙皇血脉并稳住东龙岛。", "紫研失败会让太虚古龙族继续分裂。", 23, "level>=50,rel:npc_ziyan>=35,flag:dragon_phoenix_fruit_acquired=1", "flag:dragon_emperor_awakened=1,rel:npc_ziyan:+15,reputation:+10", [
        ("抵达东龙岛", "穿越虚空并确认古龙族分裂局势。", "soul>=40", "flag:east_dragon_island_reached=1"),
        ("守护龙凰晶层", "在三岛压力下保护紫研完成炼化。", "level>=50", "rel:npc_ziyan:+10"),
        ("见证龙皇觉醒", "帮助紫研继承龙皇血脉。", "rel:npc_ziyan>=40", "flag:dragon_emperor_awakened=1"),
    ]),
    _story_phase("gu_clan_tomb", "古族成人礼与天墓", "古族成人礼与天墓开启提供了接触萧族先祖的机会。", "赢得古族认可、获得萧玄传承，并强化星陨阁。", "失败会削弱古族联盟与血脉成长。", 24, "level>=52,rel:npc_xun_er>=60", "rel:npc_gu_yuan:+20,douqi:+50", [
        ("参加古族成人礼", "在远古种族面前证明实力。", "reputation>=75", "rel:npc_gu_yuan:+10"),
        ("进入天墓", "与同伴穿越能量风暴。", "level>=50", "exp:+150"),
        ("接受萧玄传承", "恢复萧族血脉并理解先祖使命。", "soul>=45", "flag:xiao_bloodline_awakened=1,douqi:+30"),
        ("回归并强化星陨阁", "结束天墓修炼后，将星陨阁建设为更可靠的长期据点。", "flag:xiao_bloodline_awakened=1", "flag:star_pavilion_rebuilt=1,reputation:+10"),
    ]),
    _story_phase("northwest_fortress_war", "玄黄要塞与西北大陆大战", "魂殿联军进攻西北大陆，炎盟与萧家在玄黄要塞陷入苦战。", "返回故土、守住要塞并稳定西北联盟。", "故土失守会让天府联盟失去根基。", 25, "level>=54,flag:yan_alliance_founded=1", "flag:northwest_front_secured=1,reputation:+18", [
        ("赶回玄黄要塞", "响应炎盟求援并集结故土盟友。", "reputation>=82", "flag:northwest_reinforced=1"),
        ("守卫萧家与炎盟", "击退魂殿联军对西北大陆的进攻。", "level>=54", "reputation:+10"),
        ("稳定西北战线", "重新整合加玛、出云与蛇人族力量。", "flag:northwest_stabilized=1", "flag:northwest_front_secured=1"),
    ]),
    _story_phase("bodhi_tree", "莽荒古域与菩提古树", "菩提古树现世，进入莽荒古域还需面对兽潮与各方争夺。", "穿越莽荒古域、突破幻境并取得菩提心。", "心境不足会永远迷失。", 25, "level>=55,soul>=45", "soul:+20", [
        ("穿越莽荒古域兽潮", "与盟友突破古域入口和兽潮阻拦。", "reputation>=80", "exp:+100"),
        ("争夺古树入口", "与各方势力竞争进入资格。", "reputation>=80", "exp:+100"),
        ("突破菩提幻境", "分辨幻象并保持自我。", "soul>=45", "soul:+10"),
        ("取得菩提心", "吸收古树核心机缘并完成境界突破。", "level>=55", "item:+item_bodhi_heart,item:+item_bodhi_seed"),
    ]),
    _story_phase("tianfu_alliance", "建立天府联盟", "魂殿全面施压，单一势力已无法抵抗。", "联合星陨阁、丹塔、炎盟与伙伴势力。", "联盟失败会让各方被逐个击破。", 26, "flag:star_pavilion_rebuilt=1,flag:yan_alliance_founded=1,reputation>=90", "flag:tianfu_alliance_founded=1,reputation:+20", [
        ("调查灵族消失", "确认远古种族正在遭受魂族秘密袭击。", "soul>=50", "flag:ancient_clan_disappearances=1"),
        ("整合星陨阁与炎盟", "统一两地情报与资源网络。", "reputation>=90", "reputation:+5"),
        ("争取丹塔与伙伴势力", "让中州盟友加入共同防线。", "alchemy>=45,rel:npc_ziyan>=35", "reputation:+10"),
        ("建立天府联盟", "形成能够正面对抗魂殿的联盟。", "flag:star_pavilion_rebuilt=1", "flag:tianfu_alliance_founded=1"),
    ]),
    _story_phase("nether_spring", "九幽黄泉与妖暝", "建立天府联盟后，需要争取九幽地冥蟒族并强化彩鳞血脉。", "救出妖暝、取得妖圣精血并争取魔兽盟友。", "缺少魔兽盟友会让联盟侧翼空虚。", 27, "level>=58,flag:tianfu_alliance_founded=1", "flag:nether_python_allied=1,rel:npc_cai_lin:+15,reputation:+10", [
        ("深入九幽黄泉", "帮助彩鳞寻找血脉突破机缘。", "rel:npc_cai_lin>=20", "rel:npc_cai_lin:+10"),
        ("救出妖暝", "推翻九幽地冥蟒族中的篡位者。", "level>=58", "flag:yaoming_restored=1"),
        ("争取魔兽盟友", "让九幽地冥蟒族加入天府联盟。", "flag:yaoming_restored=1", "flag:nether_python_allied=1"),
    ]),
    _story_phase("dragon_island_war", "古龙岛三岛大战", "三大龙王拒绝承认紫研，古龙族战争爆发。", "帮助紫研击败三岛联军，但北龙王趁乱逃脱。", "北龙王仍会成为后续隐患。", 28, "level>=60,flag:dragon_emperor_awakened=1", "flag:north_dragon_escaped=1,rel:npc_ziyan:+15,reputation:+15", [
        ("重返古龙岛", "响应紫研求援并集结东龙岛力量。", "rel:npc_ziyan>=45", "reputation:+5"),
        ("迎战三大龙王", "打破三岛联军并保护紫研。", "level>=60", "exp:+200"),
        ("北龙王逃脱", "结束三岛大战并追踪北龙王去向。", "flag:dragon_emperor_awakened=1", "flag:north_dragon_escaped=1"),
    ]),
    _story_phase("soul_hall_war", "血洗魂殿人殿", "天府联盟成立后，双方开始争夺中州主动权。", "摧毁魂殿核心分殿并夺回灵魂本源。", "若魂殿仍掌握灵魂本源，联盟将持续受制。", 29, "level>=62,flag:tianfu_alliance_founded=1", "flag:soul_hall_weakened=1,soul:+15,reputation:+20", [
        ("血洗魂殿人殿", "摧毁魂殿灵魂收集据点。", "reputation>=105", "flag:soul_hall_core_exposed=1"),
        ("夺回灵魂本源", "释放被囚灵魂并强化自身灵魂境界。", "soul>=55,flag:soul_hall_core_exposed=1", "soul:+15"),
        ("逼退魂殿殿主", "迫使魂殿收缩，但殿主仍未被彻底击败。", "level>=62", "flag:soul_hall_weakened=1"),
    ]),
    _story_phase("demon_flame", "净莲妖火", "残图汇聚，净莲妖火空间开启。", "突破妖火幻境并完成收服。", "失败会被妖火控制。", 30, "level>=64,soul>=55,flag:soul_hall_weakened=1", "douqi:+80", [
        ("集齐妖火残图", "借助联盟情报定位妖火空间。", "soul>=50", "flag:demon_flame_map=1"),
        ("突破妖火幻境", "抵抗净莲妖圣留下的幻境。", "soul>=55", "soul:+10"),
        ("收服净莲妖火", "与盟友共同压制妖火本体。", "level>=60", "item:+item_purifying_demon_flame"),
    ]),
    _story_phase("post_demon_wars", "魂殿殿主与北龙王终战", "净莲妖火之后，魂殿殿主与逃亡的北龙王先后发动反扑。", "击败两名强敌并完成古龙族统一。", "残余强敌会破坏大陆联盟。", 31, "level>=66,flag:north_dragon_escaped=1,flag:soul_hall_weakened=1", "flag:soul_hall_defeated=1,flag:dragon_clan_unified=1,reputation:+20", [
        ("击败魂殿殿主", "终结魂殿在中州的公开统治。", "level>=66,flag:soul_hall_weakened=1", "flag:soul_hall_defeated=1"),
        ("追击北龙王", "阻止北龙王利用化龙魔阵反扑。", "rel:npc_ziyan>=50,flag:north_dragon_escaped=1", "exp:+200"),
        ("统一太虚古龙族", "彻底结束古龙族分裂。", "flag:north_dragon_escaped=1", "flag:dragon_clan_unified=1"),
    ]),
    _story_phase("medicine_ceremony", "药典与药族灭族战", "药族举办药典，魂族随后发动灭族袭击。", "通过药典、救援药族幸存者并确认魂族计划。", "药族覆灭会让魂族夺得更多血脉与帝玉。", 32, "alchemy>=50,soul>=55", "alchemy:+20,flag:medicine_clan_survivors_saved=1,reputation:+20", [
        ("完成药典考验", "展现高阶炼药与灵魂控制。", "alchemy>=50,soul>=55", "alchemy:+10"),
        ("应对药族灭族战", "在魂族袭击中保护药族幸存者。", "level>=65", "flag:hun_clan_hostile=1"),
        ("救出药族幸存者", "将幸存力量带回联盟并保存药族传承。", "reputation>=110", "flag:medicine_clan_survivors_saved=1"),
    ]),
    _story_phase("ancient_clan_war", "远古种族联盟战", "魂族开始夺取各族帝玉，远古种族面临覆灭。", "协调古族、古龙族与盟友，并救回被囚的父亲。", "联盟破裂会让魂族打开古帝洞府。", 33, "flag:dragon_clan_unified=1,flag:hun_clan_hostile=1", "flag:ancient_alliance=1,rel:npc_xiao_zhan:+20,reputation:+25", [
        ("确认魂族夺玉计划", "整合药族幸存者与古族情报。", "flag:medicine_clan_survivors_saved=1", "flag:emperor_jade_crisis=1"),
        ("再入天墓", "借助萧玄残魂将灵魂境界提升至帝境。", "flag:xiao_bloodline_awakened=1,soul>=65", "flag:emperor_soul_awakened=1,soul:+20"),
        ("营救萧战", "在魂族大战中救回被囚多年的父亲。", "flag:xiao_family_crisis=1,level>=68", "flag:xiao_zhan_rescued=1,rel:npc_xiao_zhan:+20"),
        ("协调远古种族盟友", "争取古族与统一后的太虚古龙族共同作战。", "rel:npc_gu_yuan>=30,flag:dragon_clan_unified=1", "flag:ancient_alliance=1"),
    ]),
    _story_phase("ancient_emperor", "古帝洞府", "魂族集齐八块陀舍古帝玉并打开洞府，成帝传承成为最后争夺。", "追入洞府，争夺帝品雏丹并取得迎战魂天帝的传承。", "失败会让魂天帝独占成帝契机。", 34, "level>=70,flag:ancient_alliance=1", "flag:emperor_cave_contested=1", [
        ("追入古帝洞府", "在魂族使用八玉打开洞府后，集结联盟追入洞府空间。", "flag:ancient_alliance=1", "flag:emperor_cave_opened=1"),
        ("争夺帝品雏丹", "阻止魂族夺取成帝关键。", "level>=70,flag:emperor_cave_opened=1", "flag:embryonic_pill_contested=1,douqi:+50"),
        ("魂天帝夺丹成帝", "争夺失败后，应对魂天帝完成突破的危机。", "level>=72,flag:embryonic_pill_contested=1", "flag:soul_emperor_ascended=1"),
        ("接受古帝传承", "在魂天帝成帝后，获得迎战他的最后力量。", "flag:emperor_soul_awakened=1,flag:soul_emperor_ascended=1", "flag:emperor_legacy=1,douqi:+100"),
    ]),
    _story_phase("final_war", "双帝之战", "魂天帝突破，大陆已无退路。", "集结联军并完成最终决战。", "失败意味着大陆秩序覆灭。", 35, "level>=80,flag:emperor_legacy=1", "flag:soul_emperor_defeated=1,reputation:+100", [
        ("集结大陆联军", "让所有盟友进入最终战场。", "reputation>=120,flag:ancient_alliance=1", "reputation:+20"),
        ("突破斗帝", "以古帝传承与异火完成最终突破。", "level>=80,flag:emperor_legacy=1", "flag:xiao_emperor_awakened=1"),
        ("迎战魂天帝", "封印魂天帝并终结魂族战争。", "flag:xiao_emperor_awakened=1", "flag:soul_emperor_defeated=1"),
    ]),
    _story_phase("five_emperors", "五帝破空", "双帝之战数十年后，萧炎开启源气通道，斗气大陆再次出现五位斗帝。", "安排大陆后事，并与薰儿、彩鳞、古元和烛坤前往新的位面。", "未知位面远比斗气大陆危险，必须在出发前完成交接。", 36, "flag:soul_emperor_defeated=1", "flag:story_finished=1", [
        ("开启源气通道", "引来源气，让斗气大陆重新拥有晋升斗帝的可能。", "flag:xiao_emperor_awakened=1", "flag:source_qi_channel_opened=1"),
        ("见证五帝并立", "等待薰儿、彩鳞、古元与烛坤完成突破。", "flag:source_qi_channel_opened=1", "flag:five_emperors_gathered=1"),
        ("安排大陆后事", "将萧族、古族、太虚古龙族与天府联盟交给可靠的后来者。", "reputation>=150,flag:five_emperors_gathered=1", "reputation:+20"),
        ("五帝破空", "五位斗帝一同前往新的位面。", "flag:ancient_alliance=1,flag:five_emperors_gathered=1", "flag:story_finished=1"),
    ]),
]


# 工作簿里程碑必须映射到真实节点，并按实际剧情先后排列。
PLOT_MILESTONE_SEQUENCE = [
    "退婚", "三年之约", "青莲地心火争夺", "炼药师大会", "内院选拔赛",
    "强榜大赛", "黑角域大战", "陨落心炎与天焚炼气塔", "云岚宗大战",
    "丹会", "三千焱炎火", "营救药老", "远古遗迹", "古族成人礼",
    "天墓与萧玄", "菩提古树", "净莲妖火", "药典", "古帝洞府",
    "双帝之战", "五帝破空",
]

PLOT_MILESTONE_COVERAGE = {
    "退婚": ("退婚与三年之约", "应对退婚"),
    "三年之约": ("退婚与三年之约", "立下三年之约"),
    "青莲地心火争夺": ("塔戈尔沙漠与青莲地心火", "美杜莎神殿争夺"),
    "炼药师大会": ("炼药师大会", "赢得炼药师大会"),
    "内院选拔赛": ("迦南学院外院", "通过内院选拔赛"),
    "强榜大赛": ("内院磐门与强榜", "挑战强榜大赛"),
    "黑角域大战": ("炼气塔暴动与黑盟入侵", "黑盟趁乱入侵"),
    "陨落心炎与天焚炼气塔": ("收服陨落心炎与清算韩枫", "炼化陨落心炎"),
    "云岚宗大战": ("重返加玛与云岚宗大战", "击败云山，药老被掳"),
    "丹会": ("丹会与三千焱炎火", "赢得丹会"),
    "三千焱炎火": ("丹会与三千焱炎火", "进入星域收服异火"),
    "营救药老": ("营救药老", "突袭魂殿分殿"),
    "远古遗迹": ("远古遗迹", "夺取斗圣骸骨"),
    "古族成人礼": ("古族成人礼与天墓", "参加古族成人礼"),
    "天墓与萧玄": ("古族成人礼与天墓", "接受萧玄传承"),
    "菩提古树": ("莽荒古域与菩提古树", "取得菩提心"),
    "净莲妖火": ("净莲妖火", "收服净莲妖火"),
    "药典": ("药典与药族灭族战", "完成药典考验"),
    "古帝洞府": ("古帝洞府", "追入古帝洞府"),
    "双帝之战": ("双帝之战", "迎战魂天帝"),
    "五帝破空": ("五帝破空", "五帝破空"),
}

# 不属于工作簿 21 个里程碑名称，但对剧情因果闭环不可省略的桥梁。
CRITICAL_BRIDGE_COVERAGE = {
    "药老被魂殿掳走": ("重返加玛与云岚宗大战", "击败云山，药老被掳"),
    "出云帝国战争": ("出云帝国与毒宗之战", "守卫加玛帝国"),
    "厄难毒体稳定": ("叶城与冰河谷", "凝聚毒丹"),
    "紫研觉醒龙皇血脉": ("龙岛与龙皇血脉", "见证龙皇觉醒"),
    "太虚古龙统一": ("魂殿殿主与北龙王终战", "统一太虚古龙族"),
    "魂殿决战": ("魂殿殿主与北龙王终战", "击败魂殿殿主"),
    "药族灭族战": ("药典与药族灭族战", "应对药族灭族战"),
    "营救萧战": ("远古种族联盟战", "营救萧战"),
    "获得菩提心": ("莽荒古域与菩提古树", "取得菩提心"),
    "重返黑角域": ("重返黑角域", "擒获韩枫灵魂"),
    "叶城与冰河谷": ("叶城与冰河谷", "迎战冰河谷"),
    "药老复活": ("复活药老", "药老复活"),
    "花宗传承": ("花宗与云韵传承", "争取花宗支持"),
    "九幽黄泉": ("九幽黄泉与妖暝", "救出妖暝"),
    "首次穿越黑角域": ("迦南学院外院", "穿越黑角域"),
    "再探天焚炼气塔": ("再探塔底与天火尊者", "记录古帝玉异动"),
    "中州韩家与天北城": ("进入中州", "解决天北城冲突"),
    "天目山血潭": ("进入中州", "进入天目山血潭"),
    "星陨阁强化": ("古族成人礼与天墓", "回归并强化星陨阁"),
    "源气通道": ("五帝破空", "开启源气通道"),
    "玄黄要塞大战": ("玄黄要塞与西北大陆大战", "守卫萧家与炎盟"),
    "灵族消失": ("建立天府联盟", "调查灵族消失"),
    "再入天墓帝境灵魂": ("远古种族联盟战", "再入天墓"),
    "魂天帝夺丹成帝": ("古帝洞府", "魂天帝夺丹成帝"),
}

# 取自章节索引的实际发生位置，用于防止中段剧情再次错位。
STORY_CHAPTER_ANCHORS = {
    "yunlan_duel": 329,
    "canaan_outer": 378,
    "fallen_heart": 582,
    "black_corner_war": 614,
    "yunlan_war": 668,
    "poison_sect_war": 735,
    "return_black_corner": 811,
    "revisit_tower": 896,
    "zhongzhou_arrival": 941,
    "ye_ice_valley": 1052,
    "dan_meeting_flame": 1220,
    "save_mentor": 1310,
    "ancient_ruins": 1378,
    "revive_mentor": 1439,
    "flower_sect": 1447,
    "dragon_island_legacy": 1461,
    "gu_clan_tomb": 1473,
    "northwest_fortress_war": 1566,
    "bodhi_tree": 1597,
    "tianfu_alliance": 1665,
    "nether_spring": 1692,
    "dragon_island_war": 1721,
    "soul_hall_war": 1737,
    "demon_flame": 1750,
    "post_demon_wars": 1778,
    "medicine_ceremony": 1815,
    "ancient_clan_war": 1838,
    "ancient_emperor": 1870,
    "final_war": 1901,
    "five_emperors": 1904,
}

# 地图只随剧情开放。推荐等级仅用于提示危险，不参与解锁判断。
# ── 区域通行方式（与原文一致）──
# 加玛帝国 → 黑角域：远程陆行/飞行魔兽，穿越数个小国，耗时数月（无空间虫洞直达）
# 黑角域 → 中州：必须经天涯城空间虫洞（方圆千里唯一虫洞，罗家世代守护）
# 中州内部：各大城市间有空间虫洞连接，虫洞驿站维护
# 中州 → 龙岛/虚空：空间船或斗圣强者撕裂空间
# 中州 → 远古种族空间（古界/魂界/药界等）：特定空间通道/入口
# 特殊空间（妖火空间/古帝洞府等）：需特定条件/道具方能开启
# ── 区域归属（用于通行判断）──
REGION_MAP_GROUPS = {
    "加玛帝国": {"map_wutan", "map_jia_ma", "map_jia_ma_capital", "map_jia_ma_road",
                 "map_jia_ma_border", "map_jia_ma_garrison", "map_jia_ma_mountain_pass",
                 "map_jia_ma_post_station", "map_jia_ma_battle_front", "map_ghost_pass",
                 "map_black_rock_city", "map_salt_city", "map_magic_mountains",
                 "map_qingshan", "map_tager", "map_mo_city", "map_stone_mo_city",
                 "map_miteer_auction", "map_alchemist_guild", "map_yunlan",
                 "map_yan_alliance_hq"},
    "黑角域": {"map_black_corner", "map_canaan", "map_canaan_inner", "map_peace_town",
              "map_feng_city", "map_black_emperor_city", "map_black_seal_city",
              "map_demon_flame_valley", "map_skyfire_tower", "map_skyfire_magma_world",
              "map_emperor_cave"},
    "中州": {"map_zhongzhou", "map_tianbei_city", "map_ye_city",
            "map_wind_lightning_pavilion", "map_huangquan_pavilion",
            "map_wanjian_pavilion", "map_star_pavilion", "map_star_realm",
            "map_burning_flame_valley", "map_ice_river_valley",
            "map_dan_region", "map_sacred_dan_city", "map_dan_tower",
            "map_soul_mountains", "map_soul_hall", "map_soul_realm",
            "map_ancient_ruins", "map_beast_region", "map_wilderness",
            "map_bodhi_tree", "map_flower_sect", "map_ancient_realm",
            "map_heaven_tomb", "map_ancient_sacred_city", "map_space_trade_fair",
            "map_sky_demon_sect", "map_tianmu_mountains",
            "map_heaven_mountain_blood_pool", "map_death_corpse_mountains",
            "map_heavenly_gang_hall", "map_demon_flame_space",
            "map_demon_flame_plain", "map_yao_realm", "map_hun_clan_space",
            "map_strange_flame_square"},
    "虚空/龙岛": {"map_dragon_island", "map_east_dragon_island", "map_west_dragon_island",
                 "map_south_dragon_island", "map_north_dragon_island",
                 "map_ancient_dragon_island"},
    "西北大陆": {"map_chuyun_empire", "map_poison_sect", "map_golden_goose_sect",
                "map_mulan_valley", "map_scorpion_gate", "map_xuanhuang_fortress",
                "map_northwest_battle_front"},
    "最终战场": {"map_double_emperor", "map_world_gate", "map_emperor_memorial_peak"},
    "中转站": {"map_tianya_city"},  # 天涯城：连接黑角域与中州的虫洞枢纽
}
REGION_BY_MAP = {}
for _region, _map_ids in REGION_MAP_GROUPS.items():
    for _mid in _map_ids:
        REGION_BY_MAP[_mid] = _region

# 跨区通行需要经过的中转站
TRANSIT_HUBS = {
    ("黑角域", "中州"): "map_tianya_city",  # 原文：天涯城是方圆千里唯一通往中州的虫洞
    ("中州", "黑角域"): "map_tianya_city",  # 反向亦然
}
TRANSIT_HUB_NAMES = {
    "map_tianya_city": "天涯城（空间虫洞）",
}

MAP_STORY_UNLOCKS = {
    "map_wutan": "fallen_genius",
    "map_jia_ma": "fallen_genius",
    "map_miteer_auction": "wutan_growth",
    "map_magic_mountains": "mountain_training",
    "map_qingshan": "mountain_training",
    "map_tager": "desert_flame",
    "map_jia_ma_capital": "alchemy_conference",
    "map_alchemist_guild": "alchemy_conference",
    "map_yunlan": "yunlan_duel",
    "map_peace_town": "canaan_outer",
    "map_black_corner": "canaan_outer",
    "map_canaan": "canaan_outer",
    "map_canaan_inner": "canaan_inner",
    "map_skyfire_tower": "fallen_heart",
    "map_feng_city": "black_corner_war",
    "map_black_emperor_city": "return_black_corner",
    "map_zhongzhou": "zhongzhou_arrival",
    "map_tianbei_city": "zhongzhou_arrival",
    "map_wind_lightning_pavilion": "zhongzhou_arrival",
    "map_huangquan_pavilion": "zhongzhou_arrival",
    "map_wanjian_pavilion": "zhongzhou_arrival",
    "map_burning_flame_valley": "zhongzhou_arrival",
    "map_ye_city": "ye_ice_valley",
    "map_ice_river_valley": "ye_ice_valley",
    "map_dan_region": "dan_meeting_flame",
    "map_sacred_dan_city": "dan_meeting_flame",
    "map_dan_tower": "dan_meeting_flame",
    "map_soul_mountains": "save_mentor",
    "map_soul_hall": "save_mentor",
    "map_star_pavilion": "save_mentor",
    "map_star_realm": "revive_mentor",
    "map_ancient_ruins": "ancient_ruins",
    "map_beast_region": "ancient_ruins",
    "map_flower_sect": "flower_sect",
    "map_dragon_island": "dragon_island_legacy",
    "map_east_dragon_island": "dragon_island_legacy",
    "map_ancient_dragon_island": "dragon_island_legacy",
    "map_ancient_sacred_city": "gu_clan_tomb",
    "map_ancient_realm": "gu_clan_tomb",
    "map_heaven_tomb": "gu_clan_tomb",
    "map_wilderness": "bodhi_tree",
    "map_bodhi_tree": "bodhi_tree",
    "map_space_trade_fair": "bodhi_tree",
    "map_west_dragon_island": "dragon_island_war",
    "map_south_dragon_island": "dragon_island_war",
    "map_north_dragon_island": "dragon_island_war",
    "map_demon_flame_space": "demon_flame",
    "map_yao_realm": "medicine_ceremony",
    "map_soul_realm": "ancient_clan_war",
    "map_hun_clan_space": "ancient_clan_war",
    "map_emperor_cave": "ancient_emperor",
    "map_double_emperor": "final_war",
    # wutan_growth: 加玛帝国城市扩展
    "map_black_rock_city": "wutan_growth",
    "map_salt_city": "wutan_growth",
    "map_ghost_pass": "wutan_growth",
    # desert_flame: 沙漠剧情关键节点
    "map_mo_city": "desert_flame",
    "map_stone_mo_city": "desert_flame",
    # canaan_outer: 黑角域扩展（黑印城拍卖、天涯城虫洞枢纽）
    "map_black_seal_city": "canaan_outer",
    "map_tianya_city": "canaan_outer",
    # return_black_corner: 黑角域清算战
    "map_demon_flame_valley": "return_black_corner",
    # poison_sect_war: 出云帝国万蝎门
    "map_scorpion_gate": "poison_sect_war",
    # zhongzhou_arrival: 中州宗门
    "map_sky_demon_sect": "zhongzhou_arrival",
    # save_mentor: 天目山脉与葬尸山脉
    "map_tianmu_mountains": "save_mentor",
    "map_heaven_mountain_blood_pool": "save_mentor",
    "map_death_corpse_mountains": "save_mentor",
    # soul_hall_war: 魂殿总部天罡殿
    "map_heavenly_gang_hall": "soul_hall_war",
    # demon_flame: 妖火平原
    "map_demon_flame_plain": "demon_flame",
    # ancient_emperor: 古帝异火广场
    "map_strange_flame_square": "ancient_emperor",
    # wutan_growth: 边境城市
    "map_daling_city": "wutan_growth",
    # canaan_outer: 黑角域入口与势力
    "map_black_domain_plain": "canaan_outer",
    "map_blood_sect": "canaan_outer",
    "map_eight_gates": "canaan_outer",
    # canaan_inner: 内院组织
    "map_pan_gate": "canaan_inner",
    # return_black_corner: 萧门与黑皇阁
    "map_xiao_gate": "return_black_corner",
    "map_black_emperor_pavilion": "return_black_corner",
    # zhongzhou_arrival: 中州扩展
    "map_scorching_mountains": "zhongzhou_arrival",
    "map_qi_feng_mountain": "zhongzhou_arrival",
    "map_tianhuang_city": "zhongzhou_arrival",
    "map_black_fire_sect": "zhongzhou_arrival",
    # dan_meeting_flame: 丹域扩展
    "map_wan_yao_mountains": "dan_meeting_flame",
    "map_small_dan_tower": "dan_meeting_flame",
    # bodhi_tree: 莽荒古域扩展
    "map_manghuang_town": "bodhi_tree",
    "map_heaven_demon_blood_pool": "bodhi_tree",
    "map_ancient_domain_platform": "bodhi_tree",
    # final_war: 葬天山脉
    "map_burial_sky_mountains": "final_war",
    # yunlan_war: 重返加玛与云岚宗大战
    "map_cloud_mountain_peak": "yunlan_war",
    "map_yan_alliance_hq": "yunlan_war",
    "map_jia_ma_battle_front": "yunlan_war",
    # poison_sect_war: 出云帝国与毒宗之战
    "map_chuyun_empire": "poison_sect_war",
    "map_poison_sect": "poison_sect_war",
    "map_golden_goose_sect": "poison_sect_war",
    "map_mulan_valley": "poison_sect_war",
    # revisit_tower: 再探塔底与天火尊者
    "map_skyfire_magma_world": "revisit_tower",
    # northwest_fortress_war: 玄黄要塞与西北大陆大战
    "map_xuanhuang_fortress": "northwest_fortress_war",
    "map_northwest_battle_front": "northwest_fortress_war",
    # tianfu_alliance: 建立天府联盟
    "map_tianfu_council_hall": "tianfu_alliance",
    "map_alliance_war_room": "tianfu_alliance",
    # nether_spring: 九幽黄泉与妖暝
    "map_nether_spring": "nether_spring",
    "map_nether_python_tribe": "nether_spring",
    "map_nether_underground_palace": "nether_spring",
    # post_demon_wars: 魂殿殿主与北龙王终战
    "map_soul_emperor_throne": "post_demon_wars",
    # five_emperors: 五帝破空
    "map_world_gate": "five_emperors",
    "map_emperor_memorial_peak": "five_emperors",
}

# 功能子区域沿用所属主区域的剧情开放阶段，避免等级提前解锁后续地图。
for _phase_id, _map_ids in {
    "fallen_genius": """
        map_xiao_mansion map_xiao_training_ground map_wutan_commercial_street
        map_wutan_back_mountain map_wutan_inn map_wutan_teahouse map_wutan_gate
        map_jia_ma_road
    """,
    "wutan_growth": """
        map_xiao_market map_wutan_pharmacy map_wutan_smithy map_miteer_appraisal
        map_xiao_council_hall map_wutan_east_market map_wutan_warehouse_district
        map_jia_ma_post_station
        map_black_rock_market map_black_rock_black_market map_salt_market
        map_ghost_pass_market map_ghost_pass_barracks
        map_black_rock_inn map_salt_inn map_daling_market map_daling_inn
    """,
    "mountain_training": """
        map_jia_ma_border map_jia_ma_garrison map_jia_ma_mountain_pass
        map_magic_inner map_magic_herb_valley map_wolfhead_camp
        map_magic_hidden_cave map_qingshan_mercenary_camp
        map_qingshan_medical_hall map_qingshan_market
    """,
    "desert_flame": """
        map_desert_trade_route map_snake_oasis map_desert_camp
        map_snake_temple_outer map_desert_salt_lake map_desert_ancient_well
        map_mo_market map_mo_inn map_mo_trade_post
        map_stone_mo_market map_stone_mo_mercenary map_stone_mo_inn
    """,
    "alchemy_conference": """
        map_capital_commercial map_imperial_palace map_capital_alchemist_market
        map_capital_nalan_mansion map_capital_miteer_hq map_capital_arena
    """,
    "yunlan_duel": """
        map_yunlan_gate map_yunlan_stairs map_yunlan_square
        map_yunlan_back_cliff map_yunlan_elder_hall
    """,
    "canaan_outer": """
        map_canaan_outer_square map_canaan_library map_canaan_dormitory
        map_canaan_mission_hall map_canaan_duel_arena map_black_blood_plain
        map_black_herb_market map_black_inn
        map_tianya_wormhole_square map_tianya_market map_tianya_inn
        map_black_seal_auction map_black_seal_market map_black_seal_inn
        map_black_emperor_market
        map_peace_town_inn map_peace_town_market map_canaan_trade_street
    """,
    "canaan_inner": "map_inner_arena map_inner_trade_district map_inner_market",
    "fallen_heart": "map_skyfire_lower map_skyfire_seal_core",
    "return_black_corner": """
        map_black_auction_lane map_black_emperor_square
        map_demon_valley_hall map_demon_valley_archive
    """,
    "zhongzhou_arrival": """
        map_zhongzhou_transfer_square map_zhongzhou_inn_district
        map_zhongzhou_north_market map_tianbei_han_clan map_tianbei_hong_clan
        map_zhongzhou_wormhole_station
        map_sky_demon_gate map_sky_demon_hall
        map_tianbei_market map_tianbei_inn
        map_burning_valley_market map_star_pavilion_market
    """,
    "ye_ice_valley": "map_ye_mansion map_ye_city_gate map_ye_alchemy_room map_ye_market",
    "dan_meeting_flame": """
        map_dan_herb_street map_sacred_dan_market map_dan_tower_outer_square
        map_dan_tower_trial_room map_dan_beast_enclosure map_star_domain
        map_tianhuang_market map_tianhuang_inn
    """,
    "save_mentor": """
        map_star_pavilion_back_mountain map_star_pavilion_mission_hall
        map_soul_hall_prison map_soul_hall_person_hall map_soul_hall_soul_well
    """,
    "ancient_ruins": """
        map_ancient_ruins_gate map_beast_bone_mountains map_beast_market
        map_ancient_ruins_core map_beast_region_trade_hub
    """,
    "bodhi_tree": "map_wilderness_outpost map_wilderness_poison_swamp map_manghuang_inn",
    "dragon_island_legacy": "map_dragon_island_harbor",
    "gu_clan_tomb": """
        map_ancient_city_market map_heaven_tomb_camp
    """,
    "black_corner_war": """
        map_feng_merchant_hall map_feng_alchemy_room map_feng_defense_wall
        map_feng_market
    """,
    "revive_mentor": """
        map_star_realm_core map_star_realm_training_ground map_star_pavilion_council
    """,
    "flower_sect": """
        map_flower_sect_gate map_flower_sect_garden map_flower_sect_heritage_hall
        map_flower_sect_market
    """,
    "dragon_island_war": """
        map_west_dragon_palace map_south_dragon_battlefield map_north_dragon_throne
    """,
    "demon_flame": """
        map_demon_flame_illusion_realm map_demon_flame_core
        map_demon_flame_saint_remains
    """,
    "medicine_ceremony": """
        map_yao_realm_ceremony_square map_yao_realm_herb_garden
        map_yao_realm_survivor_camp
    """,
    "ancient_clan_war": """
        map_soul_realm_battlefield map_hun_clan_ritual_site map_ancient_alliance_camp
    """,
    "ancient_emperor": """
        map_emperor_cave_gate map_emperor_cave_inner map_emperor_cave_treasure_room
    """,
    "final_war": """
        map_double_emperor_peak map_allied_forces_camp
    """,
    "poison_sect_war": """
        map_chuyun_border map_poison_sect_hall map_poison_sect_herb_cave
        map_scorpion_hall map_scorpion_cave
    """,
    "northwest_fortress_war": """
        map_xuanhuang_war_hall map_xuanhuang_defense_wall
    """,
    "nether_spring": """
        map_nether_spring_pool map_nether_python_throne
    """,
    "tianfu_alliance": """
        map_star_pavilion_alliance_hub
    """,
    "soul_hall_war": """
        map_heavenly_gang_prison map_heavenly_gang_origin
    """,
    "five_emperors": """
        map_emperor_ascension_platform
    """,
}.items():
    MAP_STORY_UNLOCKS.update(
        {map_id: _phase_id for map_id in _map_ids.split()}
    )

SCHEDULE_NODES = [
    {
        "id": "xiao_clan_trial",
        "day": 3,
        "period": 0,
        "title": "萧家族内试炼",
        "description": "族内长老将在演武场检验年轻一辈。你必须证明自己没有彻底失去锋芒。",
        "goals": {"level": 2, "training_wins": 1},
        "success_text": "你在试炼中稳住阵脚，赢得了父亲与族人的认可。",
        "success_effect": "exp:+30,reputation:+5,rel:npc_xiao_zhan:+5,item:+item_elixir",
        "failure_text": "准备不足令你在众目睽睽之下落败，族内质疑声愈发刺耳。",
        "failure_effect": "reputation:-5,rel:npc_xiao_zhan:-10,hp:-20",
    },
    {
        "id": "black_ring_deadline",
        "day": 7,
        "period": 2,
        "title": "后山之约",
        "description": "夕阳落下前，你必须带着足够的历练前往后山，查明黑色戒指的异动。",
        "goals": {"story_stage": 2, "adventure_points": 3},
        "success_text": "你如约抵达后山，戒指中传来一道苍老声音，新的道路由此展开。",
        "success_effect": "flag:ring_awakened=1,soul:+5,douqi:+5",
        "failure_text": "你错过了戒指最强烈的一次波动，只能付出更多时间重新寻找线索。",
        "failure_effect": "soul:-2,reputation:-2",
    },
]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


class GameEngine:
    def __init__(self, workbook_path: Path = WORKBOOK_PATH) -> None:
        data = load_game_data(workbook_path)
        self.events_list: List[Dict[str, Any]] = data["events"]
        self.events: Dict[str, Dict[str, Any]] = {
            event["id"]: event for event in self.events_list
        }
        self.start_event: str = data["start_event"]
        self.attribute_rules: Dict[str, Dict[str, Any]] = data["attributes"]
        self.flag_defaults: Dict[str, int] = data["flag_defaults"]
        self.npc_names: Dict[str, str] = data["npc_names"]
        self.npc_profiles: Dict[str, Dict[str, str]] = data["npc_profiles"]
        relationship_list: List[Dict[str, Any]] = data["relationships"]
        self.relationship_rules: Dict[str, Dict[str, Any]] = {
            rule["id"]: rule for rule in relationship_list
        }
        self.relationship_index = self._build_relationship_index(relationship_list)
        self.level_progression: List[Dict[str, Any]] = data["level_progression"]
        self.maps: Dict[str, Dict[str, Any]] = data["maps"]
        self.encounters: List[Dict[str, Any]] = data["encounters"]
        self.enemies: Dict[str, Dict[str, Any]] = data["enemies"]
        self.item_rules: Dict[str, Dict[str, Any]] = data["items"]
        # 合并生成的扩展道具
        for gid, gitem in _GEN_ITEMS.items():
            if gid in REMOVED_ITEM_IDS:
                continue
            if gid not in self.item_rules:
                self.item_rules[gid] = {
                    "name": gitem["name"],
                    "type": gitem["type"],
                    "description": gitem.get("desc", ""),
                    "use_effect": gitem.get("effect", ""),
                    "tier": gitem.get("tier", "iron"),
                    "price_buy": gitem.get("price_buy", 0),
                    "price_sell": gitem.get("price_sell", 0),
                }
        # 合并生成的装备到物品表（商店和掉落使用）
        for eid, eq in _GEN_EQUIPMENT.items():
            if eid not in self.item_rules:
                self.item_rules[eid] = {
                    "name": eq["name"],
                    "type": "equipment",
                    "description": f"{eq['tier_name']}{'武器' if eq['slot'] == 'weapon' else '防具' if eq['slot'] == 'armor' else '饰品'} "
                                   f"[{eq['rarity']}] ATK+{eq['atk']} DEF+{eq['def']} HP+{eq['hp']}",
                    "use_effect": "",
                    "tier": eq["tier"],
                    "price_buy": (eq["atk"] + eq["def"] + eq["hp"]) * 5,
                    "price_sell": (eq["atk"] + eq["def"] + eq["hp"]) * 2,
                    "slot": eq["slot"],
                }
        # 合并23异火
        for flame in HEAVENLY_FLAMES_FULL:
            fid = flame["id"]
            if fid not in self.item_rules:
                self.item_rules[fid] = {
                    "name": flame["name"], "type": "heavenly_flame",
                    "description": flame["desc"], "use_effect": "",
                    "tier": flame["tier"],
                    "price_buy": flame["price_buy"], "price_sell": flame["price_sell"],
                }
        # 合并100功法
        for tech in TECHNIQUE_DATA:
            tid = tech["id"]
            if tid not in self.item_rules:
                self.item_rules[tid] = {
                    "name": tech["name"], "type": "technique",
                    "description": tech["desc"], "use_effect": tech["effect"],
                    "tier": tech["tier"], "element": tech["element"],
                    "price_buy": tech["price_buy"], "price_sell": tech["price_sell"],
                }
        # 合并211技能书
        for book in SKILL_BOOK_DATA:
            bid = book["id"]
            if bid not in self.item_rules:
                self.item_rules[bid] = {
                    "name": book["name"], "type": "book",
                    "description": book["desc"], "use_effect": f"learn:{book['skill_id']}",
                    "tier": book["tier"],
                    "price_buy": book["price_buy"], "price_sell": book["price_sell"],
                }
        # 合并药鼎到物品表
        for fdata in FURNACE_DATA:
            fid = fdata["id"]
            if fid not in self.item_rules:
                self.item_rules[fid] = {
                    "name": fdata["name"], "type": "furnace",
                    "description": f"{ALCHEMY_GRADES[fdata['grade']-1]}药鼎 | {fdata['desc']} "
                                   f"加成+{fdata['bonus']}% | {fdata['special']}"
                                   + (f" | 可用{fdata['max_uses']}次" if fdata['max_uses'] > 0 else " | 无限使用"),
                    "use_effect": "", "tier": ["iron","refined","spirit","treasure","earth","heaven","mystic","saint","emperor","divine"][fdata['grade']-1],
                    "price_buy": fdata["price_buy"], "price_sell": fdata["price_sell"],
                }
        # 合并纳戒
        for ring in STORAGE_RINGS:
            rid = ring["id"]
            if rid not in self.item_rules:
                self.item_rules[rid] = {
                    "name": ring["name"], "type": "storage_ring",
                    "description": ring["desc"], "use_effect": f"capacity:+{ring['capacity']}",
                    "tier": ring["tier"],
                    "price_buy": ring["price_buy"], "price_sell": ring["price_sell"],
                }
        # 合并新技能元素映射
        SKILL_ELEMENTS.update(SKILL_ELEMENTS_FULL)
        self.skills: Dict[str, Dict[str, Any]] = data["skills"]
        SKILL_ELEMENTS.update(_build_skill_elements(self.skills))
        # 合并生成的扩展技能（211个新技能）
        for book in SKILL_BOOK_DATA:
            sid = book.get("skill_id", "")
            if sid and sid not in self.skills:
                self.skills[sid] = {
                    "name": book["skill_name"],
                    "description": book["desc"],
                    "effect": f"atk:+{book['atk_bonus']}" if book["atk_bonus"] > 0 else book.get("effect", ""),
                    "type": "skill",
                }
                if book.get("element", "无") != "无":
                    SKILL_ELEMENTS[sid] = book["element"]
        for sid, (name, effect, description) in ENEMY_SKILL_FALLBACKS.items():
            if sid not in self.skills:
                self.skills[sid] = {
                    "id": sid,
                    "name": name,
                    "description": description,
                    "effect": effect,
                    "type": "enemy_skill",
                }
        for removed_id in REMOVED_ITEM_IDS:
            self.item_rules.pop(removed_id, None)
        SKILL_ELEMENTS.update(_build_skill_elements(self.skills))
        for sid, skill in self.skills.items():
            skill["id"] = sid
            skill["mastery"] = build_skill_mastery(
                skill, SKILL_ELEMENTS.get(sid, "无")
            )
        self.realms: List[Dict[str, Any]] = data["realms"]
        self.active_encounter: Optional[Dict[str, Any]] = None
        self.active_exploration: Optional[Dict[str, Any]] = None
        self.combat: Optional[Dict[str, Any]] = None
        self.player: Dict[str, Any] = self._create_new_player()
        self.last_message: str = ""
        self.auction_listings: List[Dict[str, Any]] = []
        self.auction_last_map = ""
        self.auction_last_period = -1

    def new_game(self, name: Optional[str] = None) -> None:
        self.player = self._create_new_player()
        self.active_encounter = None
        self.active_exploration = None
        self.combat = None
        if name:
            self.player["name"] = name
        self.last_message = "斗气大陆的故事由此开始。"

    def save(self) -> None:
        self._sync_story_phase_id()
        SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with SAVE_PATH.open("w", encoding="utf-8") as file:
            json.dump(self.player, file, ensure_ascii=False, indent=2)

    def load(self) -> bool:
        if not SAVE_PATH.exists():
            return False
        self.player = load_json(SAVE_PATH)
        self._ensure_player_state()
        self.active_encounter = None
        self.active_exploration = None
        self.combat = None
        self.last_message = "存档已读取，并已迁移到最新剧情数据。"
        return True

    def _create_new_player(self) -> Dict[str, Any]:
        player: Dict[str, Any] = {
            rule_id: rule["initial"] for rule_id, rule in self.attribute_rules.items()
        }
        player.update(
            {
                "name": self.npc_names.get("player", "萧炎"),
                "max_hp": self.attribute_rules["hp"]["initial"],
                "flags": [
                    flag_id
                    for flag_id, default in self.flag_defaults.items()
                    if default
                ],
                "items": [],
                "visited": {},
                "exploration_counts": {},
                "relationships": {},
                "relationship_triggers": [],
                "active_statuses": [],
                "timed_statuses": {},
                "current_event": self.start_event,
                "last_map": "map_wutan",
                "adventure_points": 0,
                "story_stage": 0,
                "story_phase_id": STORY_PHASES[0]["id"],
                "story_substage": 0,
                "known_skills": ["skill_bajibang", "skill_flame_mantra"],
                "equipped": {"weapon": None, "armor": None, "accessory": None},
                "equipped_technique": None,
                "known_techniques": [],
                "alchemy_grade": 1,
                "alchemy_sub": 0,
                "alchemy_exp": 0,
                "known_recipes": ["recipe_1","recipe_2","recipe_4","recipe_5","recipe_6"],
                "equipped_furnace": None,
                "furnace_uses": {},
                "reverse_progress": {},
                "inventory_capacity": BASE_INVENTORY_CAPACITY,
                "storage_overflow": [],
                "wallet": {"copper": 500, "silver": 0, "gold": 0, "ancient": 0},
                "day": 1,
                "time_period": 0,
                "completed_schedule_nodes": [],
                "pending_schedule_node": "",
                "training_wins": 0,
                "progress": 0.0,
            }
        )
        # 新游戏：移除attribute_rules遗留的silver（币系统已改用wallet）
        for old_key in ("silver", "gold"):
            if old_key in player and isinstance(player.get(old_key), (int, float)):
                amount = int(player.pop(old_key, 0))
                if amount > 0:
                    player["wallet"] = wallet_add(player.get("wallet", {}), amount)
        self._ensure_player_state(player)
        return player

    def _ensure_player_state(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player

        nested_player = player.get("player")
        if isinstance(nested_player, dict):
            player.setdefault("name", nested_player.get("name", "萧炎"))
            attributes = nested_player.get("attributes", {})
            if isinstance(attributes, dict):
                for key, value in attributes.items():
                    player.setdefault(key, value)

        for legacy_key, current_key in LEGACY_STAT_ALIASES.items():
            if current_key not in player and legacy_key in player:
                player[current_key] = player[legacy_key]
        for attribute_id, rule in self.attribute_rules.items():
            player.setdefault(attribute_id, rule["initial"])

        flags = player.get("flags", [])
        if isinstance(flags, dict):
            player["flags"] = [key for key, value in flags.items() if int(value)]
        else:
            player.setdefault("flags", [])
        for legacy_flag, current_flag in LEGACY_FLAG_ALIASES.items():
            if legacy_flag in player["flags"] and current_flag not in player["flags"]:
                player["flags"].append(current_flag)
        for flag_id, default in self.flag_defaults.items():
            if default and flag_id not in player["flags"]:
                player["flags"].append(flag_id)

        if "items" not in player:
            inventory = player.get("inventory", {})
            if isinstance(inventory, dict):
                player["items"] = [
                    item_id
                    for item_id, count in inventory.items()
                    for _ in range(max(0, int(count)))
                ]
            else:
                player["items"] = []

        player.setdefault("name", self.npc_names.get("player", "萧炎"))
        player.setdefault(
            "max_hp", max(self.attribute_rules["hp"]["initial"], player["hp"])
        )
        player.setdefault("visited", {})
        player.setdefault("exploration_counts", {})
        player.setdefault("relationships", {})
        player.setdefault("relationship_triggers", [])
        player.setdefault("active_statuses", [])
        player.setdefault("timed_statuses", {})
        player.setdefault("last_map", "map_wutan")
        player.setdefault("adventure_points", 0)
        player.setdefault("equipped", {"weapon": None, "armor": None, "accessory": None})
        player.setdefault("equipped_technique", None)
        player.setdefault("known_techniques", [])
        player.setdefault("equipped_flame", None)
        player.setdefault("collected_flames", [])
        player.setdefault("equipped_storage_rings", [])
        player.setdefault("defeated_enemies", {})
        player.setdefault("skill_levels", {})
        player.setdefault("second_technique", None)
        player.setdefault("fixed_technique", None)  # FenJue
        player.setdefault("fen_jue_level", 0)
        player.setdefault("attr_points", 0)
        player.setdefault("skill_points", 0)
        player.setdefault("alchemy_grade", 1)
        player.setdefault("alchemy_sub", 0)
        player.setdefault("alchemy_exp", 0)
        player.setdefault("known_recipes", ["recipe_1","recipe_2","recipe_4","recipe_5","recipe_6"])
        player.setdefault("equipped_furnace", None)
        player.setdefault("furnace_uses", {})
        player["items"] = [
            item_id for item_id in player.get("items", [])
            if item_id not in REMOVED_ITEM_IDS
        ]
        player["storage_overflow"] = [
            item_id for item_id in player.get("storage_overflow", [])
            if item_id not in REMOVED_ITEM_IDS
        ]
        player.setdefault("reverse_progress", {})
        player.setdefault("inventory_capacity", BASE_INVENTORY_CAPACITY)
        player.setdefault("storage_overflow", [])
        # 币系统迁移：旧存档silver/gold → wallet
        player.setdefault("wallet", {"copper": 0, "silver": 0, "gold": 0, "ancient": 0})
        for old_key in ("silver", "gold"):
            if old_key in player and isinstance(player.get(old_key), (int, float)):
                amount = int(player.pop(old_key, 0))
                if amount > 0:
                    player["wallet"] = wallet_add(player["wallet"], amount)
        if "story_phase_id" in player:
            phase_id = player["story_phase_id"]
            matching_stage = next(
                (
                    index
                    for index, phase in enumerate(STORY_PHASES)
                    if phase["id"] == phase_id
                ),
                len(STORY_PHASES) if not phase_id else None,
            )
            if matching_stage is not None:
                player["story_stage"] = matching_stage
        else:
            old_stage = int(player.get("story_stage", player.get("story_steps", 0)))
            if 0 <= old_stage < len(LEGACY_STORY_PHASE_IDS_V2):
                old_phase_id = LEGACY_STORY_PHASE_IDS_V2[old_stage]
                player["story_stage"] = next(
                    (
                        index
                        for index, phase in enumerate(STORY_PHASES)
                        if phase["id"] == old_phase_id
                    ),
                    min(len(STORY_PHASES), old_stage),
                )
            else:
                player["story_stage"] = min(len(STORY_PHASES), old_stage)
            player["story_phase_id"] = (
                STORY_PHASES[player["story_stage"]]["id"]
                if player["story_stage"] < len(STORY_PHASES)
                else ""
            )
        player.setdefault("story_substage", 0)
        player.setdefault("known_skills", [])  # Learned through story
        player.setdefault("day", 1)
        player.setdefault("time_period", 0)
        player.setdefault("completed_schedule_nodes", [])
        player.setdefault("pending_schedule_node", "")
        player.setdefault("training_wins", 0)
        player.setdefault("progress", 0.0)
        self._check_schedule_nodes(player)
        if player.get("current_event") not in self.events:
            player["current_event"] = self.start_event
        self._ensure_relationship_state(player)
        self._clamp_player_stats(player)
        self._apply_progress(player)

    def _ensure_relationship_state(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player
        values = player.setdefault("relationships", {})
        for relation_id, rule in self.relationship_rules.items():
            values.setdefault(relation_id, int(rule.get("initial_value", 0)))

    @staticmethod
    def _build_relationship_index(
        relationship_list: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        index: Dict[str, str] = {}
        for rule in relationship_list:
            relation_id = rule["id"]
            source = rule["source"]
            target = rule["target"]
            index[relation_id] = relation_id
            index[f"{source}>{target}"] = relation_id
            if source == "player":
                index[target] = relation_id
            if rule.get("bidirectional"):
                index[f"{target}>{source}"] = relation_id
        return index

    def relation_rule(self, reference: str) -> Dict[str, Any]:
        relation_id = self.relationship_index.get(reference)
        if relation_id is None:
            raise KeyError(f"未定义的关系：{reference}")
        return self.relationship_rules[relation_id]

    def relation_value(self, reference: str) -> int:
        rule = self.relation_rule(reference)
        return int(self.player["relationships"][rule["id"]])

    def relation_stage(self, reference: str) -> str:
        rule = self.relation_rule(reference)
        value = self.relation_value(reference)
        stage = "未定义"
        thresholds = []
        for item in rule.get("stage_rule", "").split("|"):
            if not item:
                continue
            threshold, name = item.split(":", 1)
            thresholds.append((int(threshold), name))
        for threshold, name in sorted(thresholds):
            if value >= threshold:
                stage = name
        return stage

    def set_relation_value(
        self, reference: str, value: int, evaluate_triggers: bool = True
    ) -> List[str]:
        rule = self.relation_rule(reference)
        relation_id = rule["id"]
        # 免疫关系：不受任何事件影响，始终保持满值
        if relation_id in IMMUNE_RELATIONSHIPS:
            target_name = self.npc_names.get(rule["target"], rule["target"])
            return [f"与{target_name}的关系坚不可摧，不受此事件影响。"]
        old_value = self.relation_value(reference)
        new_value = max(
            int(rule.get("min_value", -100)),
            min(int(rule.get("max_value", 100)), int(value)),
        )
        self.player["relationships"][relation_id] = new_value
        target_name = self.npc_names.get(rule["target"], rule["target"])
        logs = [f"关系 {target_name} {old_value}->{new_value}"]
        if evaluate_triggers:
            logs.extend(self._apply_on_reach_effect(rule))
        return logs

    def change_relation_value(
        self, reference: str, delta: int, evaluate_triggers: bool = True
    ) -> List[str]:
        rule = self.relation_rule(reference)
        if rule["id"] in IMMUNE_RELATIONSHIPS:
            target_name = self.npc_names.get(rule["target"], rule["target"])
            return [f"与{target_name}的关系坚不可摧，不受此事件影响。"]
        return self.set_relation_value(
            reference,
            self.relation_value(reference) + delta,
            evaluate_triggers=evaluate_triggers,
        )

    def _apply_on_reach_effect(self, rule: Dict[str, Any]) -> List[str]:
        expression = rule.get("on_reach_effect")
        if not expression:
            return []
        match = ON_REACH_PATTERN.match(expression)
        if not match or not self._check_condition_token(match.group(1)):
            return []
        trigger_id = f"{rule['id']}:{expression}"
        triggered: List[str] = self.player["relationship_triggers"]
        if trigger_id in triggered:
            return []
        triggered.append(trigger_id)
        return self.apply_effects(match.group(2), evaluate_relationship_triggers=False)

    def current_event(self) -> Dict[str, Any]:
        event_id = self.player.get("current_event", self.start_event)
        if event_id not in self.events:
            event_id = self.start_event
            self.player["current_event"] = event_id
        return self.events[event_id]

    def mark_visited(self, event_id: str) -> None:
        visited = self.player.setdefault("visited", {})
        visited[event_id] = visited.get(event_id, 0) + 1

    @staticmethod
    def _compare(left: int, operator: str, right: int) -> bool:
        return {
            ">": left > right,
            ">=": left >= right,
            "<": left < right,
            "<=": left <= right,
            "==": left == right,
            "!=": left != right,
        }[operator]

    @staticmethod
    def _canonical_stat(key: str) -> str:
        return LEGACY_STAT_ALIASES.get(key, key)

    def _check_condition_token(self, token: str) -> bool:
        token = token.strip()
        if not token:
            return True
        if token.startswith("item:"):
            return token[5:] in self.player.get("items", [])
        # stamina system removed, always pass stamina conditions
        if token.startswith("stamina"):
            return True
        if token.startswith("flag:"):
            name, expected = token[5:].split("=", 1)
            actual = 1 if name in self.player.get("flags", []) else 0
            return actual == int(expected)

        match = COMPARISON_PATTERN.match(token)
        if not match:
            raise ValueError(f"不支持的条件表达式：{token}")
        key, operator, raw_value = match.groups()
        if key.startswith("rel:"):
            actual = self.relation_value(key[4:])
        else:
            actual = int(self.player.get(self._canonical_stat(key), 0))
        return self._compare(actual, operator, int(raw_value))

    def check_conditions(self, conditions: Optional[Any]) -> bool:
        if not conditions:
            return True
        if isinstance(conditions, str):
            return all(
                self._check_condition_token(token) for token in conditions.split(",")
            )

        player = self.player
        for stat, value in conditions.get("stat_min", {}).items():
            if player.get(self._canonical_stat(stat), 0) < value:
                return False
        for stat, value in conditions.get("stat_max", {}).items():
            if player.get(self._canonical_stat(stat), 0) > value:
                return False
        for flag in conditions.get("has_flags", []):
            if flag not in player.get("flags", []):
                return False
        for flag in conditions.get("not_flags", []):
            if flag in player.get("flags", []):
                return False
        for item in conditions.get("has_items", []):
            if item not in player.get("items", []):
                return False
        for item in conditions.get("not_items", []):
            if item in player.get("items", []):
                return False
        return True

    def available_options(
        self, event: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[int, Dict[str, Any]]]:
        event = event or self.current_event()
        if not self.check_conditions(event.get("conditions")):
            return []
        result = []
        for index, option in enumerate(event.get("options", []), start=1):
            if self.check_conditions(option.get("conditions")):
                result.append((index, option))
        return result

    def _apply_effect_token(
        self, token: str, evaluate_relationship_triggers: bool
    ) -> List[str]:
        token = token.strip()
        if not token:
            return []

        match = RELATION_EFFECT_PATTERN.match(token)
        if match:
            return self.change_relation_value(
                match.group(1),
                int(match.group(2)),
                evaluate_triggers=evaluate_relationship_triggers,
            )
        match = RELATION_SET_PATTERN.match(token)
        if match:
            return self.set_relation_value(
                match.group(1),
                int(match.group(2)),
                evaluate_triggers=evaluate_relationship_triggers,
            )
        if token.startswith("item:+"):
            item = token[6:]
            if item in self.player["items"]:
                return []
            self.player["items"].append(item)
            return [f"获得道具：{self.item_name(item)}"]
        if token.startswith("item:-"):
            item = token[6:]
            if item in self.player["items"]:
                self.player["items"].remove(item)
            return [f"失去道具：{self.item_name(item)}"]
        if token.startswith("flag:"):
            name, raw_value = token[5:].split("=", 1)
            flags = self.player["flags"]
            if int(raw_value) and name not in flags:
                flags.append(name)
            elif not int(raw_value) and name in flags:
                flags.remove(name)
            return [f"剧情开关 {name}={raw_value}"]
        if token.startswith("status:+"):
            status = token[8:]
            if status not in self.player["active_statuses"]:
                self.player["active_statuses"].append(status)
            return [f"获得状态：{status}"]
        if token.startswith("status:-"):
            status = token[8:]
            if status in self.player["active_statuses"]:
                self.player["active_statuses"].remove(status)
            return [f"移除状态：{status}"]

        key, raw_value = token.split(":", 1)
        key = self._canonical_stat(key)
        # 货币特殊处理
        if key == "silver":
            value = int(raw_value)
            self.player["wallet"] = wallet_add(self.player["wallet"], value)
            sign = "+" if value >= 0 else ""
            return [f"银两 {sign}{value}"]
        if key not in self.attribute_rules:
            raise ValueError(f"不支持的效果表达式：{token}")
        value = int(raw_value)
        self.player[key] = self.player.get(key, 0) + value
        sign = "+" if value >= 0 else ""
        return [f"{self.attribute_rules[key]['name']} {sign}{value}"]

    def apply_effects(
        self,
        effects: Optional[Any],
        evaluate_relationship_triggers: bool = True,
    ) -> List[str]:
        if not effects:
            return []
        if isinstance(effects, str):
            logs: List[str] = []
            for token in effects.split(","):
                logs.extend(
                    self._apply_effect_token(token, evaluate_relationship_triggers)
                )
            self._clamp_player_stats()
            logs.extend(self._apply_progress())
            return logs

        logs: List[str] = []
        for key, value in effects.items():
            canonical_key = self._canonical_stat(key)
            if canonical_key in self.attribute_rules:
                self.player[canonical_key] = self.player.get(canonical_key, 0) + value
                logs.append(f"{self.attribute_rules[canonical_key]['name']} {value:+d}")
        self._clamp_player_stats()
        logs.extend(self._apply_progress())
        return logs

    def _clamp_player_stats(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player
        for attribute_id, rule in self.attribute_rules.items():
            if attribute_id in ("silver", "gold"):
                continue  # 货币已迁移到wallet系统
            value = int(player.get(attribute_id, rule["initial"]))
            maximum = rule["max"]
            if attribute_id == "douqi" and player is getattr(self, "player", None):
                maximum = self.effective_max_douqi()
            player[attribute_id] = max(rule["min"], min(maximum, value))

    def _progress_rule(self, level: int) -> Optional[Dict[str, Any]]:
        for rule in self.level_progression:
            if rule["min_level"] <= level <= rule["max_level"]:
                return rule
        return None


    SKILL_LV_THRESHOLDS = {1: 0, 2: 10, 3: 30, 4: 60, 5: 100}
    SKILL_LV_MULT = {1: 1.0, 2: 1.12, 3: 1.30, 4: 1.50, 5: 1.75}
    SKILL_LV_CRIT = {1: 0, 2: 2, 3: 5, 4: 8, 5: 12}
    SKILL_LV_NAMES = {1: "Beginner", 2: "Skilled", 3: "Expert", 4: "Master", 5: "Grandmaster"}
    FEN_JUE_ID = "tech_火_焚天诀"

    def _record_skill_use(self, skill_id: str) -> None:
        if not skill_id:
            return
        sl = self.player.setdefault("skill_levels", {})
        entry = sl.setdefault(skill_id, {"level": 1, "uses": 0})
        entry["uses"] = entry.get("uses", 0) + 1
        new_lv = entry["level"]
        for lv in [2, 3, 4, 5]:
            if entry["uses"] >= self.SKILL_LV_THRESHOLDS[lv]:
                new_lv = lv
        if new_lv > entry["level"]:
            entry["level"] = new_lv
            skill = self.skills.get(skill_id, {})
            self.last_special = (
                f"Skill [{skill.get('name', skill_id)}] leveled up to "
                f"{self.SKILL_LV_NAMES[new_lv]} (Lv{new_lv})!"
            )

    def _skill_level_bonus(self, skill_id: str) -> tuple:
        if not skill_id:
            return (1.0, 0, 1)
        sl = self.player.get("skill_levels", {})
        entry = sl.get(skill_id, {"level": 1, "uses": 0})
        lv = entry.get("level", 1)
        return (self.SKILL_LV_MULT.get(lv, 1.0),
                self.SKILL_LV_CRIT.get(lv, 0), lv)

    def add_timed_status(
        self, status_id: str, value: int, turns: int, name: str = ""
    ) -> None:
        """添加或刷新统一持续状态。"""
        statuses = self.player.setdefault("timed_statuses", {})
        current = statuses.get(status_id, {})
        statuses[status_id] = {
            "value": max(int(value), int(current.get("value", 0))),
            "turns": max(int(turns), int(current.get("turns", 0))),
            "name": name or current.get("name", status_id),
        }

    def timed_status_value(self, status_id: str) -> int:
        status = self.player.get("timed_statuses", {}).get(status_id, {})
        return int(status.get("value", 0)) if int(status.get("turns", 0)) > 0 else 0

    def _tick_timed_statuses(self) -> List[str]:
        """在玩家回合开始时结算回复并推进持续回合。"""
        statuses = self.player.setdefault("timed_statuses", {})
        logs: List[str] = []
        hp_regen = self.timed_status_value("hp_regen")
        douqi_regen = self.timed_status_value("douqi_regen")
        if hp_regen:
            before = self.player["hp"]
            self.player["hp"] = min(self.effective_max_hp(), before + hp_regen)
            if self.player["hp"] > before:
                logs.append(f"持续恢复生命 {self.player['hp'] - before}")
        if douqi_regen:
            before = self.player["douqi"]
            self.player["douqi"] = min(self.effective_max_douqi(), before + douqi_regen)
            if self.player["douqi"] > before:
                logs.append(f"持续恢复斗气 {self.player['douqi'] - before}")
        expired = []
        for status_id, status in statuses.items():
            status["turns"] = int(status.get("turns", 0)) - 1
            if status["turns"] <= 0:
                expired.append(status_id)
        for status_id in expired:
            status = statuses.pop(status_id)
            logs.append(f"{status.get('name', status_id)}效果结束")
        return logs

    def timed_status_text(self) -> str:
        statuses = self.player.get("timed_statuses", {})
        return "、".join(
            f"{status.get('name', status_id)}({status.get('turns', 0)}回合)"
            for status_id, status in statuses.items()
            if int(status.get("turns", 0)) > 0
        ) or "无"

    def _apply_timed_item_effect(self, effect: str) -> List[str]:
        """将物品 DSL 转换为统一持续状态。"""
        logs: List[str] = []
        match = re.fullmatch(r"(hp_regen|douqi_regen):(\d+),(\d+)", effect)
        if match:
            status_id, value, turns = match.groups()
            name = "生命持续恢复" if status_id == "hp_regen" else "斗气持续恢复"
            self.add_timed_status(status_id, int(value), int(turns), name)
            return [f"获得{name}，持续{turns}回合"]
        match = re.fullmatch(r"element_boost:(\w+)", effect)
        if match:
            element = ELEMENT_ITEM_NAMES.get(match.group(1), match.group(1))
            self.add_timed_status(f"element_power_{element}", 30, 5, f"{element}属性强化")
            return [f"{element}属性伤害提高30%，持续5回合"]
        match = re.fullmatch(r"(thorns|lifesteal):(\d+)", effect)
        if match:
            status_id, value = match.groups()
            name = "反伤" if status_id == "thorns" else "吸血"
            self.add_timed_status(status_id, int(value), 5, name)
            return [f"获得{name}{value}%，持续5回合"]
        match = re.fullmatch(r"resist:(\w+)", effect)
        if match:
            element = ELEMENT_ITEM_NAMES.get(match.group(1), match.group(1))
            self.add_timed_status(f"resist_{element}", 30, 5, f"{element}属性抗性")
            return [f"{element}属性抗性提高30%，持续5回合"]
        if effect == "temp_buff:all":
            for status_id in ("atk_pct", "def_pct", "spd_pct"):
                self.add_timed_status(status_id, 10, 5, "祝福")
            return ["攻击、防御、速度提高10%，持续5回合"]
        return logs

    def skill_mastery_text(self, skill_id: str) -> str:
        """返回技能的 Lv3/Lv5 强化说明，供各 UI 统一展示。"""
        skill = self.skills.get(skill_id, {})
        parts = []
        for level in (3, 5):
            data = skill.get("mastery", {}).get(level, {})
            if data:
                parts.append(f"Lv{level}【{data['name']}】{data['description']}")
        return "；".join(parts)

    def _apply_skill_mastery_before_damage(
        self, skill: Dict[str, Any], level: int, multiplier: float, enemy_def: int
    ) -> Tuple[float, int, int, float]:
        """应用伤害结算前的技能里程碑，返回倍率、防御、额外暴击率、暴伤。"""
        element = SKILL_ELEMENTS.get(skill.get("id", ""), "无")
        crit_bonus = 0
        crit_mult = 2.0
        if level >= 3:
            if element == "雷":
                enemy_def = int(enemy_def * 0.85)
            elif element == "无":
                multiplier *= 1.10
        if level >= 5:
            if element == "火":
                multiplier *= 1.25
            elif element == "雷":
                multiplier *= 1.20
            elif element == "风":
                multiplier *= 1.15
            elif element == "土":
                enemy_def = int(enemy_def * 0.70)
            elif element == "毒" and self.combat:
                multiplier *= 1.0 + self.combat.get("poison", 0) * 0.08
            elif element == "无":
                crit_bonus += 25
                crit_mult = 2.5
        return multiplier, enemy_def, crit_bonus, crit_mult

    def _apply_skill_mastery_after_damage(
        self, skill: Dict[str, Any], level: int, cost: int, actual_damage: int
    ) -> List[str]:
        """应用命中后的技能里程碑效果。"""
        if self.combat is None or level < 3:
            return []
        combat = self.combat
        element = SKILL_ELEMENTS.get(skill.get("id", ""), "无")
        logs: List[str] = []
        if element == "火":
            combat["burn"] = max(combat.get("burn", 0), 2)
            combat["burn_dmg"] = max(1, self._skill_attack_bonus(skill.get("effect", "")) // 5)
            logs.append("Lv3【余烬】目标陷入灼烧")
        elif element == "冰":
            combat["debuff_spd"] = max(
                combat.get("debuff_spd", 0), max(1, int(combat["spd"] * 0.20))
            )
            combat["debuff_spd_turns"] = max(combat.get("debuff_spd_turns", 0), 2)
            logs.append("Lv3【寒侵】敌人速度降低")
        elif element == "风":
            refund = max(1, cost // 5)
            self.player["douqi"] = min(
                self.effective_max_douqi(), self.player["douqi"] + refund
            )
            combat["combo"] = combat.get("combo", 0) + 1
            logs.append(f"Lv3【回风】返还{refund}斗气并增加连击")
        elif element == "木":
            heal = max(1, self.effective_max_hp() * 5 // 100)
            self.player["hp"] = min(self.effective_max_hp(), self.player["hp"] + heal)
            logs.append(f"Lv3【生息】恢复{heal}生命")
        elif element == "土":
            shield = max(1, self.effective_max_hp() * 8 // 100)
            combat["player_shield"] = combat.get("player_shield", 0) + shield
            logs.append(f"Lv3【岩甲】获得{shield}护盾")
        elif element == "毒":
            combat["poison"] = min(7, combat.get("poison", 0) + 1)
            logs.append("Lv3【蚀骨】额外施加1层中毒")

        if level >= 5:
            if element == "火" and combat.get("burn", 0):
                burst = combat.get("burn_dmg", 1) * combat.get("burn", 0)
                combat["hp"] = max(0, combat["hp"] - burst)
                combat["burn"] = 0
                logs.append(f"Lv5【焚灭】引爆灼烧，额外造成{burst}伤害")
            elif element in ("冰", "雷") and random.randint(1, 100) <= (25 if element == "冰" else 20):
                combat["stunned"] = combat.get("stunned", 0) + 1
                logs.append("Lv5里程碑触发，敌人下一次行动被封锁")
            elif element == "风":
                combat["player_gauge"] = combat.get("player_gauge", 0) + GAUGE_MAX // 2
                logs.append("Lv5【无影】行动条推进50%")
            elif element == "木":
                heal = max(1, actual_damage // 5)
                self.player["hp"] = min(self.effective_max_hp(), self.player["hp"] + heal)
                logs.append(f"Lv5【共生】吸取{heal}生命")
            elif element == "土":
                combat["def"] = max(0, int(combat["def"] * 0.90))
                logs.append("Lv5【山崩】敌人防御降低10%")
        return logs

    def _apply_utility_skill_effect(self, skill: Dict[str, Any], level: int) -> List[str]:
        """执行辅助斗技效果；Lv3/Lv5分别提高25%/50%。"""
        if self.combat is None or "atk:+" in skill.get("effect", ""):
            return []
        combat = self.combat
        scale = 1.5 if level >= 5 else 1.25 if level >= 3 else 1.0
        scale *= 1.0 + self._technique_effect_value("heal_bonus") / 100.0
        logs: List[str] = []
        debuff = re.search(r"debuff:(atk|def|spd),(\d+)", skill.get("effect", ""))
        if debuff:
            stat, raw_amount = debuff.groups()
            amount = int(int(raw_amount) * scale)
            if stat == "def":
                combat["def"] = max(0, int(combat["def"] * (1 - amount / 100)))
            elif stat == "spd":
                combat["debuff_spd"] = max(
                    combat.get("debuff_spd", 0), int(combat["spd"] * amount / 100)
                )
            else:
                combat["atk"] = max(1, int(combat["atk"] * (1 - amount / 100)))
            logs.append(f"敌人{stat}降低{amount}%")
        for token in skill.get("effect", "").split(","):
            parts = token.split(":")
            kind = parts[0]
            raw = parts[1].split(",")[0] if len(parts) > 1 else ""
            value = int(float(raw) * scale) if raw.isdigit() else 0
            if kind == "heal":
                self.player["hp"] = min(self.effective_max_hp(), self.player["hp"] + value)
                logs.append(f"斗技恢复{value}生命")
            elif kind == "douqi_restore":
                self.player["douqi"] = min(
                    self.effective_max_douqi(), self.player["douqi"] + value
                )
                logs.append(f"斗技恢复{value}斗气")
            elif kind == "shield":
                combat["player_shield"] = combat.get("player_shield", 0) + value
                logs.append(f"斗技生成{value}护盾")
            elif kind == "hp_drain":
                dealt = min(value, combat["hp"])
                combat["hp"] -= dealt
                self.player["hp"] = min(self.effective_max_hp(), self.player["hp"] + dealt)
                logs.append(f"吸取敌人{dealt}生命")
            elif kind == "douqi_drain":
                combat["hp"] = max(0, combat["hp"] - value)
                logs.append(f"扰乱斗气造成{value}伤害")
            elif kind == "extra_turn":
                combat["player_gauge"] = combat.get("player_gauge", 0) + GAUGE_MAX
                logs.append("获得额外行动")
            elif kind in ("seal", "cleanse", "cure_poison", "cure_mental"):
                if kind == "seal":
                    combat["stunned"] = combat.get("stunned", 0) + 1
                    logs.append("敌人被封印一次行动")
                else:
                    logs.append("负面状态已被净化")
        if level >= 5:
            combat["player_gauge"] = combat.get("player_gauge", 0) + GAUGE_MAX // 2
            logs.append("Lv5【圆满之境】行动条推进50%")
        return logs

    # ── Dual Technique Slots ─────────────────────────────────

    def equip_technique(self, tech_id: str, slot: int = 0) -> bool:
        """slot 0=auto: FenJue→fixed, other→second. slot 1=fixed, 2=second."""
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tech_id), None)
        if tech is None:
            self.last_message = "Technique not found."
            return False
        if tech_id not in self.player.get("known_techniques", []):
            self.player.setdefault("known_techniques", []).append(tech_id)
        if tech_id == self.FEN_JUE_ID:
            self.player["fixed_technique"] = tech_id
            self.player["equipped_technique"] = tech_id
            self.last_message = f"Fixed technique: {tech['name']} ({tech['element']})"
            return True
        old = self.player.get("second_technique")
        self.player["second_technique"] = tech_id
        self.last_message = f"Equipped: {tech['name']} ({tech['element']})"
        if old:
            old_t = next((t for t in TECHNIQUE_DATA if t["id"] == old), {})
            self.last_message += f" (replaced {old_t.get('name', old)})"
        return True

    def unequip_technique(self) -> bool:
        tid = self.player.get("second_technique")
        if not tid:
            self.last_message = "No second technique equipped."
            return False
        tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), {})
        self.player["second_technique"] = None
        self.last_message = f"Unequipped: {tech.get('name', tid)}"
        return True

    def upgrade_fen_jue(self) -> bool:
        fid = self.player.get("equipped_flame")
        if not fid:
            self.last_message = "Need an equipped flame to upgrade FenJue."
            return False
        if self.player.get("fixed_technique") != self.FEN_JUE_ID:
            self.last_message = "Need FenJue equipped first."
            return False
        flame = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == fid), None)
        if not flame:
            return False
        self.player["equipped_flame"] = None
        fj = self.player.get("fen_jue_level", 0) + 1
        self.player["fen_jue_level"] = min(10, fj)
        self.last_message = (
            f"FenJue absorbed {flame['name']}! Now at layer {self.player['fen_jue_level']}."
        )
        return True

    def _exp_for_progress(self, level: int) -> int:
        """EXP per decile of progress. Total per level = return * 10.
        Uses level^2/2 for smooth scaling: Lv1=10, Lv50=12500, Lv90=40500 total."""
        return max(1, level * level // 2)

    def _is_realm_boundary(self, level: int) -> bool:
        return level in REALM_BOUNDARY_LEVELS

    @staticmethod
    def _realm_index(level: int) -> int:
        boundaries = sorted(REALM_BOUNDARY_LEVELS)
        for i, boundary in enumerate(boundaries):
            if level <= boundary:
                return i
        return len(boundaries)

    def _breakthrough_chance_bp(self, level: int) -> int:
        """返回突破成功率，单位为万分之一（bp）。10000 = 100%，1 = 0.01%"""
        if self._is_realm_boundary(level):
            realm_index = self._realm_index(level)
            return REALM_BREAKTHROUGH_CHANCE_BP.get(realm_index, 1)
        else:
            # 段内突破：80% → 逐渐衰减，最低 0.5%（50bp）
            return max(50, int((80 - level * 0.78) * 100))

    def _apply_level_gains(self, level: int, player: Optional[Dict[str, Any]] = None) -> List[str]:
        """应用升级时的属性增益 + 属性点 + 技能点。"""
        player = player if player is not None else self.player
        logs: List[str] = []
        # 每级固定获得 10 属性点 + 5 技能点（不受 Excel 规则影响）
        player["attr_points"] = player.get("attr_points", 0) + 10
        player["skill_points"] = player.get("skill_points", 0) + 5
        logs.append(f"获得 10 属性点、5 技能点（累计属性 {player['attr_points']}，技能 {player['skill_points']}）")
        rule = self._progress_rule(level)
        if rule is None:
            return logs
        for attribute_id, gain in rule["gains"].items():
            player[attribute_id] = player.get(attribute_id, 0) + gain
            if attribute_id == "hp":
                player["max_hp"] = player.get("max_hp", player["hp"]) + gain
        self._clamp_player_stats(player)
        skill_id = LEVEL_SKILL_MILESTONES.get(level)
        if skill_id and skill_id not in player["known_skills"]:
            player["known_skills"].append(skill_id)
            logs.append(f"领悟斗技：{self.skills[skill_id]['name']}")
        return logs

    def allocate_attr_point(self, stat: str) -> bool:
        """分配 1 属性点到 ATK/DEF/HP/SPD。"""
        valid = {"atk": "atk", "def": "def", "hp": "max_hp", "spd": "spd"}
        if stat not in valid:
            self.last_message = f"无效属性：{stat}。可选：atk/def/hp/spd"
            return False
        if self.player.get("attr_points", 0) <= 0:
            self.last_message = "没有可用的属性点。"
            return False
        self.player["attr_points"] -= 1
        key = valid[stat]
        self.player[key] = self.player.get(key, 0) + 1
        if stat == "hp":
            self.player["hp"] = self.player.get("hp", 0) + 1
        name_map = {"atk": "攻击", "def": "防御", "hp": "生命", "spd": "速度"}
        self.last_message = f"{name_map[stat]}+1（剩余属性点 {self.player['attr_points']}）"
        return True

    def upgrade_skill_with_point(self, skill_id: str) -> bool:
        """消耗 1 技能点提升技能等级（跳过使用次数限制）。"""
        if self.player.get("skill_points", 0) <= 0:
            self.last_message = "没有可用的技能点。"
            return False
        skill = self.skills.get(skill_id)
        if skill is None:
            self.last_message = "未习得该技能。"
            return False
        self.player["skill_points"] -= 1
        sl = self.player.setdefault("skill_levels", {})
        entry = sl.setdefault(skill_id, {"level": 1, "uses": 0})
        if entry["level"] >= 5:
            self.last_message = f"{skill['name']} 已达最高等级。"
            self.player["skill_points"] += 1  # refund
            return False
        entry["level"] += 1
        entry["uses"] = self.SKILL_LV_THRESHOLDS[entry["level"]]
        lv_name = self.SKILL_LV_NAMES[entry["level"]]
        self.last_message = (
            f"{skill['name']} 提升至 {lv_name}（Lv{entry['level']}）！"
            f"（剩余技能点 {self.player['skill_points']}）"
        )
        return True

    def breakthrough(self) -> bool:
        """尝试突破到下一等级。返回是否成功。"""
        if float(self.player.get("progress", 0)) < 100.0:
            self.last_message = "修炼进度未满，还无法尝试突破。"
            return False

        level = int(self.player["level"])
        if level >= 100:
            self.last_message = "你已是斗帝之境，无需突破。"
            return False

        if not self._can_take_free_action():
            return False

        chance_bp = self._breakthrough_chance_bp(level)
        success = random.randint(1, 10000) <= chance_bp

        boundary_text = "境界" if self._is_realm_boundary(level) else "段内"
        exp_lost = self._exp_for_progress(level) // 2

        # 格式化概率显示
        if chance_bp >= 100:
            chance_text = f"{chance_bp / 100:.0f}%"
        elif chance_bp >= 10:
            chance_text = f"{chance_bp / 100:.1f}%"
        else:
            chance_text = f"{chance_bp / 100:.2f}%"

        if success:
            self.player["level"] = level + 1
            self.player["progress"] = 0.0
            realm = self.realm_name()
            logs = self._apply_level_gains(level + 1)
            self.last_message = (
                f"{boundary_text}突破成功！你晋升至 {realm} Lv.{level + 1}。"
                f"（成功率 {chance_text}）"
            )
            if logs:
                self.last_message += "；" + "；".join(logs)
        else:
            self.player["exp"] = max(0, self.player["exp"] - exp_lost)
            self.last_message = (
                f"{boundary_text}突破失败！（成功率 {chance_text}）\n"
                f"你损失了 {exp_lost} 点经验，进度仍为 100.00%，可再次尝试。"
            )

        self.advance_time()
        return success

    def _apply_progress(
        self, player: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """按百分比消耗 exp 填充修炼进度。"""
        player = player if player is not None else self.player
        logs: List[str] = []
        level = int(player.get("level", 1))
        total_exp_needed = self._exp_for_progress(level) * 10
        if total_exp_needed <= 0:
            return logs

        progress = float(player.get("progress", 0.0))
        if progress >= 100.0:
            return logs  # 已满，需要突破

        exp = int(player.get("exp", 0))
        if exp <= 0:
            return logs

        # 计算填满到 100% 还差多少 exp
        exp_to_full = max(1, int((100.0 - progress) / 100.0 * total_exp_needed))
        consume = min(exp, exp_to_full)
        progress_gained = consume / total_exp_needed * 100.0
        new_progress = min(100.0, progress + progress_gained)

        player["exp"] = exp - consume
        old_pct = int(progress)
        player["progress"] = round(new_progress, 2)
        new_pct = int(player["progress"])

        if player["progress"] >= 100.0:
            player["progress"] = 100.0
            logs.append("修炼进度已满（100.00%）！可以尝试突破。")
        elif new_pct > old_pct:
            logs.append(f"修炼进度 {player['progress']:.2f}%")

        return logs

    def eligible_random_events(self) -> List[Dict[str, Any]]:
        return [
            event
            for event in self.events_list
            if event.get("pool") not in {"", "main"}
            and self.check_conditions(event.get("conditions"))
        ]

    def choose_random_event_id(self) -> str:
        candidates = self.eligible_random_events()
        if not candidates:
            return self.player.get("current_event", self.start_event)
        weights = [max(1, int(event.get("weight", 1))) for event in candidates]
        return random.choices(candidates, weights=weights, k=1)[0]["id"]

    def resolve_next(self, option: Dict[str, Any]) -> str:
        next_id = option.get("next", "")
        if not next_id:
            return self.player.get("current_event", self.start_event)
        if next_id == "random":
            return self.choose_random_event_id()
        if "|" in next_id:
            branches = []
            for branch in next_id.split("|"):
                event_id, weight = branch.rsplit(":", 1)
                branches.append((event_id, max(1, int(weight))))
            return random.choices(
                [branch[0] for branch in branches],
                weights=[branch[1] for branch in branches],
                k=1,
            )[0]
        return next_id

    def choose_option(self, visible_option_number: int) -> bool:
        event = self.current_event()
        option_map = {index: option for index, option in self.available_options(event)}
        if visible_option_number not in option_map:
            self.last_message = "无效选择，或当前条件尚未满足。"
            return False

        self.mark_visited(event["id"])
        option = option_map[visible_option_number]
        logs = self.apply_effects(option.get("effects"))
        next_id = self.resolve_next(option)
        if next_id in self.events:
            self.player["current_event"] = next_id
        else:
            logs.append(f"暂不支持的跳转：{next_id}")
        self.last_message = "；".join(logs) if logs else "继续前行。"
        return True

    def realm_name(self) -> str:
        level = int(self.player.get("level", 1))
        for realm in self.realms:
            if realm["min_level"] <= level <= realm["max_level"]:
                return realm["name"]
        return "未知境界"

    def current_map(self) -> Dict[str, Any]:
        return self.maps.get(self.player.get("last_map", ""), self.maps["map_wutan"])

    def time_text(self) -> str:
        return f"第{self.player['day']}日 {TIME_PERIODS[self.player['time_period']]}"

    def is_night(self) -> bool:
        return int(self.player["time_period"]) >= 2

    def pending_schedule_node(self) -> Optional[Dict[str, Any]]:
        node_id = self.player.get("pending_schedule_node", "")
        return next((node for node in SCHEDULE_NODES if node["id"] == node_id), None)

    def next_schedule_node(self) -> Optional[Dict[str, Any]]:
        completed = set(self.player.get("completed_schedule_nodes", []))
        return next((node for node in SCHEDULE_NODES if node["id"] not in completed), None)

    def schedule_text(self, node: Dict[str, Any]) -> str:
        goals = []
        for key, required in node["goals"].items():
            names = {
                "level": "等级",
                "training_wins": "切磋胜场",
                "story_steps": "主线进度",
                "story_stage": "关键阶段",
                "adventure_points": "冒险阅历",
            }
            goals.append(f"{names.get(key, key)} {self.player.get(key, 0)}/{required}")
        return (
            f"{node['title']}｜第{node['day']}日 {TIME_PERIODS[node['period']]}\n"
            f"{node['description']}\n目标：" + "、".join(goals)
        )

    def schedule_countdown_text(self, node: Dict[str, Any]) -> str:
        node_time = (node["day"] - 1) * len(TIME_PERIODS) + node["period"]
        remaining = max(0, node_time - self._absolute_time())
        days, periods = divmod(remaining, len(TIME_PERIODS))
        parts = []
        if days:
            parts.append(f"{days}日")
        if periods:
            parts.append(f"{periods}个时段")
        return "剩余" + ("".join(parts) if parts else "时间已到")

    def _can_take_free_action(self) -> bool:
        if self.pending_schedule_node() is None:
            return True
        self.last_message = "当前有必须处理的日程节点，无法进行其他行动。"
        return False

    def _absolute_time(self, player: Optional[Dict[str, Any]] = None) -> int:
        player = player if player is not None else self.player
        return (int(player["day"]) - 1) * len(TIME_PERIODS) + int(player["time_period"])

    def _check_schedule_nodes(self, player: Optional[Dict[str, Any]] = None) -> None:
        player = player if player is not None else self.player
        if player.get("pending_schedule_node"):
            return
        completed = set(player.get("completed_schedule_nodes", []))
        current_time = self._absolute_time(player)
        for node in SCHEDULE_NODES:
            node_time = (node["day"] - 1) * len(TIME_PERIODS) + node["period"]
            if node["id"] not in completed and current_time >= node_time:
                player["pending_schedule_node"] = node["id"]
                return

    def advance_time(self, periods: int = 1) -> None:
        elapsed = max(0, periods)
        absolute = self._absolute_time() + elapsed
        self.player["day"] = absolute // len(TIME_PERIODS) + 1
        self.player["time_period"] = absolute % len(TIME_PERIODS)
        self._advance_auction_time(elapsed)
        self._check_schedule_nodes()

    def resolve_schedule_node(self) -> bool:
        node = self.pending_schedule_node()
        if node is None:
            self.last_message = "当前没有必须处理的日程。"
            return False
        success = all(
            int(self.player.get(key, 0)) >= required
            for key, required in node["goals"].items()
        )
        result_text = node["success_text"] if success else node["failure_text"]
        effects = node["success_effect"] if success else node["failure_effect"]
        logs = self.apply_effects(effects)
        self.player["completed_schedule_nodes"].append(node["id"])
        self.player["pending_schedule_node"] = ""
        self.last_message = (
            f"{'达标' if success else '未达标'}：{result_text}"
            + ("；" + "；".join(logs) if logs else "")
        )
        self._check_schedule_nodes()
        return success

    def available_maps(self) -> List[Dict[str, Any]]:
        return [map_rule for map_rule in self.maps.values() if self.is_map_unlocked(map_rule["id"])]

    def is_map_unlocked(self, map_id: str) -> bool:
        phase_id = MAP_STORY_UNLOCKS.get(map_id)
        if phase_id is None:
            return False
        required_stage = next(
            (
                index
                for index, phase in enumerate(STORY_PHASES)
                if phase["id"] == phase_id
            ),
            len(STORY_PHASES),
        )
        return int(self.player.get("story_stage", 0)) >= required_stage

    def map_unlock_text(self, map_id: str) -> str:
        phase_id = MAP_STORY_UNLOCKS.get(map_id)
        phase = next((phase for phase in STORY_PHASES if phase["id"] == phase_id), None)
        return f"推进至“{phase['title']}”开放" if phase else "尚无开放剧情"

    def travel(self, map_id: str) -> bool:
        if not self._can_take_free_action():
            return False
        map_rule = self.maps.get(map_id)
        if map_rule is None or not self.is_map_unlocked(map_id):
            self.last_message = (
                f"该区域尚未开放。{self.map_unlock_text(map_id)}"
                if map_rule is not None
                else "不存在该区域。"
            )
            return False
        if self.player["time_period"] == 3 and not map_rule["safe_zone"]:
            self.last_message = "深夜无法安全前往危险区域，请等到天亮。"
            return False

        # 跨区通行检查（与原文通行方式一致）
        current_region = REGION_BY_MAP.get(self.player["last_map"], "未知")
        target_region = REGION_BY_MAP.get(map_id, "未知")
        transit_map_id = TRANSIT_HUBS.get((current_region, target_region))
        if transit_map_id:
            transit_name = TRANSIT_HUB_NAMES.get(transit_map_id, transit_map_id)
            visited = self.player.setdefault("visited", {})
            if not visited.get(transit_map_id):
                hub_rule = self.maps.get(transit_map_id, {})
                self.last_message = (
                    f"从{current_region}前往{target_region}需要经由{transit_name}中转。\n"
                    f"请先抵达{hub_rule.get('name', transit_map_id)}，再尝试前往{target_region}。"
                )
                return False

        # 根据区域间距计算通行耗时
        if current_region != target_region and current_region != "中转站":
            # 跨区通行耗时更久
            periods = 2
        else:
            periods = 1

        self.player["last_map"] = map_id
        self.active_encounter = None
        self.active_exploration = None
        self.advance_time(periods)

        # 通行描述与原文一致
        if transit_map_id:
            self.last_message = (
                f"你通过{TRANSIT_HUB_NAMES.get(transit_map_id, '中转站')}"
                f"抵达了{map_rule['name']}。{map_rule['description']}"
            )
        else:
            self.last_message = f"你抵达了{map_rule['name']}。{map_rule['description']}"
        return True

    def rest(self) -> bool:
        if not self._can_take_free_action():
            return False
        map_rule = self.current_map()
        if not map_rule["safe_zone"]:
            self.last_message = "此处危机四伏，不宜休息。请前往城镇、客栈或据点等安全区域。"
            return False
        self.player["hp"] = self.player["max_hp"]
        periods = len(TIME_PERIODS) - int(self.player["time_period"])
        self.advance_time(periods)
        self.last_message = f"你休整到{self.time_text()}，生命已经恢复。"
        return True

    def cultivate(self) -> bool:
        if not self._can_take_free_action():
            return False
        soul_gain = 2 if self.is_night() else 1
        self.player["adventure_points"] += 1
        if "ring_awakened" not in self.player["flags"]:
            logs = self.apply_effects(f"soul:+{soul_gain}")
            action_text = "药老尚未苏醒，你只能感知戒指异动、锤炼灵魂。"
        else:
            logs = self.apply_effects(f"exp:+10,douqi:+2,soul:+{soul_gain}")
            action_text = "你依照药老指导运转斗气，完成了一轮修炼。"
        self.advance_time()
        self.last_message = action_text + "；获得冒险阅历 +1"
        if logs:
            self.last_message += "；" + "；".join(logs)
        return True


    # ── 野外遇敌辅助方法 ─────────────────────────────────────

    def _current_period(self) -> int:
        """Current period index for cooldown tracking."""
        return int(self.player.get("day", 1)) * 4 + int(self.player.get("time_period", 0))

    def _is_story_enemy(self, enemy_id: str) -> bool:
        """Story enemies (boss/final_boss/rival/with win_next) never spawn in wild."""
        enemy = self.enemies.get(enemy_id, {})
        etype = enemy.get("type", "mob")
        if etype in ("boss", "final_boss", "rival"):
            return True
        if enemy.get("win_next") or enemy.get("lose_next"):
            return True
        if not enemy.get("can_kill", True):
            return True
        return False

    def _is_beast_enemy(self, enemy_id: str) -> bool:
        """Beast enemies drop materials only, no currency."""
        enemy = self.enemies.get(enemy_id, {})
        name = enemy.get("name", "")
        eid_lower = enemy_id.lower()
        return any(kw in name.lower() or kw in eid_lower for kw in BEAST_NAME_KEYWORDS)

    def _spawn_wild_enemy(self, map_level: int) -> Optional[Dict[str, Any]]:
        """Select a random wild enemy matching the map level."""
        current = self._current_period()
        candidates = []
        weights = []

        for eid, enemy in self.enemies.items():
            if self._is_story_enemy(eid):
                continue
            etype = enemy.get("type", "mob")
            if etype not in ("mob", "elite"):
                continue
            elv = int(enemy.get("level", 1))
            if abs(elv - map_level) > 5:
                continue
            last_defeat = self.player.get("defeated_enemies", {}).get(eid, -999)
            if current - last_defeat < RESPAWN_COOLDOWN_PERIODS:
                continue
            candidates.append(enemy)
            weights.append(WILD_ELITE_WEIGHT if etype == "elite" else WILD_MOB_WEIGHT)

        if not candidates:
            return None
        total_w = max(1, sum(weights))
        weights = [w / total_w for w in weights]
        return random.choices(candidates, weights=weights, k=1)[0]

    def _random_beast_loot(self, enemy_level: int, count: int = 1,
                            tier_shift: int = 0, enemy_type: str = "mob") -> List[str]:
        """Beast loot: materials only, no equipment/currency. Respects tier_shift."""
        tier = self._tier_for_level(enemy_level)
        all_tiers = self.ALL_TIERS
        tier_idx = all_tiers.index(tier) if tier in all_tiers else 0

        results = []
        for _ in range(count):
            if tier_shift >= 3:
                use_idx = min(len(all_tiers) - 1, tier_idx + 2)
            elif tier_shift >= 1:
                use_idx = min(len(all_tiers) - 1, tier_idx + 1) if random.random() < 0.10 else tier_idx
            else:
                use_idx = min(len(all_tiers) - 1, tier_idx + 1) if random.random() < 0.10 else tier_idx
            use_tier = all_tiers[use_idx]
            pool = LOOT_TABLE.get(use_tier, LOOT_TABLE.get(tier, []))
            mat_ids, mat_weights = [], []
            for pid, weight in pool:
                rule = self.item_rules.get(pid, {})
                itype = rule.get("type", "")
                if itype in ("material", "consumable") and not pid.startswith("eq_"):
                    mat_ids.append(pid)
                    mat_weights.append(weight)
            if not mat_ids:
                continue
            total_w = max(1, sum(mat_weights))
            r = random.randint(1, total_w)
            cum = 0
            for i, w in enumerate(mat_weights):
                cum += w
                if r <= cum:
                    results.append(mat_ids[i])
                    break
        return results

    # ── 原有方法 ─────────────────────────────────────────────

    def exploration_actions(self) -> List[Dict[str, Any]]:
        map_rule = self.current_map()
        night_cost = 2 if self.is_night() else 0
        return [
            {
                "id": action_id,
                **rule,
                "cost": max(
                    1,
                    int(map_rule["stamina_cost"])
                    + night_cost
                    + int(rule["cost_modifier"]),
                ),
            }
            for action_id, rule in EXPLORATION_ACTIONS.items()
        ]

    @staticmethod
    def _encounter_has_combat(encounter: Dict[str, Any]) -> bool:
        return any(
            str(option.get("next", "")).startswith("combat:")
            for option in encounter.get("options", [])
        )

    def _exploration_weight(self, encounter: Dict[str, Any], action_id: str) -> int:
        weight = max(1, int(encounter["weight"]))
        visited = int(self.player.get("visited", {}).get(encounter["id"], 0))
        has_combat = self._encounter_has_combat(encounter)
        if action_id == "scout":
            return weight * max(1, 4 - min(visited, 3))
        if action_id == "gather":
            return weight * (4 if not has_combat else 1)
        if action_id == "hunt":
            return weight * (5 if has_combat else 1)
        if action_id == "investigate":
            return weight * max(1, 5 - min(visited, 4))
        return weight

    def explore(self, action_id: str = "roam") -> Optional[Dict[str, Any]]:
        if not self._can_take_free_action():
            return None
        action = EXPLORATION_ACTIONS.get(action_id)
        if action is None:
            self.last_message = "没有这种探索方式。"
            return None
        map_rule = self.current_map()
        action_logs = []
        if action_id == "scout":
            action_logs.extend(self.apply_effects("soul:+1"))
        elif action_id == "gather":
            silver_gain = random.randint(2, 6)
            action_logs.extend(self.apply_effects(f"silver:+{silver_gain},alchemy:+1"))
        elif action_id == "investigate":
            self.player["adventure_points"] += 1
            action_logs.append("冒险阅历 +1")

        counts = self.player.setdefault("exploration_counts", {})
        counts[action_id] = int(counts.get(action_id, 0)) + 1
        self.active_exploration = {
            "action_id": action_id,
            "action_name": action["name"],
            "cost": 0,
            "logs": action_logs,
        }
        candidates = [
            encounter
            for encounter in self.encounters
            if encounter["map_id"] == map_rule["id"]
            and self.check_conditions(encounter.get("conditions"))
        ]
        if not candidates:
            self.player["adventure_points"] += 1
            self.advance_time()
            action_logs.append("冒险阅历 +1")
            self.last_message = (
                f"你在{map_rule['name']}进行了“{action['name']}”，虽然没有触发特别遭遇，"
                f"但熟悉了周边环境。结果：" + "；".join(action_logs)
            )
            self.active_exploration = None
            return None
        self.active_encounter = random.choices(
            candidates,
            weights=[
                self._exploration_weight(encounter, action_id)
                for encounter in candidates
            ],
            k=1,
        )[0]
        self.last_message = (
            f"你在{map_rule['name']}进行“{action['name']}”。"
            f"即时结果：" + "；".join(action_logs) + f"。随后发现：{self.active_encounter['text']}"
        )
        return self.active_encounter

    def encounter_options(self) -> List[Tuple[int, Dict[str, Any]]]:
        if self.active_encounter is None:
            return []
        return [
            (index, option)
            for index, option in enumerate(self.active_encounter["options"], start=1)
            if self.check_conditions(option.get("conditions"))
        ]

    def choose_encounter_option(self, option_number: int) -> bool:
        option_map = {index: option for index, option in self.encounter_options()}
        if option_number not in option_map:
            self.last_message = "当前无法选择该行动。"
            return False
        option = option_map[option_number]
        logs = self.apply_effects(option.get("effects"))
        next_id = option.get("next", "")
        encounter = self.active_encounter
        if encounter:
            self.mark_visited(encounter["id"])
        action_name = (
            self.active_exploration.get("action_name", "探索")
            if self.active_exploration
            else "探索"
        )
        self.active_encounter = None
        self.active_exploration = None
        self.player["adventure_points"] += 1
        logs.append("冒险阅历 +1")
        if self.is_night():
            self.player["adventure_points"] += 1
            logs.append("夜间探索额外获得 1 点冒险阅历")
        response = (
            f"你在“{action_name}”中选择了“{option['text']}”。"
            f"这次行动让你处理了当前遭遇。结果：" + "；".join(logs)
        )
        if next_id.startswith("combat:"):
            self.combat_time_cost = 1
            self.begin_combat(next_id[7:])
            self.last_message = response + "；" + self.last_message
        else:
            self.advance_time()
            self.last_message = response
        return True

    def leave_encounter(self) -> bool:
        if self.active_encounter is None:
            self.last_message = "当前没有需要离开的探索遭遇。"
            return False
        encounter = self.active_encounter
        action_name = (
            self.active_exploration.get("action_name", "探索")
            if self.active_exploration
            else "探索"
        )
        self.mark_visited(encounter["id"])
        self.active_encounter = None
        self.active_exploration = None
        self.player["adventure_points"] += 1
        logs = ["冒险阅历 +1"]
        if self.is_night():
            self.player["adventure_points"] += 1
            logs.append("夜间探索额外获得 1 点冒险阅历")
        self.advance_time()
        self.last_message = (
            f"你在“{action_name}”中判断继续介入风险过高，于是记下"
            f"“{encounter['text']}”的情况后离开。结果：" + "；".join(logs)
        )
        return True

    def begin_training_combat(self) -> bool:
        if not self._can_take_free_action():
            return False
        level = int(self.player["level"])
        self.combat_time_cost = 1
        self.combat_is_training = True
        self.combat = {
            "enemy_id": "training_opponent",
            "name": "萧家陪练弟子",
            "level": level,
            "hp": 25 + level * 10,
            "max_hp": 25 + level * 10,
            "atk": 4 + level * 2,
            "def": 1 + level,
            "spd": 4 + level,
            "exp_reward": 8 + level * 4,
            "drop_table": "",
            "round": 1,
            "defending": False,
            "can_escape": True,
            "element": "火",
            "weakness": "风",
            "shield_broken": False,
            "intent": "attack",
            "combo": 0,
            "charged": False,
            "charge_used": False,
            "player_gauge": 0,
            "enemy_gauge": 0,
        }
        self.last_message = "陪练弟子摆开架势，回合战斗开始。"
        return True

    def begin_combat(self, enemy_id: str) -> bool:
        enemy = self.enemies.get(enemy_id)
        if enemy is None:
            self.last_message = f"未找到敌人配置：{enemy_id}"
            return False
        level = int(self.player["level"])
        enemy_level = max(level, min(enemy["level"], level + 4))
        # Player-relative clamp: ensures TTK 3~15 while preserving type scaling
        p_atk = max(10, int(self.player.get("atk", 10)))
        p_def = max(3, int(self.player.get("def", 5)))
        p_spd = max(5, int(self.player.get("spd", 8)))

        tm = {"mob": 1.0, "elite": 1.5, "boss": 2.2, "final_boss": 3.5, "rival": 1.4}
        t = tm.get(enemy.get("type", "mob"), 1.0)

        raw_hp = enemy.get("hp", 30)
        raw_atk = enemy.get("atk", 4)
        raw_def = enemy.get("def", 1)
        raw_spd = enemy.get("spd", 3)
        raw_exp = enemy.get("exp_reward", 8)

        # ATK: raw with cap so player survives 2+ hits (final_boss 1-hit KO acceptable)
        atk_lo = max(4, int(p_def * 0.2 * t))
        atk_hi = int(p_def * 1.5 * t)
        atk_c = max(atk_lo, min(raw_atk, atk_hi))

        # DEF: raw with cap so player always deals 30%+ ATK as damage
        def_lo = max(1, int(p_atk * 0.03 * t))
        def_hi = int(p_atk * 0.65)
        def_c = max(def_lo, min(raw_def, def_hi))

        # HP: after boss ×3 / final_boss ×5 post-multiplier, target TTK 4-15
        # Use smaller base since HP multipliers apply after clamp
        hp_lo = max(30, int(p_atk * 2))
        hp_hi = int(p_atk * 4 * t)
        hp = max(hp_lo, min(raw_hp, hp_hi))

        # SPD: player-relative
        spd_lo = max(3, int(p_spd * 0.3))
        spd_hi = int(p_spd * 1.0 * t)
        spd_c = max(spd_lo, min(raw_spd, spd_hi))

        exp_c = max(8, raw_exp)
        # Boss/精英额外 HP 倍率
        if enemy["type"] == "final_boss":
            hp = hp * 5
            atk_c = int(atk_c * 1.5)
        elif enemy["type"] == "boss":
            hp = int(hp * 3)
            atk_c = int(atk_c * 1.3)

        # 属性克制
        if enemy_id not in ENEMY_ELEMENTS:
            elem = random.choice(ELEMENT_TYPES)
            weakness = ELEMENT_WEAKNESS[elem]
            ENEMY_ELEMENTS[enemy_id] = {"element": elem, "weakness": weakness}

        # 意图预判
        intent = random.choice(["attack", "attack", "defend", "skill"])

        self.combat = {
            "enemy_id": enemy_id,
            "name": enemy["name"],
            "level": enemy_level,
            "hp": hp,
            "max_hp": hp,
            "atk": atk_c,
            "def": def_c,
            "spd": spd_c,
            "exp_reward": exp_c,
            "drop_table": enemy["drop_table"],
            "type": enemy["type"],
            "notes": enemy.get("notes", ""),
            "round": 1,
            "defending": False,
            "can_escape": enemy["type"] not in {"boss", "final_boss"},
            # 新机制
            "element": ENEMY_ELEMENTS[enemy_id]["element"],
            "weakness": ENEMY_ELEMENTS[enemy_id]["weakness"],
            "shield_broken": False,
            "intent": intent,
            "combo": 0,
            "charged": False,
            "charge_used": False,
            "player_gauge": 0,
            "enemy_gauge": 0,
        }
        self.combat_is_training = False
        self.last_message = (
            f"{enemy['name']}（{ENEMY_ELEMENTS[enemy_id]['element']}属性）挡住了去路，回合战斗开始。"
        )
        return True

    def combat_text(self) -> str:
        if self.combat is None:
            return ""
        c = self.combat
        intent_names = {"attack": "攻击", "defend": "防御", "skill": "斗技", "charge": "蓄力"}
        intent_text = intent_names.get(c.get("intent", "attack"), "?")
        soul = int(self.player.get("soul", 0))
        intent_line = f"  意图预判：{intent_text}" if soul >= 20 else ""
        combo = c.get("combo", 0)
        combo_line = f"  连击：{combo}" if combo >= 2 else ""
        poison = c.get("poison", 0)
        poison_line = f"  中毒：{poison}层(-{c.get('poison_dmg', 0)}/回)" if poison > 0 else ""
        shield = " [护盾已破]" if c.get("shield_broken") else ""
        p_gauge = c.get("player_gauge", 0)
        e_gauge = c.get("enemy_gauge", 0)
        p_spd = self.effective_spd()
        e_spd = int(c.get("spd", 5))
        p_pct = p_gauge * 100 // GAUGE_MAX
        e_pct = e_gauge * 100 // GAUGE_MAX
        return (
            f"第{c['round']}回合｜{c['name']}{shield}（{c.get('element', '?')}属性）\n"
            f"生命 {c['hp']}/{c['max_hp']}  行动条 {e_gauge}/{GAUGE_MAX}({e_pct}%)（SPD:{e_spd}）\n"
            f"{self.player['name']} 生命 {self.player['hp']}｜斗气 {self.player['douqi']}"
            f"  行动条 {p_gauge}/{GAUGE_MAX}({p_pct}%)（SPD:{p_spd}）"
            f"{intent_line}{combo_line}{poison_line}"
        )

    def combat_intent_text(self) -> str:
        """返回敌人意图文本（用于 UI 渲染），技能意图显示具体技能名。"""
        if self.combat is None:
            return ""
        intent = self.combat.get("intent", "attack")
        intent_names = {"attack": "攻击", "defend": "防御", "skill": "斗技", "charge": "蓄力"}
        text = intent_names.get(intent, "?")
        if intent == "skill":
            enemy_data = self.enemies.get(self.combat["enemy_id"], {})
            enemy_skills = enemy_data.get("skills", [])
            if enemy_skills:
                skill_data = self.skills.get(enemy_skills[0], {})
                text = f"斗技「{skill_data.get('name', enemy_skills[0])}」"
        return text

    def enemy_skill_list(self) -> List[str]:
        """返回当前敌人的技能名称列表。"""
        if self.combat is None:
            return []
        enemy_data = self.enemies.get(self.combat["enemy_id"], {})
        return [
            self.skills.get(sid, {}).get("name", sid)
            for sid in enemy_data.get("skills", [])
        ]

    def enemy_element(self) -> str:
        if self.combat is None:
            return ""
        return self.combat.get("element", "")

    def enemy_weakness(self) -> str:
        if self.combat is None:
            return ""
        return self.combat.get("weakness", "")

    def combat_combo(self) -> int:
        if self.combat is None:
            return 0
        return self.combat.get("combo", 0)

    def combat_charged(self) -> bool:
        if self.combat is None:
            return False
        return self.combat.get("charged", False)

    def combat_shield_broken(self) -> bool:
        if self.combat is None:
            return False
        return self.combat.get("shield_broken", False)

    def combat_skills(self) -> List[Dict[str, Any]]:
        return [
            self.skills[skill_id]
            for skill_id in self.player.get("known_skills", [])
            if skill_id in self.skills
        ]

    @staticmethod
    def _skill_attack_bonus(effect: str) -> int:
        for token in effect.split(","):
            if token.startswith("atk:+"):
                return int(token[5:])
        return 0

    def _skill_cost(self, skill: Dict[str, Any]) -> int:
        cost = max(2, 2 + self._skill_attack_bonus(skill["effect"]) // 15)
        level = self._skill_level_bonus(skill.get("id", ""))[2]
        if level >= 3 and "atk:+" not in skill.get("effect", ""):
            cost = max(1, cost * 3 // 4)
        elif level >= 3 and SKILL_ELEMENTS.get(skill.get("id", ""), "无") == "无":
            cost = max(1, cost * 4 // 5)
        return cost

    def _estimated_attack_damage(self, bonus: int = 0, multiplier: float = 1.0) -> int:
        if self.combat is None:
            return 0
        return max(1, int((self.effective_atk() + bonus) * multiplier) - self.combat["def"])

    @staticmethod
    def _effect_gain(effect: str, stat: str) -> int:
        prefix = f"{stat}:+"
        for token in effect.split(","):
            if token.startswith(prefix):
                return int(token[len(prefix):])
        return 0

    def _combat_healing_items(self) -> List[Tuple[str, int, int]]:
        missing_hp = max(0, int(self.player["max_hp"]) - int(self.player["hp"]))
        missing_douqi = max(
            0,
            self.effective_max_douqi() - int(self.player["douqi"]),
        )
        candidates = []
        for item_id in self.player.get("items", []):
            item = self.item_rules.get(item_id, {})
            hp_gain = self._effect_gain(item.get("use_effect", ""), "hp")
            douqi_gain = self._effect_gain(item.get("use_effect", ""), "douqi")
            if hp_gain > 0 and missing_hp > 0 and self.check_conditions(item.get("use_condition")):
                effective = min(hp_gain, missing_hp) + min(douqi_gain, missing_douqi)
                candidates.append((item_id, effective, max(0, hp_gain - missing_hp)))
        return sorted(candidates, key=lambda value: (-value[1], value[2]))

    def choose_auto_combat_action(self) -> Tuple[str, Optional[str]]:
        if self.combat is None:
            return "none", None

        hp_ratio = self.player["hp"] / max(1, self.player["max_hp"])
        enemy_ratio = self.combat["hp"] / max(1, self.combat["max_hp"])
        enemy_damage = max(1, self.combat["atk"] - self.effective_def())
        healing_items = self._combat_healing_items()

        if healing_items and (hp_ratio <= 0.40 or self.player["hp"] <= enemy_damage * 2):
            return "item", healing_items[0][0]
        if not healing_items and self.player["hp"] <= enemy_damage:
            return "defend", None

        normal_damage = self._estimated_attack_damage()
        if normal_damage >= self.combat["hp"]:
            return "attack", None

        usable_skills = []
        for skill in self.combat_skills():
            bonus = self._skill_attack_bonus(skill["effect"])
            if bonus <= 0:
                continue
            cost = self._skill_cost(skill)
            if self.player["douqi"] < cost:
                continue
            finisher_threshold = FINISHER_SKILLS.get(skill["id"])
            if finisher_threshold is not None and enemy_ratio > finisher_threshold:
                continue
            damage = self._estimated_attack_damage(bonus, 1.25)
            # 保留最后一轮普通攻击所需的斗气余量，避免高消耗技能无意义溢伤。
            score = min(damage, self.combat["hp"]) / cost
            if damage >= self.combat["hp"]:
                score += 100
            if finisher_threshold is not None:
                score += 20
            usable_skills.append((score, skill["id"]))

        if usable_skills:
            return "skill", max(usable_skills)[1]
        if hp_ratio <= 0.30 and self.combat["hp"] > normal_damage * 2:
            return "defend", None
        return "attack", None

    def auto_battle(self, max_rounds: int = 200) -> str:
        if self.combat is None:
            self.last_message = "当前没有正在进行的战斗。"
            return "none"
        battle_logs = ["自动战斗开始"]
        result = "continue"
        for _ in range(max_rounds):
            action, target = self.choose_auto_combat_action()
            if action == "none":
                break
            result = self.combat_action(action, target)
            battle_logs.append(self.last_message)
            if result != "continue":
                break
        if result == "continue":
            battle_logs.append("自动战斗达到回合上限，已暂停")
        self.last_message = "；".join(log for log in battle_logs if log)
        return result

    def _advance_to_next_action(self) -> str:
        """推进行动条直到有人能行动。返回 'player' 或 'enemy'。"""
        if self.combat is None:
            return "player"
        player_spd = self.effective_spd()
        enemy_spd = int(self.combat.get("spd", 5))
        # 敌人速度受 debuff 影响
        if self.combat.get("debuff_spd", 0) > 0:
            enemy_spd = max(1, enemy_spd - self.combat["debuff_spd"])

        for _ in range(1000):  # 安全上限
            self.combat["player_gauge"] += player_spd
            self.combat["enemy_gauge"] += enemy_spd

            p_ready = self.combat["player_gauge"] >= GAUGE_MAX
            e_ready = self.combat["enemy_gauge"] >= GAUGE_MAX

            if p_ready and e_ready:
                # 同时到达：SPD 高者先动
                if player_spd >= enemy_spd:
                    self.combat["player_gauge"] -= GAUGE_MAX
                    return "player"
                else:
                    self.combat["enemy_gauge"] -= GAUGE_MAX
                    return "enemy"

            if p_ready:
                self.combat["player_gauge"] -= GAUGE_MAX
                return "player"

            if e_ready:
                self.combat["enemy_gauge"] -= GAUGE_MAX
                return "enemy"

        return "player"  # 安全回退

    def _enemy_action(self) -> List[str]:
        """执行敌人 AI 行动。返回日志列表。"""
        combat = self.combat
        if combat is None:
            return []
        logs: List[str] = []
        enemy_intent = combat.get("intent", "attack")
        hp_ratio = combat["hp"] / max(1, combat["max_hp"])
        if combat.get("stunned", 0) > 0:
            combat["stunned"] -= 1
            logs.append(f"{combat['name']}被控制，无法行动")
            return logs

        if enemy_intent == "defend":
            enemy_damage = max(1, (combat["atk"] - self.effective_def() + random.randint(-2, 3)) // 2)
            logs.append(f"{combat['name']}转入防守姿态")
        elif enemy_intent == "skill":
            enemy_data = self.enemies.get(combat["enemy_id"], {})
            enemy_skills = enemy_data.get("skills", [])
            skill_bonus = 0
            skill_name = "强力斗技"
            if enemy_skills:
                chosen = random.choice(enemy_skills)
                skill_data = self.skills.get(chosen, {})
                skill_name = skill_data.get("name", chosen)
                skill_bonus = self._skill_attack_bonus(skill_data.get("effect", ""))
                if hp_ratio < 0.3 and len(enemy_skills) >= 2:
                    best = max(enemy_skills, key=lambda s: self._skill_attack_bonus(
                        self.skills.get(s, {}).get("effect", "")))
                    skill_data = self.skills.get(best, {})
                    skill_name = skill_data.get("name", best)
                    skill_bonus = self._skill_attack_bonus(skill_data.get("effect", ""))
            enemy_damage = max(
                1,
                int(combat["atk"] * 1.3) + skill_bonus - self.effective_def() + random.randint(-1, 5),
            )
            logs.append(f"{combat['name']}施展了「{skill_name}」！")
            combat["combo"] = 0
        else:
            enemy_damage = max(1, combat["atk"] - self.effective_def() + random.randint(-2, 3))
            logs.append(f"{combat['name']}发起攻击")
        if combat.get("blind", 0) > 0:
            combat["blind"] -= 1
            if random.randint(1, 100) <= 50:
                enemy_damage = 0
                logs.append(f"{combat['name']}因失明而攻击落空")

        # 玩家闪避判定
        dodge_rate = (
            int(self.player.get("dodge_rate", 5))
            + self._technique_effect_value("dodge_rate")
            + self.timed_status_value("dodge_rate")
        )
        if random.randint(1, 100) <= dodge_rate:
            enemy_damage = 0
            logs.append(f"✨ 你灵巧地躲过了{combat['name']}的攻击！")
        elif combat.get("defending"):
            enemy_damage = max(1, enemy_damage // 2)
            logs.append("防御姿态减免了伤害")

        if enemy_damage > 0:
            resist = self._technique_damage_resistance(combat.get("element", ""))
            enemy_damage = max(1, int(enemy_damage * max(0.2, 1.0 - resist / 100.0)))
            shield = combat.get("player_shield", 0)
            if shield > 0:
                absorbed = min(shield, enemy_damage)
                combat["player_shield"] = shield - absorbed
                enemy_damage -= absorbed
                logs.append(f"功法护盾吸收{absorbed}伤害")
            self.player["hp"] = max(0, self.player["hp"] - enemy_damage)
            logs.append(f"{combat['name']}造成 {enemy_damage} 点伤害")
            thorns = self._technique_effect_value("thorns")
            thorns += self._technique_effect_value("thorns_damage")
            thorns += self.timed_status_value("thorns")
            if thorns > 0 and enemy_damage > 0:
                reflected = max(1, enemy_damage * thorns // 100)
                combat["hp"] = max(0, combat["hp"] - reflected)
                logs.append(f"功法反震造成{reflected}伤害")
            if self._technique_effect_value("thorns_poison") > 0 and enemy_damage > 0:
                combat["poison"] = min(7, combat.get("poison", 0) + 1)
                combat["poison_dmg"] = max(3, combat.get("poison_dmg", 3))
                logs.append("功法反震附加中毒")
        else:
            logs.append(f"{combat['name']}的攻击落空了！")

        # 更新敌人下回合意图
        hp_ratio_new = combat["hp"] / max(1, combat["max_hp"])
        if hp_ratio_new < 0.3:
            combat["intent"] = random.choice(["attack", "defend", "skill", "skill"])
        elif hp_ratio_new < 0.6:
            combat["intent"] = random.choice(["attack", "attack", "defend", "skill"])
        else:
            combat["intent"] = random.choice(["attack", "attack", "attack", "defend"])

        return logs

    def combat_usable_items(self) -> List[str]:
        """返回当前战斗中可直接使用的物品。"""
        usable = []
        combat_prefixes = (
            "hp:+", "douqi:+", "inflict_poison:", "sleep:", "blind:",
            "freeze:", "paralyze:", "escape:", "shield:", "damage_shield",
            "hp_regen:", "douqi_regen:", "element_boost:", "thorns:",
            "lifesteal:", "resist:", "temp_buff:", "auto_revive",
        )
        for item_id in self.player.get("items", []):
            effect = self.item_rules.get(item_id, {}).get("use_effect", "")
            if effect.startswith(combat_prefixes):
                usable.append(item_id)
        return usable

    def _use_combat_item(self, item_id: str) -> Tuple[bool, List[str]]:
        """在战斗中执行物品效果。"""
        if self.combat is None or item_id not in self.player.get("items", []):
            return False, []
        item = self.item_rules.get(item_id, {})
        effect = item.get("use_effect", "")
        logs: List[str] = []
        hp_gain = self._effect_gain(effect, "hp")
        douqi_gain = self._effect_gain(effect, "douqi")
        handled = False
        if hp_gain > 0:
            before = self.player["hp"]
            self.player["hp"] = min(self.effective_max_hp(), before + hp_gain)
            logs.append(f"恢复 {self.player['hp'] - before} 点生命")
            handled = True
        if douqi_gain > 0:
            before = self.player["douqi"]
            self.player["douqi"] = min(self.effective_max_douqi(), before + douqi_gain)
            logs.append(f"恢复 {self.player['douqi'] - before} 点斗气")
            handled = True

        match = re.match(r"inflict_poison:(\d+),(\d+)", effect)
        if match:
            stacks, damage = map(int, match.groups())
            self.combat["poison"] = min(7, self.combat.get("poison", 0) + stacks)
            self.combat["poison_dmg"] = max(self.combat.get("poison_dmg", 0), damage)
            logs.append(f"敌人中毒{stacks}层，每回合受到{damage}伤害")
            handled = True
        match = re.match(r"(sleep|freeze|paralyze):(\d+)", effect)
        if match:
            status, turns = match.groups()
            self.combat["stunned"] = self.combat.get("stunned", 0) + int(turns)
            logs.append(f"敌人陷入{status}，封锁{turns}次行动")
            handled = True
        match = re.match(r"blind:(\d+)", effect)
        if match:
            turns = int(match.group(1))
            self.combat["blind"] = max(self.combat.get("blind", 0), turns)
            logs.append(f"敌人失明{turns}回合")
            handled = True
        match = re.match(r"escape:(\d+)", effect)
        if match:
            chance = int(match.group(1))
            if self.combat.get("can_escape") and random.randint(1, 100) <= chance:
                self.player["items"].remove(item_id)
                self.combat = None
                logs.append("成功脱离战斗")
                return True, logs
            logs.append("脱离战斗失败")
            handled = True
        match = re.match(r"shield:(\d+)", effect)
        if match:
            shield = int(match.group(1))
            self.combat["player_shield"] = self.combat.get("player_shield", 0) + shield
            logs.append(f"获得{shield}点护盾")
            handled = True
        if effect == "damage_shield":
            self.combat["player_shield"] = self.combat.get("player_shield", 0) + self.effective_max_hp()
            logs.append("获得可抵挡一次重击的护盾")
            handled = True
        timed_logs = self._apply_timed_item_effect(effect)
        if timed_logs:
            logs.extend(timed_logs)
            handled = True
        if effect == "auto_revive":
            self.add_timed_status("auto_revive", 1, 99, "重生之羽")
            logs.append("本场战斗可自动复活一次")
            handled = True
        if handled:
            self.player["items"].remove(item_id)
            logs.insert(0, f"使用{item.get('name', item_id)}")
        return handled, logs

    def combat_action(self, action: str, skill_id: Optional[str] = None) -> str:
        if self.combat is None:
            return "none"
        combat = self.combat
        logs: List[str] = []
        combat["defending"] = False
        soul = int(self.player.get("soul", 0))
        logs.extend(self._tick_timed_statuses())
        logs.extend(self._technique_combat_turn_start())

        # ── 中毒伤害（回合开始时触发）──
        if combat.get("poison", 0) > 0:
            poison_dmg = combat.get("poison_dmg", 3)
            combat["hp"] = max(0, combat["hp"] - poison_dmg)
            logs.append(f"☠️ 中毒伤害 -{poison_dmg}")
            combat["poison"] = combat["poison"] - 1
            if combat["poison"] <= 0:
                combat.pop("poison", None)
                combat.pop("poison_dmg", None)
        if combat.get("burn", 0) > 0:
            burn_dmg = combat.get("burn_dmg", 1)
            combat["hp"] = max(0, combat["hp"] - burn_dmg)
            combat["burn"] -= 1
            logs.append(f"灼烧伤害 -{burn_dmg}")

        if action == "escape":
            chance = 0.35 + max(0, self.player["spd"] - combat["spd"]) * 0.02
            chance += self._technique_effect_value("escape_bonus") / 100.0
            if combat["can_escape"] and random.random() < min(0.9, chance):
                self.combat = None
                self.advance_time(getattr(self, "combat_time_cost", 0))
                self.last_message = "你抓住空隙脱离了战斗。"
                return "escaped"
            logs.append("你试图撤退，但被对方拦下")
            combat["combo"] = 0
        elif action == "item":
            item_id = skill_id or "item_elixir"
            used, item_logs = self._use_combat_item(item_id)
            if not used:
                self.last_message = "该物品无法在战斗中使用。"
                return "invalid"
            logs.extend(item_logs)
            if self.combat is None:
                self.advance_time(getattr(self, "combat_time_cost", 0))
                self.last_message = "；".join(logs)
                return "escaped"
            combat["combo"] = 0
        elif action == "defend":
            combat["defending"] = True
            logs.append("你凝聚斗气防守")
            combat["combo"] = 0
        elif action == "charge":
            if combat.get("charge_used"):
                self.last_message = "本场战斗已无法再次蓄力。"
                return "invalid"
            combat["charged"] = True
            combat["combo"] = 0
            self.player["douqi"] = min(
                self.effective_max_douqi(),
                self.player["douqi"] + CHARGE_DOUQI_PER_TURN,
            )
            logs.append(f"你凝神蓄力，斗气恢复 {CHARGE_DOUQI_PER_TURN} 点，下一击将威力倍增！")
        else:
            # ── 攻击（普攻/斗技） ──
            bonus = 0
            multiplier = 1.0

            # 当前使用的元素
            current_element = ""
            if action == "skill":
                current_element = SKILL_ELEMENTS.get(skill_id or "", "")

            # ── 元素同系连击增益 ──
            last_element = combat.get("last_element", "")
            element_streak = combat.get("element_streak", 0)
            if current_element and current_element == last_element:
                element_streak += 1
                streak_mult = ELEMENTAL_RULES["same_element_combo"].get(str(element_streak), 1.0)
                if streak_mult > 1.0:
                    multiplier *= streak_mult
                    logs.append(f"✨ {current_element}系{element_streak}连击！伤害x{streak_mult:.1f}")
            else:
                element_streak = 1
            # ── 跨元素组合效果 ──
            if current_element and last_element and current_element != last_element:
                cross_key = f"{last_element}+{current_element}"
                cross_effect = ELEMENTAL_RULES["cross_element_effects"].get(cross_key)
                if cross_effect:
                    multiplier *= cross_effect["mult"]
                    logs.append(f"💫 元素组合【{cross_effect['name']}】！伤害x{cross_effect['mult']:.1f}")
            combat["last_element"] = current_element
            combat["element_streak"] = element_streak

            # 蓄力加成
            if combat.get("charged"):
                multiplier *= CHARGE_DAMAGE_MULTIPLIER
                combat["charged"] = False
                combat["charge_used"] = True
                logs.append("⚡ 蓄力一击，威力倍增！")

            # 连击加成
            combo = combat.get("combo", 0)
            combo_mult = 1.0 + min(combo, COMBO_MAX) * COMBO_DAMAGE_PER_STACK
            if combo >= 2:
                logs.append(f"🔥 {combo}连击！伤害+{int((combo_mult - 1) * 100)}%")
            multiplier *= combo_mult

            if action == "skill":
                skill = self.skills.get(skill_id or "")
                if skill is None:
                    self.last_message = "尚未掌握该斗技。"
                    return "invalid"
                cost = self._skill_cost(skill)
                if self.player["douqi"] < cost:
                    self.last_message = "斗气不足，无法施展该斗技。"
                    return "invalid"
                self.player["douqi"] -= cost
                bonus = self._skill_attack_bonus(skill["effect"])
                bonus += int(self.effective_atk() * 0.5)
                # Skill level bonus
                lv_mult, lv_crit, lv = self._skill_level_bonus(skill["id"])
                multiplier *= 1.25 * lv_mult
                self._record_skill_use(skill["id"])
                logs.extend(self._apply_utility_skill_effect(skill, lv))
                if lv >= 3:
                    logs.append(f"Lv{lv} skill! dmg x{lv_mult:.1f}")
                logs.append(f"你施展了{skill['name']}（{SKILL_ELEMENTS.get(skill['id'], '?')}属性）")
                finisher_threshold = FINISHER_SKILLS.get(skill["id"])
                enemy_ratio = combat["hp"] / max(1, combat["max_hp"])
                if finisher_threshold is not None and enemy_ratio <= finisher_threshold:
                    multiplier *= 2
                    logs.append("斗技命中虚弱破绽，触发暴击！")

                # ── 属性克制判断 ──
                skill_element = SKILL_ELEMENTS.get(skill["id"], "")
                multiplier *= self._technique_element_power(skill_element)
                enemy_weakness = combat.get("weakness", "")
                if skill_element and skill_element == enemy_weakness:
                    multiplier *= 1.5
                    logs.append(f"💥 属性克制！{skill_element}克{combat.get('element', '?')}")
                    if not combat.get("shield_broken"):
                        combat["shield_broken"] = True
                        multiplier *= 1.3
                        logs.append(f"🛡️ 击破{combat['name']}的元素护盾！")
            else:
                # 普通攻击也有微弱元素效果
                logs.append(f"你挥拳攻向{combat['name']}")

            # 破盾后的额外伤害
            if combat.get("shield_broken"):
                multiplier *= 1.1

            enemy_def = combat["def"]
            mastery_crit = 0
            crit_multiplier = 2.0
            if action == "skill":
                penetration_key = {
                    "火": "fire_penetration", "冰": "ice_penetration",
                    "雷": "thunder_penetration", "风": "wind_penetration",
                    "木": "wood_penetration", "土": "earth_penetration",
                    "毒": "poison_penetration",
                }.get(SKILL_ELEMENTS.get(skill_id or "", ""), "")
                penetration = self._technique_effect_value(penetration_key)
                enemy_def = int(enemy_def * max(0.0, 1.0 - penetration / 100.0))
                multiplier, enemy_def, mastery_crit, crit_multiplier = (
                    self._apply_skill_mastery_before_damage(
                        skill, lv, multiplier, enemy_def
                    )
                )
            damage = max(
                1,
                int((self.effective_atk() + bonus) * multiplier)
                - enemy_def
                + random.randint(-2, 3),
            )
            # 暴击判定
            crit_rate = (
                int(self.player.get("crit_rate", 5))
                + self._technique_effect_value("crit_rate")
                + self.timed_status_value("crit_rate")
                + (lv_crit if action == "skill" else 0)
                + mastery_crit
            )
            was_crit = False
            if random.randint(1, 100) <= crit_rate:
                was_crit = True
                damage = int(damage * crit_multiplier)
                logs.append("💥 暴击！伤害翻倍！")
            actual_damage = min(damage, combat["hp"])
            combat["hp"] = max(0, combat["hp"] - actual_damage)
            logs.append(f"对{combat['name']}造成 {actual_damage} 点伤害")
            lifesteal = self.timed_status_value("lifesteal")
            if lifesteal > 0 and actual_damage > 0:
                healed = max(1, actual_damage * lifesteal // 100)
                self.player["hp"] = min(self.effective_max_hp(), self.player["hp"] + healed)
                logs.append(f"吸血恢复 {healed} 生命")
            if action == "skill":
                logs.extend(
                    self._apply_skill_mastery_after_damage(
                        skill, lv, cost, actual_damage
                    )
                )
                logs.extend(
                    self._apply_technique_skill_procs(
                        SKILL_ELEMENTS.get(skill_id or "", ""), was_crit
                    )
                )

            # 中毒判定：毒属性技能命中施加中毒
            if action == "skill":
                se = SKILL_ELEMENTS.get(skill_id or "", "")
                if se == "毒":
                    extra_stacks = max(0, self._technique_effect_value("poison_stacks"))
                    poison_stacks = combat.get("poison", 0) + 1 + extra_stacks
                    combat["poison"] = min(poison_stacks, 7 if lv >= 3 else 5)
                    combat["poison_dmg"] = (
                        3 + int(self.player.get("poison", 0)) // 10
                        + self._technique_effect_value("poison_dmg")
                    )
                    logs.append(f"☠️ 中毒 +{combat['poison_dmg']}/回合 ({combat['poison']}层)")

            # 连击递增
            combat["combo"] = combo + 1

        # ── 胜负判定 ──
        if combat["hp"] <= 0:
            logs.extend(self._finish_combat_win())
            self.last_message = "；".join(logs)
            return "won"

        # ── 灵魂感知：意图预判 ──
        enemy_intent = combat.get("intent", "attack")
        if soul >= 20:
            intent_names = {"attack": "攻击", "defend": "防御", "skill": "斗技", "charge": "蓄力"}
            logs.append(f"👁️ 灵魂感知：{combat['name']}意图[{intent_names.get(enemy_intent, '?')}]")

        # ── 行动条：推进直到玩家回合 ──
        while True:
            next_actor = self._advance_to_next_action()
            if next_actor == "enemy":
                enemy_logs = self._enemy_action()
                logs.extend(enemy_logs)
                # 玩家死亡判定
                if self.player["hp"] <= 0:
                    if self.timed_status_value("auto_revive") > 0:
                        self.player["timed_statuses"].pop("auto_revive", None)
                        self.player["hp"] = max(1, self.effective_max_hp() // 2)
                        logs.append("重生之羽生效，你恢复了一半生命")
                        continue
                    revive_chance = self._technique_effect_value("revive_chance")
                    if (
                        revive_chance > 0
                        and not combat.get("technique_revived")
                        and random.randint(1, 100) <= revive_chance
                    ):
                        combat["technique_revived"] = True
                        self.player["hp"] = max(1, self.effective_max_hp() // 3)
                        logs.append("功法护住心脉，你恢复了三分之一生命")
                        continue
                    self.player["hp"] = max(1, self.attribute_rules["hp"]["initial"] // 3)
                    self.player["last_map"] = "map_wutan"
                    self.combat = None
                    self.advance_time(getattr(self, "combat_time_cost", 0))
                    logs.append("你失去意识，被送回乌坦城休养")
                    self.last_message = "；".join(logs)
                    return "lost"
                continue
            else:  # player
                combat["round"] += 1
                self.last_message = "；".join(logs)
                return "continue"

    def _finish_combat_win(self) -> List[str]:
        if self.combat is None:
            return []
        combat = self.combat
        logs = [f"你击败了{combat['name']}"]
        logs.extend(self.apply_effects(f"exp:+{combat['exp_reward']},reputation:+1"))
        self.player["adventure_points"] += 2
        if getattr(self, "combat_is_training", False):
            self.player["training_wins"] += 1
        if combat["drop_table"]:
            drops = combat["drop_table"].split("|")
            for drop in drops:
                parts = drop.split(":")
                if len(parts) == 3 and random.randint(1, 100) <= int(parts[2]):
                    if parts[0] == "item":
                        item_id = parts[1]
                        if item_id not in self.player["items"]:
                            self.player["items"].append(item_id)
                        logs.append(f"获得{self.item_name(item_id)}")
                    elif parts[0] in self.attribute_rules:
                        logs.extend(self.apply_effects(f"{parts[0]}:+{parts[1]}"))
        # ── 击败追踪 + 掉落等级偏移 + 野兽掉落 ──
        enemy_id = combat.get("enemy_id", "")
        if enemy_id and not self._is_story_enemy(enemy_id):
            self.player["defeated_enemies"][enemy_id] = self._current_period()

        enemy_type = combat.get("type", "mob")
        if enemy_type in ("boss", "final_boss"):
            tier_shift = 3  # Boss: always high-tier
        elif enemy_type == "elite":
            tier_shift = 1  # Elite: 90% mid, 10% high
        else:
            tier_shift = 0  # Mob: mid and below

        enemy_level = int(combat.get("level", 1))
        if self._is_beast_enemy(enemy_id):
            extra_drops = self._random_beast_loot(enemy_level, count=random.randint(1, 3),
                                                   tier_shift=tier_shift,
                                                   enemy_type=enemy_type)
        else:
            extra_drops = self._random_loot(enemy_level, count=random.randint(0, 2),
                                            tier_shift=tier_shift,
                                            enemy_type=enemy_type)
        for drop_id in extra_drops:
            if drop_id not in self.player["items"]:
                self.player["items"].append(drop_id)
            logs.append(f"获得{self.item_name(drop_id)}")
        self.combat = None
        self.advance_time(getattr(self, "combat_time_cost", 0))
        return logs

    @staticmethod
    def _tier_for_level(level: int) -> str:
        """根据等级返回对应的装备/道具层级ID。"""
        tiers = [
            ("iron", 1, 9), ("refined", 10, 19), ("spirit", 20, 29),
            ("treasure", 30, 39), ("earth", 40, 49), ("heaven", 50, 59),
            ("mystic", 60, 69), ("saint", 70, 79), ("emperor", 80, 89),
            ("divine", 90, 100),
        ]
        for tid, lo, hi in tiers:
            if lo <= level <= hi:
                return tid
        return "iron"

    ALL_TIERS = ["iron","refined","spirit","treasure","earth","heaven","mystic","saint","emperor","divine"]

    RARITY_MULTIPLIERS = {
        "common": 1.0, "uncommon": 1.2, "rare": 1.5,
        "epic": 1.8, "legendary": 2.2, "mythic": 3.0,
    }
    RARITY_BY_TYPE = {
        "final_boss": {"mythic": 10, "legendary": 25, "epic": 35, "rare": 20, "uncommon": 10},
        "boss":       {"legendary": 8, "epic": 22, "rare": 30, "uncommon": 30, "common": 10},
        "elite":      {"epic": 5, "rare": 15, "uncommon": 30, "common": 50},
        "mob":        {"rare": 5, "uncommon": 15, "common": 80},
    }

    @staticmethod
    def _roll_rarity(enemy_type: str) -> str:
        dist = GameEngine.RARITY_BY_TYPE.get(enemy_type, {"common": 100})
        r = random.randint(1, 100)
        cum = 0
        for rarity, chance in dist.items():
            cum += chance
            if r <= cum:
                return rarity
        return "common"

    @staticmethod
    def _rarity_stat_multiplier(rarity: str) -> float:
        return GameEngine.RARITY_MULTIPLIERS.get(rarity, 1.0)

    @staticmethod
    def _random_loot(enemy_level: int, count: int = 1, tier_shift: int = 0,
                     enemy_type: str = "mob") -> List[str]:
        """从层级掉落池中随机抽取。tier_shift: boss=3, elite=1, mob=0。

        Boss: always higher tier. Elite: 10% higher, 90% base.
        Mob: 90% base-or-lower, 10% higher.
        """
        tier = GameEngine._tier_for_level(enemy_level)
        all_tiers = GameEngine.ALL_TIERS
        tier_idx = all_tiers.index(tier) if tier in all_tiers else 0

        results = []
        for _ in range(count):
            if tier_shift >= 3:
                # Boss: always use elevated tier
                use_idx = min(len(all_tiers) - 1, tier_idx + 2)
            elif tier_shift >= 1:
                # Elite: 10% chance of +1 tier
                if random.random() < 0.10:
                    use_idx = min(len(all_tiers) - 1, tier_idx + 1)
                else:
                    use_idx = tier_idx
            else:
                # Mob: 10% chance of +1, otherwise base or lower
                if random.random() < 0.10:
                    use_idx = min(len(all_tiers) - 1, tier_idx + 1)
                else:
                    use_idx = max(0, tier_idx)
            use_tier = all_tiers[use_idx]
            pool = LOOT_TABLE.get(use_tier, LOOT_TABLE.get(tier, []))
            if not pool:
                continue
            # Rarity filter for equipment
            rolled_rarity = GameEngine._roll_rarity(enemy_type)
            rare_pool = [(pid, w) for pid, w in pool
                         if not pid.startswith("eq_") or
                         EQUIPMENT_DATA.get(pid, {}).get("rarity", "common") == rolled_rarity]
            if not rare_pool:
                rare_pool = pool
            ids = [p[0] for p in rare_pool]
            weights = [p[1] for p in rare_pool]
            total_w = sum(weights)
            if total_w <= 0:
                continue
            r = random.randint(1, total_w)
            cum = 0
            for i, w in enumerate(weights):
                cum += w
                if r <= cum:
                    results.append(ids[i])
                    break
        return results

    def story_requirement(self) -> int:
        phase = self.current_story_phase()
        if phase is None:
            return 0
        if self.current_story_subnode() is not None:
            return max(1, int(phase["requirement"]) // 2)
        return int(phase["requirement"])

    def _sync_story_phase_id(self) -> None:
        stage = int(self.player.get("story_stage", 0))
        self.player["story_phase_id"] = (
            STORY_PHASES[stage]["id"] if stage < len(STORY_PHASES) else ""
        )

    def current_story_phase(self) -> Optional[Dict[str, Any]]:
        stage = int(self.player.get("story_stage", 0))
        return STORY_PHASES[stage] if stage < len(STORY_PHASES) else None

    def current_story_subnode(self) -> Optional[Dict[str, Any]]:
        phase = self.current_story_phase()
        if phase is None:
            return None
        substage = int(self.player.get("story_substage", 0))
        return phase["subnodes"][substage] if substage < len(phase["subnodes"]) else None

    def advance_story(self) -> bool:
        if not self._can_take_free_action():
            return False
        phase = self.current_story_phase()
        if phase is None:
            self.last_message = "主要目标已经全部完成。"
            return False
        requirement = self.story_requirement()
        if self.player["adventure_points"] < requirement:
            self.last_message = (
                f"还缺少 {requirement - self.player['adventure_points']} 点冒险阅历。"
                "请通过探索、修炼或战斗积累。"
            )
            return False
        subnode = self.current_story_subnode()
        if subnode is not None:
            if not self.check_conditions(subnode.get("condition")):
                self.last_message = (
                    f"子节点“{subnode['title']}”尚未达成：{subnode['condition']}。"
                    "完成方式可以自由选择。"
                )
                return False
            self.player["adventure_points"] -= requirement
            self.player["story_substage"] += 1
            logs = self.apply_effects(subnode.get("effect"))
            self.last_message = f"子节点完成：{subnode['title']}"
            if logs:
                self.last_message += "；" + "；".join(logs)
            self.advance_time()
            return True
        if not self.check_conditions(phase.get("condition")):
            self.last_message = (
                f"尚未达到“{phase['title']}”的目标条件：{phase['condition']}。"
                "你可以自由探索、修炼和建立关系后再来。"
            )
            return False
        self.player["adventure_points"] -= requirement
        self.player["story_stage"] += 1
        self.player["story_substage"] = 0
        self._sync_story_phase_id()
        logs = self.apply_effects(phase.get("effect"))
        self.last_message = f"关键目标完成：{phase['title']}"
        if logs:
            self.last_message += "；" + "；".join(logs)
        self.advance_time()
        return True

    def item_name(self, item_id: str) -> str:
        return self.item_rules.get(item_id, {}).get("name", item_id)

    # ── 装备系统 ─────────────────────────────────────────────

    def get_equipped_bonus(self, stat: str) -> int:
        """返回已装备物品对指定属性的总加成。"""
        equipped = self.player.get("equipped", {})
        total = 0
        for slot, item_id in equipped.items():
            if item_id and item_id in EQUIPMENT_DATA:
                total += EQUIPMENT_DATA[item_id].get(stat, 0)
        return total

    TECHNIQUE_EFFECT_PATTERN = re.compile(r"^([a-z_]+):([+-]?\d+)(%?)$")

    def _parse_technique_effect(self, effect_str: str) -> Dict[str, Tuple[int, bool]]:
        """解析功法效果 DSL，返回 {stat: (value, is_percent)}。"""
        result: Dict[str, Tuple[int, bool]] = {}
        if not effect_str:
            return result
        for token in effect_str.split(","):
            token = token.strip()
            m = self.TECHNIQUE_EFFECT_PATTERN.match(token)
            if m:
                stat = m.group(1)
                value = int(m.group(2))
                is_pct = bool(m.group(3))
                result[stat] = (value, is_pct)
        return result

    def _technique_stat_bonus(self, stat: str) -> int:
        """Sum bonuses from fixed + second technique."""
        total = 0
        for tid in [self.player.get("fixed_technique"),
                     self.player.get("second_technique")]:
            if not tid:
                continue
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
            if not tech:
                continue
            effects = self._parse_technique_effect(tech.get("effect", ""))
            bonus, is_pct = effects.get(stat, (0, False))
            if not is_pct:
                total += bonus
        return total

    def _technique_stat_multiplier(self, stat: str) -> float:
        """Product of multipliers from both techniques."""
        total = 1.0
        for tid in [self.player.get("fixed_technique"),
                     self.player.get("second_technique")]:
            if not tid:
                continue
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
            if not tech:
                continue
            effects = self._parse_technique_effect(tech.get("effect", ""))
            bonus, is_pct = effects.get(stat, (0, False))
            if is_pct:
                total *= (1.0 + bonus / 100.0)
        return total

    def _technique_effect_value(self, stat: str) -> int:
        """汇总两部已装备功法的指定效果，百分比和固定值均按数值相加。"""
        total = 0
        for tid in [self.player.get("fixed_technique"),
                    self.player.get("second_technique")]:
            if not tid:
                continue
            tech = next((t for t in TECHNIQUE_DATA if t["id"] == tid), None)
            if tech:
                total += self._parse_technique_effect(
                    tech.get("effect", "")
                ).get(stat, (0, False))[0]
        return total

    def _technique_element_power(self, element: str) -> float:
        key = {
            "火": "fire_power", "冰": "ice_power", "雷": "thunder_power",
            "风": "wind_power", "木": "wood_power", "土": "earth_power",
            "毒": "poison_power",
        }.get(element)
        technique_bonus = self._technique_effect_value(key) if key else 0
        status_bonus = self.timed_status_value(f"element_power_{element}")
        status_bonus += self.timed_status_value("element_power_all")
        return 1.0 + (technique_bonus + status_bonus) / 100.0

    def _technique_damage_resistance(self, element: str) -> int:
        key = {
            "火": "fire_resist", "冰": "ice_resist",
            "雷": "thunder_resist", "风": "wind_resist",
            "木": "wood_resist", "土": "earth_resist",
            "毒": "poison_resist",
        }.get(element, "")
        return (
            self._technique_effect_value("all_resist")
            + self._technique_effect_value(key)
            + self.timed_status_value(f"resist_{element}")
        )

    def _technique_combat_turn_start(self) -> List[str]:
        """兑现功法的开场、回复与敌方领域类效果。"""
        if self.combat is None:
            return []
        combat = self.combat
        logs: List[str] = []
        if not combat.get("technique_opened"):
            combat["technique_opened"] = True
            shield = self._technique_effect_value("shield_start")
            shield += self._technique_effect_value("ice_armor")
            if shield > 0:
                combat["player_shield"] = combat.get("player_shield", 0) + shield
                logs.append(f"功法护体：开场获得{shield}护盾")
            combat["def"] = max(
                0, int(combat["def"] * self._technique_stat_multiplier("enemy_def"))
            )
            slowed_spd = int(combat["spd"] * self._technique_stat_multiplier("enemy_spd"))
            combat["debuff_spd"] = max(
                combat.get("debuff_spd", 0), combat["spd"] - slowed_spd
            )
        hp_regen = self._technique_effect_value("hp_regen")
        douqi_regen = self._technique_effect_value("douqi_regen")
        if hp_regen > 0:
            self.player["hp"] = min(self.effective_max_hp(), self.player["hp"] + hp_regen)
            logs.append(f"功法运转：恢复{hp_regen}生命")
        if douqi_regen > 0:
            self.player["douqi"] = min(
                self.effective_max_douqi(), self.player["douqi"] + douqi_regen
            )
            logs.append(f"功法运转：恢复{douqi_regen}斗气")
        return logs

    def _apply_technique_skill_procs(self, element: str, was_crit: bool) -> List[str]:
        """兑现功法中依赖技能命中的连击与控制类特殊效果。"""
        if self.combat is None:
            return []
        combat = self.combat
        logs: List[str] = []
        combo_key = {
            "火": "fire_combo", "冰": "ice_combo", "雷": "thunder_combo",
            "风": "wind_combo", "木": "wood_combo", "土": "earth_combo",
            "毒": "poison_combo",
        }.get(element)
        extra_combo = self._technique_effect_value(combo_key) if combo_key else 0
        if extra_combo > 0:
            combat["combo"] = combat.get("combo", 0) + extra_combo
            logs.append(f"功法共鸣：额外获得{extra_combo}层连击")

        control_chance = 0
        if element == "冰":
            control_chance = self._technique_effect_value("freeze_chance")
        elif element == "雷":
            control_chance = self._technique_effect_value("stun_chance")
        elif element == "木":
            control_chance = self._technique_effect_value("wood_bind_chance")
        elif element == "土":
            control_chance = self._technique_effect_value("earth_shock_chance")
        if control_chance > 0 and random.randint(1, 100) <= control_chance:
            duration = 1 + max(0, self._technique_effect_value("freeze_duration"))
            combat["stunned"] = combat.get("stunned", 0) + duration
            logs.append(f"功法控制触发：敌人被封锁{duration}次行动")

        slow_chance = self._technique_effect_value("earth_slow_chance")
        if element == "土" and slow_chance > 0 and random.randint(1, 100) <= slow_chance:
            combat["debuff_spd"] = max(
                combat.get("debuff_spd", 0), max(1, combat["spd"] // 5)
            )
            logs.append("功法触发：敌人速度降低")

        if was_crit and self._technique_effect_value("crit_poison") > 0:
            combat["poison"] = min(7, combat.get("poison", 0) + 1)
            logs.append("功法触发：暴击附加中毒")
        return logs

    def _flame_stat_bonus(self, stat: str) -> int:
        """读取已装备异火的属性加成。"""
        fid = self.player.get("equipped_flame")
        if not fid:
            return 0
        flame = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == fid), None)
        if not flame:
            return 0
        tier = flame.get("tier", "iron")
        bonus_table = FLAME_TIER_BONUS.get(tier, {})
        return bonus_table.get(stat, 0)

    def _flame_alchemy_bonus(self, stat: str) -> int:
        """读取已装备异火的炼药加成。"""
        fid = self.player.get("equipped_flame")
        if not fid:
            return 0
        flame = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == fid), None)
        if not flame:
            return 0
        tier = flame.get("tier", "iron")
        bonus_table = FLAME_ALCHEMY_BONUS.get(tier, {})
        return bonus_table.get(stat, 0)

    def effective_spd(self) -> int:
        """计算玩家有效速度（基础+装备+功法+异火）。"""
        base = int(self.player.get("spd", 8))
        base += self.get_equipped_bonus("spd")
        base += self._technique_stat_bonus("spd")
        base += self._flame_stat_bonus("spd")
        mult = self._technique_stat_multiplier("spd")
        mult *= self._technique_stat_multiplier("all_spd")
        mult *= 1.0 + self.timed_status_value("spd_pct") / 100.0
        return max(1, int(base * mult))

    def _equipped_rarity_multiplier(self) -> float:
        """Best rarity multiplier from equipped items."""
        best = 1.0
        for slot, item_id in self.player.get("equipped", {}).items():
            if item_id and item_id in EQUIPMENT_DATA:
                rarity = EQUIPMENT_DATA[item_id].get("rarity", "common")
                mult = self._rarity_stat_multiplier(rarity)
                if mult > best:
                    best = mult
        return best

    def effective_atk(self) -> int:
        base = int(self.player.get("atk", 0)) + self.get_equipped_bonus("atk")
        base += self._technique_stat_bonus("atk")
        base += self._flame_stat_bonus("atk")
        rarity_mult = self._equipped_rarity_multiplier()
        mult = self._technique_stat_multiplier("atk")
        mult *= 1.0 + self.timed_status_value("atk_pct") / 100.0
        return max(1, int(base * mult * rarity_mult))

    def effective_def(self) -> int:
        base = int(self.player.get("def", 0)) + self.get_equipped_bonus("def")
        base += self._technique_stat_bonus("def")
        base += self._flame_stat_bonus("def")
        rarity_mult = self._equipped_rarity_multiplier()
        mult = self._technique_stat_multiplier("def")
        mult *= 1.0 + self.timed_status_value("def_pct") / 100.0
        return max(0, int(base * mult * rarity_mult))

    def effective_max_hp(self) -> int:
        base = int(self.player.get("max_hp", 100))
        base += self.get_equipped_bonus("hp")
        base += self._technique_stat_bonus("hp")
        base += self._flame_stat_bonus("hp")
        rarity_mult = self._equipped_rarity_multiplier()
        mult = self._technique_stat_multiplier("hp")
        return max(1, int(base * mult * rarity_mult))

    def effective_max_douqi(self) -> int:
        """计算玩家有效斗气上限（基础上限+功法固定/百分比加成）。"""
        base = int(self.attribute_rules["douqi"]["max"])
        base += self._technique_stat_bonus("douqi_max")
        return max(1, int(base * self._technique_stat_multiplier("douqi_max")))

    def equip_item(self, item_id: str) -> bool:
        """装备一件物品。返回是否成功。"""
        if item_id not in self.player.get("items", []):
            self.last_message = "背包中没有该物品。"
            return False
        eq = EQUIPMENT_DATA.get(item_id)
        if eq is None:
            self.last_message = "该物品无法装备。"
            return False
        slot = eq["slot"]
        equipped = self.player.setdefault("equipped", {"weapon": None, "armor": None, "accessory": None})
        # 卸下同槽位旧装备
        old = equipped.get(slot)
        if old:
            if old not in self.player["items"]:
                self.player["items"].append(old)
        equipped[slot] = item_id
        self.player["items"].remove(item_id)
        self.last_message = f"装备了{eq['name']}（{slot}）。"
        if old:
            self.last_message += f" 卸下了{EQUIPMENT_DATA.get(old, {}).get('name', old)}。"
        return True

    def unequip_item(self, slot: str) -> bool:
        """卸下指定槽位的装备。"""
        equipped = self.player.get("equipped", {})
        item_id = equipped.get(slot)
        if not item_id:
            self.last_message = f"{slot} 槽位没有装备。"
            return False
        equipped[slot] = None
        self.player["items"].append(item_id)
        name = EQUIPMENT_DATA.get(item_id, {}).get("name", item_id)
        self.last_message = f"卸下了{name}。"
        return True

    # ── 功法系统 ─────────────────────────────────────────────


    # Dual-slot equip/unequip defined above


    # ── 异火系统 ─────────────────────────────────────────────

    def equip_flame(self, flame_id: str) -> bool:
        """装备异火（提供战斗和炼药被动加成）。"""
        flame = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == flame_id), None)
        if flame is None:
            self.last_message = "找不到该异火。"
            return False
        if flame_id not in self.player.get("items", []):
            self.last_message = "背包中没有该异火。"
            return False
        old = self.player.get("equipped_flame")
        if old and old not in self.player.get("items", []):
            self.player.setdefault("items", []).append(old)
        self.player["items"].remove(flame_id)
        self.player["equipped_flame"] = flame_id
        self.player.setdefault("collected_flames", [])
        if flame_id not in self.player["collected_flames"]:
            self.player["collected_flames"].append(flame_id)
        tier_name = flame.get("tier", "iron")
        atk_bonus = FLAME_TIER_BONUS.get(tier_name, {}).get("atk", 0)
        self.last_message = f"装备异火：{flame['name']}（{tier_name}，攻击+{atk_bonus}）"
        return True

    def unequip_flame(self) -> bool:
        """卸下异火。"""
        fid = self.player.get("equipped_flame")
        if not fid:
            self.last_message = "当前未装备异火。"
            return False
        flame = next((f for f in HEAVENLY_FLAMES_FULL if f["id"] == fid), {})
        self.player["equipped_flame"] = None
        if fid not in self.player.get("items", []):
            self.player.setdefault("items", []).append(fid)
        self.last_message = f"收起异火：{flame.get('name', fid)}"
        return True

    LEARN_EFFECT_PATTERN = re.compile(r"^learn:(.+)$")

    # ── 炼药术系统（完整版：药鼎+丹方学习+逆向研究）─────

    def alchemy_grade_name(self) -> str:
        g = int(self.player.get("alchemy_grade", 1))
        return ALCHEMY_GRADES[g - 1] if 1 <= g <= 10 else "未入门"

    def alchemy_progress_text(self) -> str:
        g = int(self.player.get("alchemy_grade", 1))
        sub = int(self.player.get("alchemy_sub", 0))
        exp = int(self.player.get("alchemy_exp", 0))
        return f"{ALCHEMY_GRADES[g-1]}炼药师 [{sub+1}/10] {exp}/{ALCHEMY_EXP_PER_SUB}"

    def equip_furnace(self, furnace_id: str) -> bool:
        """装备药鼎。"""
        fdata = next((f for f in FURNACE_DATA if f["id"] == furnace_id), None)
        if fdata is None:
            self.last_message = "找不到该药鼎。"
            return False
        # 检查背包
        if furnace_id not in self.player.get("items", []):
            self.last_message = "背包中没有该药鼎。"
            return False
        # 卸下旧鼎
        old = self.player.get("equipped_furnace")
        if old:
            if old not in self.player["items"]:
                self.player["items"].append(old)
        self.player["items"].remove(furnace_id)
        self.player["equipped_furnace"] = furnace_id
        uses = self.player.get("furnace_uses", {})
        if furnace_id not in uses:
            uses[furnace_id] = 0
        self.last_message = f"装备了{fdata['name']}（{ALCHEMY_GRADES[fdata['grade']-1]}药鼎）"
        if fdata["max_uses"] > 0:
            self.last_message += f"，剩余使用次数：{fdata['max_uses'] - uses[furnace_id]}"
        return True

    def _get_furnace_data(self) -> dict:
        fid = self.player.get("equipped_furnace")
        if not fid:
            return {"bonus": 0, "grade": 0, "max_uses": 0, "special": "", "name": "无"}
        return next((f for f in FURNACE_DATA if f["id"] == fid), {"bonus": 0, "grade": 0, "max_uses": 0, "special": "", "name": "无"})

    def craft_pill(self, recipe_id: str) -> bool:
        """炼制丹药。需习得丹方、装备药鼎。"""
        recipe = next((r for r in ALCHEMY_RECIPES if r["id"] == recipe_id), None)
        if recipe is None:
            self.last_message = "无效的丹方ID。"
            return False
        if recipe["output"] in REMOVED_ITEM_IDS:
            self.last_message = "该丹方对应的道具系统已移除。"
            return False

        # 检查是否习得丹方
        if recipe_id not in self.player.get("known_recipes", []):
            self.last_message = "尚未习得该丹方，无法炼制。"
            return False

        # 检查药鼎
        fdata = self._get_furnace_data()
        if fdata["grade"] == 0:
            self.last_message = "没有药鼎！请先装备一个药鼎才能炼药。"
            return False

        # 检查药鼎使用次数
        fid = self.player.get("equipped_furnace")
        if fid and fdata["max_uses"] > 0:
            uses = self.player.get("furnace_uses", {})
            used = uses.get(fid, 0)
            if used >= fdata["max_uses"]:
                self.last_message = f"{fdata['name']}已因使用次数耗尽而损坏！请更换药鼎。"
                self.player["equipped_furnace"] = None
                return False

        pill_id = recipe["output"]
        req_grade = recipe["grade"]
        materials = recipe["materials"]
        base_rate = recipe["base_rate"]
        player_grade = int(self.player.get("alchemy_grade", 1))

        # 检查材料
        missing = []
        for mat_id, count in materials:
            have = self.player.get("items", []).count(mat_id)
            if have < count:
                missing.append(f"{self.item_name(mat_id)}x{count}(有{have})")
        if missing:
            self.last_message = f"材料不足：{'、'.join(missing)}"
            return False

        # 成功率：基础 + 品级差 + 药鼎加成 + 异火加成
        grade_diff = player_grade - req_grade
        flame_success = self._flame_alchemy_bonus("success")
        success_rate = min(98, max(3, base_rate + grade_diff * 8 + fdata["bonus"] // 2 + flame_success))

        # 消耗材料（圣鼎以上概率省材）
        for mat_id, count in materials:
            actual = count
            if "省材" in fdata["special"] and random.random() < 0.2:
                actual = max(1, count - 1)
            for _ in range(actual):
                self.player["items"].remove(mat_id)

        # 药鼎消耗次数
        if fid and fdata["max_uses"] > 0:
            uses = self.player.get("furnace_uses", {})
            uses[fid] = uses.get(fid, 0) + 1

        if random.randint(1, 100) <= success_rate:
            # 成功
            count_out = 1
            if "双倍" in fdata["special"] and random.random() < 0.1 + (0.1 if "20%" in fdata["special"] else 0) + (0.1 if "30%" in fdata["special"] else 0):
                count_out = 2
            for _ in range(count_out):
                if pill_id not in self.player["items"]:
                    self.player["items"].append(pill_id)
                else:
                    self.player["items"].append(pill_id)
            exp_gain = req_grade * 15 + random.randint(5, 15)
            if "经验" in fdata["special"]:
                exp_gain = int(exp_gain * 1.2)
            flame_exp = self._flame_alchemy_bonus("exp")
            exp_gain += flame_exp
            self._gain_alchemy_exp(exp_gain)
            msg = f"炼制成功！获得 {self.item_name(pill_id)}"
            if count_out > 1:
                msg += f" x{count_out}"
            msg += f"（成功率{success_rate}%）炼药经验+{exp_gain}"
            self.last_message = msg
            return True
        else:
            exp_gain = req_grade * 5
            self._gain_alchemy_exp(exp_gain)
            self.last_message = f"炼制失败…丹炉冒出黑烟（成功率{success_rate}%）炼药经验+{exp_gain}"
            return False

    def study_alchemy(self) -> bool:
        """研读丹方，获得少量炼药经验。"""
        exp_gain = 5 + random.randint(1, 10)
        self._gain_alchemy_exp(exp_gain)
        self.advance_time(1)
        self.last_message = f"研读丹方，炼药经验+{exp_gain} [{self.alchemy_progress_text()}]"
        return True

    def breakthrouth_alchemy(self) -> bool:
        g = int(self.player.get("alchemy_grade", 1))
        sub = int(self.player.get("alchemy_sub", 0))
        exp = int(self.player.get("alchemy_exp", 0))
        if g >= 10 and sub >= 9 and exp >= ALCHEMY_EXP_PER_SUB:
            self.last_message = "已是帝品炼药师，无需突破。"
            return False
        if sub < 9 or exp < ALCHEMY_EXP_PER_SUB:
            self.last_message = "当前进度经验未满，无法突破。"
            return False
        chance_bp = REALM_BREAKTHROUGH_CHANCE_BP.get(g, 1)
        success = random.randint(1, 10000) <= chance_bp
        self.advance_time(1)
        if success:
            self.player["alchemy_grade"] = g + 1
            self.player["alchemy_sub"] = 0
            self.player["alchemy_exp"] = 0
            self.last_message = f"突破成功！晋升{ALCHEMY_GRADES[g]}炼药师！（概率{chance_bp/100:.1f}%）"
        else:
            self.player["alchemy_sub"] = 9
            self.player["alchemy_exp"] = ALCHEMY_EXP_PER_SUB // 2
            self.last_message = f"突破失败…丹火反噬。（概率{chance_bp/100:.1f}%）"
        return success

    def _gain_alchemy_exp(self, amount: int) -> None:
        g = int(self.player.get("alchemy_grade", 1))
        sub = int(self.player.get("alchemy_sub", 0))
        exp = int(self.player.get("alchemy_exp", 0)) + amount
        while exp >= ALCHEMY_EXP_PER_SUB:
            exp -= ALCHEMY_EXP_PER_SUB
            sub += 1
            if sub >= ALCHEMY_SUB_PER_GRADE:
                sub = ALCHEMY_SUB_PER_GRADE - 1
                exp = ALCHEMY_EXP_PER_SUB
                break
        if g >= 10:
            sub = min(sub, ALCHEMY_SUB_PER_GRADE - 1)
            exp = min(exp, ALCHEMY_EXP_PER_SUB)
        self.player["alchemy_grade"] = g
        self.player["alchemy_sub"] = sub
        self.player["alchemy_exp"] = exp

    def available_recipes(self) -> List[dict]:
        """返回玩家已习得且品级可用的丹方列表。"""
        player_grade = int(self.player.get("alchemy_grade", 1))
        known = self.player.get("known_recipes", [])
        result = []
        for r in ALCHEMY_RECIPES:
            if r["output"] in REMOVED_ITEM_IDS:
                continue
            if r["id"] in known and r["grade"] <= player_grade + 1:
                grade_diff = player_grade - r["grade"]
                fdata = self._get_furnace_data()
                flame_success = self._flame_alchemy_bonus("success")
                success_rate = min(98, max(3, r["base_rate"] + grade_diff * 8 + fdata["bonus"] // 2 + flame_success))
                mat_names = [f"{self.item_name(mid)}x{c}" for mid, c in r["materials"]]
                result.append({
                    "id": r["id"], "name": r["name"],
                    "output": self.item_name(r["output"]),
                    "grade": r["grade"], "rate": success_rate,
                    "materials": mat_names, "mats_raw": r["materials"],
                })
        return result

    # ── 逆向研究 ─────────────────────────────────────────────

    def reverse_engineer(self, pill_item_id: str) -> bool:
        """逆向研究丹药——必定销毁丹药，概率识别一种材料。
        识别出全部材料后自动习得对应丹方。"""
        if pill_item_id in REMOVED_ITEM_IDS:
            self.last_message = "该道具系统已移除。"
            return False
        items = self.player.get("items", [])
        if pill_item_id not in items:
            self.last_message = "背包中没有该丹药。"
            return False

        # 找到该丹药对应的丹方
        recipe = next((r for r in ALCHEMY_RECIPES if r["output"] == pill_item_id), None)
        if recipe is None:
            self.last_message = "该丹药没有已知丹方可逆向。"
            return False

        rid = recipe["id"]
        # 如果已习得丹方，无需逆向
        if rid in self.player.get("known_recipes", []):
            self.last_message = "已习得该丹方，无需逆向研究。"
            return False

        # 必定销毁丹药
        self.player["items"].remove(pill_item_id)

        # 初始化逆向进度
        rp = self.player.setdefault("reverse_progress", {})
        if rid not in rp:
            rp[rid] = {"known": [], "total": [m[0] for m in recipe["materials"]]}
        progress = rp[rid]
        unknown = [m for m in progress["total"] if m not in progress["known"]]

        if not unknown:
            # 全部识别完毕，习得丹方
            self.player.setdefault("known_recipes", []).append(rid)
            rp.pop(rid, None)
            self.last_message = f"逆向研究成功！已习得丹方：{recipe['name']}（炼制{self.item_name(pill_item_id)}）"
            return True

        # 尝试识别一个未知材料（概率按材料tier递减）
        target_mat = random.choice(unknown)
        mat_item = self.item_rules.get(target_mat, {})
        mat_tier = mat_item.get("tier", "iron")
        tier_levels = {"iron": 1, "refined": 2, "spirit": 3, "treasure": 4,
                       "earth": 5, "heaven": 6, "mystic": 7, "saint": 8, "emperor": 9, "divine": 10}
        tlv = tier_levels.get(mat_tier, 1)
        identify_chance = max(5, 80 - tlv * 8)  # 铁器85% → 神阶5%

        if random.randint(1, 100) <= identify_chance:
            progress["known"].append(target_mat)
            exp_gain = tlv * 30 + random.randint(10, 20)
            self._gain_alchemy_exp(exp_gain)
            remaining = [m for m in progress["total"] if m not in progress["known"]]
            self.last_message = (
                f"逆向研究：识别出材料「{self.item_name(target_mat)}」！"
                f"（识别率{identify_chance}%）炼药经验+{exp_gain}"
                + (f" 剩余未知材料：{len(remaining)}种" if remaining else " 全部材料已识别！")
            )
            # 全部识别完毕
            if not remaining:
                self.player.setdefault("known_recipes", []).append(rid)
                rp.pop(rid, None)
                self.last_message += f"\n已自动习得丹方：{recipe['name']}！"
        else:
            exp_gain = tlv * 5
            self._gain_alchemy_exp(exp_gain)
            self.last_message = (
                f"逆向研究失败…丹药已毁，未能识别出任何新材料。"
                f"（识别率{identify_chance}%）炼药经验+{exp_gain}"
            )

        return True

    def get_reverse_progress(self, pill_item_id: str) -> Optional[dict]:
        """获取某丹药的逆向研究进度。"""
        recipe = next((r for r in ALCHEMY_RECIPES if r["output"] == pill_item_id), None)
        if recipe is None:
            return None
        rid = recipe["id"]
        rp = self.player.get("reverse_progress", {})
        if rid in rp:
            p = rp[rid]
            known_names = [self.item_name(m) for m in p["known"]]
            total_names = [self.item_name(m) for m in p["total"]]
            return {"known": known_names, "total": total_names, "recipe_name": recipe["name"]}
        return None

    def gift_targets(self) -> List[Dict[str, str]]:
        """返回当前可选择的赠礼目标。"""
        result = []
        for rule in self.relationship_rules.values():
            if not rule.get("visible", False):
                continue
            target = rule["target"]
            result.append({
                "id": target,
                "name": self.npc_names.get(target, target),
                "stage": self.relation_stage(target),
            })
        return result

    def give_gift(self, item_id: str, target: str) -> bool:
        """向指定关系目标赠送礼物。"""
        if item_id not in self.player.get("items", []):
            self.last_message = "背包中没有该礼物。"
            return False
        if self.item_rules.get(item_id, {}).get("use_effect") != "gift":
            self.last_message = "该物品不能用于赠礼。"
            return False
        if target not in {entry["id"] for entry in self.gift_targets()}:
            self.last_message = "当前无法向该人物赠礼。"
            return False
        tier = self.item_rules[item_id].get("tier", "iron")
        tier_values = {
            "iron": 2, "refined": 3, "spirit": 5, "treasure": 7,
            "earth": 9, "heaven": 12, "mystic": 15, "saint": 20,
            "emperor": 25, "divine": 30,
        }
        gain = tier_values.get(tier, 2)
        self.player["items"].remove(item_id)
        logs = self.change_relation_value(target, gain)
        self.last_message = f"向{self.npc_names.get(target, target)}赠送{self.item_name(item_id)}；" + "；".join(logs)
        return True

    def use_item(self, item_id: str, target: Optional[str] = None) -> bool:
        if item_id not in self.player["items"]:
            self.last_message = "背包中没有该道具。"
            return False
        item = self.item_rules.get(item_id)
        if item is None:
            self.last_message = "该道具不存在。"
            return False
        etype = item.get("type", "")
        effect = item.get("use_effect", "")
        if effect == "gift":
            if target is None:
                names = "、".join(entry["name"] for entry in self.gift_targets())
                self.last_message = f"请选择赠礼目标：{names}"
                return False
            return self.give_gift(item_id, target)
        # 药鼎装备
        if etype == "furnace":
            return self.equip_furnace(item_id)
        # 异火装备
        if etype == "heavenly_flame":
            return self.equip_flame(item_id)
        if etype == "storage_ring":
            return self.equip_storage_ring(item_id)
        # 功法书学习
        if etype == "technique":
            tid = item_id
            if tid.startswith("tech_"):
                self.player["items"].remove(item_id)
                return self.equip_technique(tid)
        # 技能书学习
        learn_match = self.LEARN_EFFECT_PATTERN.match(effect)
        if learn_match:
            skill_id = learn_match.group(1)
            if skill_id in self.player.get("known_skills", []):
                self.last_message = "已习得该斗技。"
                return False
            self.player["items"].remove(item_id)
            self.player.setdefault("known_skills", []).append(skill_id)
            skill_name = self.skills.get(skill_id, {}).get("name", skill_id)
            self.last_message = f"研读{item['name']}，习得斗技：{skill_name}！"
            return True
        # 通用物品使用
        if not item.get("use_effect"):
            self.last_message = "该道具当前不能直接使用。"
            return False
        if not self.check_conditions(item.get("use_condition")):
            self.last_message = "尚未满足该道具的使用条件。"
            return False
        timed_logs = self._apply_timed_item_effect(effect)
        if timed_logs:
            self.player["items"].remove(item_id)
            self.last_message = f"使用{item['name']}；" + "；".join(timed_logs)
            return True
        special_result = self._use_special_item_effect(item_id, item)
        if special_result is not None:
            return special_result
        snapshot = json.loads(json.dumps(self.player))
        try:
            logs = self.apply_effects(item["use_effect"])
        except (ValueError, KeyError, TypeError):
            self.player = snapshot
            self.last_message = f"{item['name']}的效果尚未接入，物品未消耗。"
            return False
        self.player["items"].remove(item_id)
        self.last_message = f"使用{item['name']}；" + "；".join(logs)
        return True

    def _use_special_item_effect(
        self, item_id: str, item: Dict[str, Any]
    ) -> Optional[bool]:
        """执行无需额外目标选择的特殊物品；未知效果返回 None。"""
        effect = item.get("use_effect", "")
        if effect.startswith("teleport:"):
            map_id = effect.split(":", 1)[1]
            if map_id not in self.maps or not self.is_map_unlocked(map_id):
                self.last_message = "目标区域尚未开放，传送道具未消耗。"
                return False
            map_name = self.maps[map_id].get("name", map_id)
            self.player["items"].remove(item_id)
            self.player["last_map"] = map_id
            self.active_encounter = None
            self.active_exploration = None
            self.last_message = f"使用{item['name']}，传送至{map_name}。"
            return True
        if effect.startswith("cure:"):
            status = effect.split(":", 1)[1]
            statuses = self.player.setdefault("active_statuses", [])
            if status in statuses:
                statuses.remove(status)
            self.player["items"].remove(item_id)
            self.last_message = f"使用{item['name']}，清除了{status}状态。"
            return True
        if effect == "remove_curse":
            statuses = self.player.setdefault("active_statuses", [])
            self.player["active_statuses"] = [
                status for status in statuses if "curse" not in status.lower()
            ]
            self.player["items"].remove(item_id)
            self.last_message = f"使用{item['name']}，诅咒已被净化。"
            return True
        if effect == "expand_inventory":
            self.player["items"].remove(item_id)
            self.player["inventory_capacity"] = self.inventory_capacity() + 10
            self.last_message = f"使用{item['name']}，背包容量增加10格。"
            return True
        if effect == "random_reward":
            self.player["items"].remove(item_id)
            reward = random.randint(50, 250)
            self.player["wallet"] = wallet_add(self.player.get("wallet", {}), reward)
            self.last_message = f"打开{item['name']}，获得{reward}铜币。"
            return True
        return None

    def is_ending(self) -> bool:
        return self.current_story_phase() is None

    # ── 背包容量 ─────────────────────────────────────────────

    def inventory_used(self) -> int:
        return len(self.player.get("items", []))

    def inventory_capacity(self) -> int:
        return int(self.player.get("inventory_capacity", BASE_INVENTORY_CAPACITY))

    def can_add_item(self) -> bool:
        return self.inventory_used() < self.inventory_capacity()

    def add_item_safe(self, item_id: str) -> bool:
        """安全添加物品，背包满则放入溢出区。"""
        if self.inventory_used() < self.inventory_capacity():
            self.player["items"].append(item_id)
            return True
        else:
            self.player.setdefault("storage_overflow", []).append(item_id)
            self.last_message = "背包已满，物品已暂存溢出区（请扩容或清理背包）"
            return False

    def equip_storage_ring(self, ring_id: str) -> bool:
        """使用纳戒扩容背包（支持多戒指累加容量）。"""
        ring = next((r for r in STORAGE_RINGS if r["id"] == ring_id), None)
        if ring is None:
            self.last_message = "这不是纳戒。"
            return False
        if ring_id not in self.player.get("items", []):
            self.last_message = "背包中没有该纳戒。"
            return False
        self.player["items"].remove(ring_id)
        # 累加到已装备纳戒列表
        old_rings = self.player.get("equipped_storage_rings", [])
        old_rings.append(ring_id)
        self.player["equipped_storage_rings"] = old_rings
        # 重新计算总容量
        total_cap = BASE_INVENTORY_CAPACITY + sum(
            (next((r for r in STORAGE_RINGS if r["id"] == rid), {})).get("capacity", 0)
            for rid in old_rings
        )
        self.player["inventory_capacity"] = total_cap
        # 溢出区上限处理
        overflow = self.player.get("storage_overflow", [])
        if len(overflow) > MAX_STORAGE_OVERFLOW:
            lost = len(overflow) - MAX_STORAGE_OVERFLOW
            overflow = overflow[:MAX_STORAGE_OVERFLOW]
            self.player["storage_overflow"] = overflow
            self.last_message = f"警告：溢出区已达上限，{lost}件物品已丢失。"
        # 从溢出区移入
        moved = 0
        while overflow and self.inventory_used() < self.inventory_capacity():
            self.player["items"].append(overflow.pop(0))
            moved += 1
        self.player["storage_overflow"] = overflow
        total_ring_cap = total_cap - BASE_INVENTORY_CAPACITY
        self.last_message = (
            f"使用{ring['name']}，纳戒总容量+{total_ring_cap}格（背包{total_cap}格）"
            + (f"，从溢出区移入{moved}件物品" if moved else "")
        )
        return True

    # ── 拍卖行 ───────────────────────────────────────────────

    def refresh_auction(self, map_id: str = "") -> List[Dict[str, Any]]:
        """刷新拍卖行商品（按当前地图等级生成高价稀有物品）。"""
        if not map_id:
            map_id = self.player.get("last_map", "map_wutan")
        md = self.maps.get(map_id, {})
        map_level = md.get("recommend_level", 1)

        player_listings = [
            item for item in self.auction_listings if item.get("player_sold")
        ]
        listings = []
        # 高tier物品池
        player_level = int(self.player.get("level", 1))
        target_tier = self._tier_for_level(max(map_level, player_level))
        # 偏向高tier
        all_tiers = ["iron","refined","spirit","treasure","earth","heaven","mystic","saint","emperor","divine"]
        tier_idx = all_tiers.index(target_tier) if target_tier in all_tiers else 3

        pool = []
        # 装备
        for eid, eq in _GEN_EQUIPMENT.items():
            et = eq.get("tier", "iron")
            eti = all_tiers.index(et) if et in all_tiers else 0
            if eti >= tier_idx - 1 and eti <= tier_idx + 2:  # 当前tier±范围
                pool.append((eid, eq["name"], "equipment", eq))
        # 消耗品/材料/异火
        for iid, item_def in self.item_rules.items():
            it = item_def.get("tier", "iron")
            eti = all_tiers.index(it) if it in all_tiers else 0
            itype = item_def.get("type", "")
            if eti >= tier_idx - 1 and eti <= tier_idx + 2:
                if itype in ("consumable","material","heavenly_flame","book","technique","storage_ring","furnace"):
                    pool.append((iid, item_def.get("name", iid), itype, item_def))

        # 随机抽取
        if pool:
            picks = random.sample(pool, min(AUCTION_LISTING_COUNT, len(pool)))
            for pid, pname, ptype, pdata in picks:
                base_price = pdata.get("price_buy", 100) if isinstance(pdata, dict) else 100
                markup = random.uniform(AUCTION_MARKUP_MIN, AUCTION_MARKUP_MAX)
                price = max(100, int(base_price * markup))
                time_left = random.randint(2, 6)
                # 顶级物品（tier>=saint）或异火：使用远古币
                itier = (pdata.get("tier","") if isinstance(pdata, dict) else "")
                use_ancient = (itier in ("saint","emperor","divine") or ptype == "heavenly_flame") and random.random() < 0.3
                currency = "ancient" if use_ancient else "copper"
                if use_ancient:
                    price = max(1, price // 100000)  # 转为远古币价格
                listings.append({
                    "id": pid, "name": pname, "type": ptype,
                    "price": price, "time_left": time_left, "currency": currency,
                })

        self.auction_listings = player_listings + listings
        self.auction_last_map = map_id
        self.auction_last_period = int(self.player.get("time_period", 0)) + int(self.player.get("day", 1)) * 4
        return listings

    def get_auction_listings(self, map_id: str = "") -> List[Dict[str, Any]]:
        """获取当前拍卖行商品（过期自动下架并刷新）。"""
        if not map_id:
            map_id = self.player.get("last_map", "map_wutan")
        current_period = int(self.player.get("time_period", 0)) + int(self.player.get("day", 1)) * 4
        # 换地图或过时段自动刷新
        if (map_id != self.auction_last_map or
            current_period - self.auction_last_period >= AUCTION_REFRESH_PERIODS or
            not self.auction_listings):
            return self.refresh_auction(map_id)
        return self.auction_listings

    def _advance_auction_time(self, periods: int) -> None:
        """仅在游戏时间推进时结算拍卖倒计时与 NPC 购买。"""
        for _ in range(periods):
            expired = []
            for item in self.auction_listings:
                item["time_left"] = item.get("time_left", 0) - 1
                if item["time_left"] <= 0:
                    expired.append(item)
            for item in expired:
                if item.get("player_sold") and item.get("id"):
                    self.add_item_safe(item["id"])
                self.auction_listings.remove(item)
            self._npc_auction_cycle()

    def _npc_auction_cycle(self) -> None:
        """NPC对拍卖行物品的兴趣——时段驱动自动购买玩家上架品。"""
        if not self.auction_listings:
            return
        player_sold = [(i, item) for i, item in enumerate(self.auction_listings)
                       if item.get("player_sold")]
        if player_sold and random.random() < 0.3:
            idx, item = random.choice(player_sold)
            npc_price = max(1, int(item["price"] * random.uniform(0.6, 0.9)))
            self.player["wallet"] = wallet_add(self.player.get("wallet", {}), npc_price)
            bought_name = item.get("name", "物品")
            self.auction_listings.pop(idx)
            self.last_special = f"拍卖行：NPC以 {npc_price} 铜币买走了您上架的「{bought_name}」！"

    def auction_buy(self, listing_index: int) -> bool:
        """从拍卖行购买物品。"""
        listings = self.get_auction_listings()
        if listing_index < 0 or listing_index >= len(listings):
            self.last_message = "无效的商品编号。"
            return False
        item = listings[listing_index]
        currency = item.get("currency", "copper")
        wallet = self.player.get("wallet", {})
        if not self.can_add_item():
            self.last_message = "背包已满，无法购买。"
            return False
        if currency == "ancient":
            if wallet.get("ancient", 0) < item["price"]:
                self.last_message = f"远古币不足！需要 {item['price']} 远古币。"
                return False
            wallet["ancient"] -= item["price"]
        else:
            if not wallet_can_afford(wallet, item["price"]):
                self.last_message = f"资金不足！需要 {item['price']} 铜币。"
                return False
            self.player["wallet"] = wallet_add(wallet, -item["price"])
        self.add_item_safe(item["id"])
        self.auction_listings.pop(listing_index)
        unit = "远古币" if currency == "ancient" else "铜币"
        self.last_message = f"以 {item['price']} {unit}拍得 {item['name']}！"
        return True

    def auction_sell(self, item_index: int, price: int) -> bool:
        """将背包物品上架拍卖行。"""
        inv = self.player.get("items", [])
        if item_index < 0 or item_index >= len(inv):
            self.last_message = "无效的物品编号。"
            return False
        if price < 1:
            self.last_message = "价格必须大于0。"
            return False
        item_id = inv[item_index]
        rule = self.item_rules.get(item_id, {})
        self.player["items"].pop(item_index)
        self.auction_listings.append({
            "id": item_id, "name": self.item_name(item_id),
            "type": rule.get("type", "misc"),
            "price": price, "time_left": 6, "player_sold": True,
        })
        self.last_message = f"已将 {self.item_name(item_id)} 上架拍卖行，标价 {price} 银两。"
        return True

    def is_finished(self) -> bool:
        return self.is_ending()

    def status_text(self) -> str:
        core_attributes = [
            "level",
            "exp",
            "hp",
            "douqi",
            "atk",
            "def",
            "spd",
            "wallet",
            "reputation",
            "alchemy",
            "soul",
        ]
        attribute_text = "｜".join(
            f"{self.attribute_rules[key]['name']} {self.player[key]}"
            for key in core_attributes
            if key in self.attribute_rules
        )
        relationships = []
        for rule in self.relationship_rules.values():
            if not rule.get("visible", False):
                continue
            if rule.get("pre_condition") and not self.check_conditions(
                rule["pre_condition"]
            ):
                continue
            target = rule["target"]
            target_name = self.npc_names.get(target, target)
            relationships.append(
                f"{target_name} {self.relation_value(target)}"
                f"({self.relation_stage(target)})"
            )
        relationship_text = "、".join(relationships) or "无"
        items = "、".join(self.player.get("items", [])) or "无"
        flags = "、".join(self.player.get("flags", [])) or "无"
        node = self.next_schedule_node()
        schedule = (
            f"\n日程：{node['title']}（{self.schedule_countdown_text(node)}）"
            if node
            else ""
        )
        return (
            f"{self.player['name']}｜{self.realm_name()} Lv.{self.player['level']}｜"
            f"进度 {self.player['progress']:.2f}%｜{attribute_text}\n"
            f"{self.time_text()}｜所在区域：{self.current_map()['name']}｜"
            f"冒险阅历 {self.player['adventure_points']}"
            f"｜关键阶段 {self.player['story_stage']}/{len(STORY_PHASES)}"
            f"｜阶段子节点 {self.player['story_substage']}/"
            f"{len(self.current_story_phase()['subnodes']) if self.current_story_phase() else 0}\n"
            f"道具：{items}\n持续效果：{self.timed_status_text()}\n开关：{flags}\n关系：{relationship_text}{schedule}"
        )
