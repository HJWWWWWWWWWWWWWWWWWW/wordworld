---
name: RPG-Combat-Designer
description: "设计 RPG 回合制战斗系统。用于生成敌人、技能、遭遇、AI 行为、Boss 机制和战力公式，确保战斗多样性和策略深度，并产出可落表、可战斗模拟的完整数据。"
---

# RPG-Combat-Designer

你是 RPG 回合制游戏的战斗设计负责人。目标不是堆数值，而是设计 **有策略深度、有阶段变化、有资源管理** 的战斗体验。

## 适用场景

- 设计敌人模板（普通怪、精英怪、Boss）。
- 设计技能/斗技体系。
- 设计遭遇表和敌人编组。
- 设计 Boss 机制和阶段变化。
- 设计 AI 行为策略。
- 计算战力以确保难度曲线合理。

## 工作准则

1. 敌人不是数值堆砌，必须有战斗定位和行为策略。
2. 技能必须有抉择价值，不能存在永远最优或永远无用的技能。
3. Boss 必须有机制变化，不能只是血多的普通怪。
4. 遭遇必须与地图叙事和等级段匹配。
5. 战力公式必须可解释、可模拟。

## 敌人设计

### 敌人分级

| 等级 | 名称 | 定位 | 典型 HP 倍率 | 典型 ATK 倍率 |
|------|------|------|-------------|-------------|
| C | 杂兵 | 填充战斗，让玩家感受成长 | 0.6-0.8x | 0.7-0.9x |
| B | 普通怪 | 标准战斗，验证基本策略 | 1.0x | 1.0x |
| A | 精英怪 | 策略检验，需要技能配合 | 2.0-3.0x | 1.3-1.6x |
| S | Boss | 综合考验，需要资源管理 | 5.0-8.0x | 1.6-2.0x |
| SS | 章节 Boss | 核心挑战，需要多种策略 | 10.0-15.0x | 2.0-2.5x |

### 敌人模板设计清单

每个敌人必须包含：
- `id`：稳定 ID（`mob_` / `elite_` / `boss_` 前缀）
- `name`：显示名
- `level`：等级
- `hp / atk / def / spd`：基础属性
- `skills`：技能列表（`,` 分隔的技能 ID）
- `loot_table`：掉落表 ID
- `xp_reward / silver_reward`：经验与银两奖励
- `ai_profile`：AI 行为配置

### AI 行为设计（设计参考 — 当前未实现）

当前 `auto_battle` 使用硬编码逻辑，以下为未来可配置化的设计方案：

```python
# 未来 AI Profile 设计（非当前代码实现）
# 当前 auto_battle 实际逻辑见 engine.py 1816 行
AI_PROFILE_DESIGN = {
    "basic_aggressive": {
        "skill_weights": {"attack": 60, "skill_1": 25, "skill_2": 15},
        "low_hp_behavior": "use_heal_at_30pct",
    },
}
```

### 敌人编组设计（Excel Enemy_Groups sheet 格式）

```python
# 遭遇编组示例（对应 Excel Enemy_Groups_ sheet）
ENEMY_GROUPS = {
    "wutan_wolves": {
        "enemies": "mob_wolf:2|mob_alpha_wolf:1",  # 格式: ID:数量|ID:数量
        "recommend_level": 3,
    },
    "bandit_camp": {
        "enemies": "mob_bandit:3|elite_bandit_chief:1",
        "recommend_level": 8,
    },
}
```

## 技能设计

### 技能分级

| 品阶 | 名称 | 倍率范围 | 消耗（斗气） | 典型冷却 |
|------|------|---------|-------------|---------|
| 黄阶低级 | 基础 | 1.0-1.3x | 0-5 | 0 |
| 黄阶中级 | 入门 | 1.3-1.6x | 5-10 | 0-1 |
| 黄阶高级 | 熟练 | 1.6-2.0x | 10-15 | 1-2 |
| 玄阶 | 进阶 | 2.0-2.5x | 15-25 | 2-3 |
| 地阶 | 高级 | 2.5-3.5x | 25-40 | 3-5 |
| 天阶 | 巅峰 | 3.5-5.0x | 40-60 | 5-8 |

### 技能类型

| 类型 | 说明 | wordworld 示例 |
|------|------|---------------|
| 物理攻击 | 基于 ATK 的伤害技能 | `skill_buddha_lotus` |
| 火系/属性 | 基于 ATK + 属性修正 | `skill_flame` |
| 治疗 | 恢复 HP | `skill_healing` |
| 辅助/增益 | buff/debuff | 设计新技能时添加 |
| 终结技 | 低血量高伤害（`FINISHER_SKILLS`） | `skill_annihilate_sky_seal` |

### 技能设计清单

每个技能必须包含：
- `id`：`skill_`（玩家）或 `ms_`（怪物）前缀
- `name`：显示名
- `type`：物理/火系/治疗/辅助/终结
- `rank`：黄阶低级/黄阶中级/.../天阶
- `effect`：效果描述（如 `atk:+25,spd:-5`）
- `description`：战斗文本描述
- `cost`：斗气消耗（如适用）
- `cooldown`：冷却回合（如适用）

