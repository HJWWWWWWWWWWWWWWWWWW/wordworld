"""敌人配置中历史技能 ID 的兼容定义。"""

ENEMY_SKILL_FALLBACKS = {
    "skill_defensive_stance": ("防御姿态", "def:+25,atk:-10", "进入防御姿态提升生存能力。"),
    "skill_battle_cry": ("战吼", "atk:+18,def:+10", "战吼鼓舞自身战力。"),
    "skill_counter_strike": ("反击", "atk:+25", "格挡后瞬间反击。"),
    "skill_soul_shock": ("灵魂冲击", "atk:+30,soul:+10", "灵魂冲击造成精神伤害。"),
    "skill_emperor_will": ("帝之意志", "atk:+70,soul:+25", "以帝境意志压制对手。"),
    "skill_soul_rend": ("灵魂撕裂", "atk:+48,soul:+15", "撕裂目标灵魂。"),
    "skill_dragon_roar": ("龙吟", "atk:+40,soul:+10", "龙吟震慑目标灵魂。"),
    "skill_inferno": ("烈焰风暴", "atk:+30,spd:-5", "召唤烈焰风暴席卷战场。"),
    "skill_ancient_dragon_roar": ("远古龙吟", "atk:+80,soul:+30", "远古龙吟震荡灵魂。"),
    "skill_lightning_bolt": ("雷电术", "atk:+22,spd:+10", "召唤雷电劈击。"),
    "skill_thunder_clap": ("雷霆一击", "atk:+32,spd:+5", "雷属性强力一击。"),
    "skill_thunder_wrath": ("天雷怒降", "atk:+55,spd:+10", "召唤天雷之怒。"),
    "skill_demon_puppet": ("妖傀重击", "atk:+50,def:+15", "驱动妖傀发动沉重攻击。"),
    "skill_absolute_zero": ("绝对零度", "atk:+50,spd:-20", "将周围化为极寒炼狱。"),
    "skill_heavy_strike": ("重击", "atk:+16,spd:-5", "蓄力发动沉重一击。"),
    "skill_cyclone": ("旋风斩", "atk:+22,spd:+5", "旋转攻击周围目标。"),
    "skill_corrosive_acid": ("腐蚀酸液", "atk:+30,def:-10", "强酸腐蚀目标防御。"),
    "skill_meditate": ("冥想", "atk:+10,hp:+20", "冥想恢复状态并凝聚力量。"),
    "skill_shadow_strike": ("暗影突袭", "atk:+25,spd:+15", "从暗影中高速突袭。"),
}