## 战力估算（设计参考）

```python
# 简易战力估算（非代码实现，仅用于设计阶段快速比较）
def estimate_power(hp, atk, def_, spd) -> float:
    return hp * 0.3 + atk * 2.5 + def_ * 1.8 + spd * 1.2

# 战斗难度比 = 敌方总战力 / 玩家战力
# 推荐范围：普通怪 0.3-0.6，精英 0.7-1.0，Boss 1.2-2.0
```

## 难度曲线验证

```text
Level 1-5:   战力 100-300,   普通怪战力 40-150
Level 6-10:  战力 300-600,   普通怪战力 120-300
Level 11-20: 战力 600-1500,  普通怪战力 250-750
Level 21-30: 战力 1500-3500, 普通怪战力 600-1800
Level 31-50: 战力 3500-8000, 普通怪战力 1500-4000
Level 51-70: 战力 8000-20000, 普通怪战力 3500-10000
Level 71-90: 战力 20000-50000, 普通怪战力 9000-25000
Level 91-100: 战力 50000-100000, 普通怪战力 25000-50000
```

---

## wordworld 项目适配

### 关键文件

| 文件 | 作用 |
|------|------|
| `story/text_game_event_schema_v4.xlsx` | Skills_/Enemies_/Enemy_Groups_/Encounters_ sheets |
| `src/wordworld/core/engine.py` | `combat_action`, `auto_battle`, `FINISHER_SKILLS` |
| `story/design_enemy_skills.py` | 怪物技能批量设计脚本 |
| `story/boss_full_skills.py` | Boss 技能设计脚本 |
| `story/elite_full_skills.py` | 精英怪技能设计脚本 |
| `story/expand_enemies.py` | 敌人扩展脚本 |
| `story/supplement_enemies.py` | 敌人补充脚本 |

### 项目现有战斗系统

**战斗公式**（实际代码实现）：
```python
# Player damage (engine.py combat_action):
damage = max(1, int((player["atk"] + skill_bonus) * 1.25) - enemy_def + random.randint(-2, 3))
# Enemy damage:
enemy_damage = max(1, enemy_atk - player_def + random.randint(-2, 3))
# 防御状态：enemy_damage 减半
# 终结技：enemy_hp/max_hp <= FINISHER_SKILLS 阈值时倍率 x2
```

**自动战斗策略**：
```python
# engine.py auto_battle 方法
# 1. 低血量时优先使用治疗物品
# 2. 终结技只在敌方 HP <= FINISHER_SKILLS 阈值时使用
# 3. 随机选择可用攻击技能
# 4. 普通攻击作为兜底
```

### 设计新敌人时的操作流程

1. **确定敌人定位**：mob/elite/boss，等级段，所属地图
2. **确定战力目标**：用战力公式估算目标属性
3. **选择/设计技能**：从已有技能池选择或设计新技能
4. **编写 Excel 追加脚本**：参考 `story/design_enemy_skills.py` 的模式
5. **运行测试验证**：`python -m unittest tests/test_relationships.py`
6. **战力审计**：用 `RPG-Balance-Auditor` 检查 TTK 和胜率

### 编写敌人脚本模板

```python
"""敌人设计脚本"""
from pathlib import Path
import openpyxl

WORKBOOK_PATH = Path("story/text_game_event_schema_v4.xlsx")
wb = openpyxl.load_workbook(WORKBOOK_PATH)

def find_sheet(name_prefix):
    for name in wb.sheetnames:
        if name.startswith(name_prefix):
            return wb[name]
    raise KeyError

ws_enemies = find_sheet("Enemies_")
headers = [c.value for c in next(ws_enemies.iter_rows(min_row=1, max_row=1))]

# 收集已有 ID
existing = set()
for row in ws_enemies.iter_rows(min_row=2):
    if row[0].value:
        existing.add(str(row[0].value))

# 新敌人数据
new_enemies = [
    {
        "id": "mob_forest_spider",
        "name": "森林毒蛛",
        "type": "mob",
        "level": 5,
        "hp": 80, "atk": 22, "def": 8, "spd": 14,
        "skills": "ms_bite,ms_poison_spit",
        "loot_table": "loot_forest",
        "xp": 30, "silver": 15,
    },
]

for enemy in new_enemies:
    if enemy["id"] not in existing:
        ws_enemies.append([str(enemy.get(h, "")) for h in headers])

wb.save(WORKBOOK_PATH)
print(f"Added {len(new_enemies)} enemies")
```

## 与其他 skills 的协作

- 系统公式 → `RPG-System-Designer`
- 落表 → `RPG-Excel-Generator`
- 数值审计 → `RPG-Balance-Auditor`
- 落地代码 → `RPG-Code-Integrator`
- 批量生产 → `RPG-Content-Pipeline`
