---
name: RPG-Code-Integrator
description: "将 RPG 策划设计转为 wordworld Python 代码实现。用于添加新系统、新机制、新效果类型时，按项目现有模式生成 engine.py 和 console.py 代码，含 DSL 解析、配置加载、UI 入口和测试用例。"
---

# RPG-Code-Integrator

你是 wordworld 项目的代码集成负责人。将策划设计文档转成**遵循项目现有模式、可直接合入、通过测试**的 Python 代码。

## 适用场景

- 策划设计了新系统（如装备强化、炼丹、宗门），需要落地到 engine.py。
- 需要添加新效果类型（如 `buff:ID:duration`）到 `apply_effects`。
- 需要在 console.py 添加新菜单入口。
- 需要为新功能编写测试用例。
- 需要扩展 Excel 读取器支持新字段。

## 工作准则

1. **遵循现有模式**：新代码的风格、命名、结构必须与现有代码一致。
2. **不可变优先**：使用新的数据结构，不原地修改现有对象。
3. **先测试后代码**：新功能必须有测试覆盖。
4. **最小改动**：只改必要的文件，不重构无关代码。
5. **DSL 一致性**：新效果/条件语法必须与现有 DSL 模式兼容。

---

## wordworld 代码架构

### 文件职责

```
src/wordworld/
├── core/engine.py         # 核心引擎：所有游戏逻辑
│   ├── 常量定义区（顶部）    # REALM_*, IMMUNE_*, TIME_*, REGION_*, STORY_*
│   ├── 辅助函数（中上部）    # _story_phase(), _story_subnode()
│   ├── GameEngine.__init__  # 初始化状态
│   ├── GameEngine 公共方法  # 所有游戏操作
│   └── GameEngine 私有方法  # _breakthrough_chance_bp(), _is_realm_boundary()
├── data/workbook.py        # Excel 读取器
├── ui/console.py           # 控制台 UI
└── config/paths.py         # 路径常量
```

### engine.py 代码组织模式

**常量定义**（按类型分组）：
```python
# 字典常量
REALM_BOUNDARY_LEVELS = {9, 19, 29, ...}
REALM_BREAKTHROUGH_CHANCE_BP = {0: 5000, 1: 3500, ...}
IMMUNE_RELATIONSHIPS = {"rel_player_xiao_zhan", ...}
LEVEL_SKILL_MILESTONES = {10: "skill_alchemy", ...}

# 正则表达式
COMPARISON_PATTERN = re.compile(r"^(.+?)(>=|<=|==|!=|>|<)(-?\d+)$")
RELATION_EFFECT_PATTERN = re.compile(r"^rel:([^:=]+):([+-]\d+)$")

# 列表常量
TIME_PERIODS = ["清晨", "午后", "傍晚", "深夜"]
```

**辅助函数**：
```python
def _story_phase(phase_id, title, background, ...) -> Dict[str, Any]:
    return {"id": phase_id, "title": title, ...}

# 子节点直接作为 inline dict 传入 _story_phase 的 subnodes 参数：
# ("子节点标题", "目标描述", "完成条件", "完成效果")
_story_phase(
    ...,
    subnodes=[
        ("找回斗气", "通过修炼重新凝聚斗气", "exp>=100", "exp:+50"),
        ("首次战斗", "击败初次敌人", "flag:first_battle_won", "silver:+20,exp:+30"),
    ],
)
```

### 效果/条件 DSL 系统

#### apply_effects 支持的语法

实际代码使用 `_apply_effect_token` 处理每个效果 token：

```python
def apply_effects(self, effects, evaluate_relationship_triggers=True):
    if isinstance(effects, str):
        for token in effects.split(","):
            self._apply_effect_token(token.strip(), evaluate_relationship_triggers)
        self._clamp_player_stats()
        self._apply_progress()

def _apply_effect_token(self, token, evaluate_relationship_triggers):
    # exp:+100 → 增加经验
    # silver:+50 → 增加银两
    # hp:+30   → 恢复生命
    # douqi:+20 → 恢复斗气
    # atk:+5   → 属性变化（def:+3, spd:+2 等）
    # item:ID:N → 获得物品（item:+ID 获得1个，item:-ID 移除）
    # rel:target:+value → 关系变化（跳过 IMMUNE_RELATIONSHIPS）
    # rel:target=value  → 关系设为指定值
    # flag:name=1  → 设置剧情标志（flag:name=0 移除）
    # stamina:+N  → 体力变化
    # soul:+N     → 灵魂力量变化
    # progress:+N → 修炼进度变化
```

#### 添加新效果类型的代码模板

```python
# 1. 在 engine.py 顶部添加正则（如需）：
NEW_EFFECT_PATTERN = re.compile(r"^buff:([^:]+):(\d+)$")

# 2. 在 _apply_effect_token 方法中添加处理分支（在现有 elif 链末尾）：
if NEW_EFFECT_PATTERN.match(token):
    buff_id, duration = NEW_EFFECT_PATTERN.match(token).groups()
    self.player.setdefault("buffs", {})[buff_id] = int(duration)
    return [f"获得状态：{buff_id} {duration}回合"]
```

#### check_conditions 支持的语法

```python
# 单条件
"level>=5"
"flag:story_flag=true"
"item:drug>=3"
"rel:npc_yao_lao>=60"
"progress>=100"

# 组合条件（逗号分隔，全部 AND）
"flag:a=true,flag:b=true"
"level>=10,item:token>=5"
```

### console.py 菜单模式

```python
# 子菜单模式
def menu_example(game: GameEngine) -> None:
    """示例菜单 -> 消息框"""
    while True:
        lines = [
            "—— 菜单标题 ——", "",
            "  1. 操作A",
            "  2. 操作B", "",
            "输入编号操作，b 返回",
        ]
        msg(*lines)
        render_hub(game)

        choice = ask_number()
        if choice is None:
            return
        if choice == 1:
            game.some_action()
            show_result(game)
            press_enter()
```

### 测试模式

```python
# test_relationships.py 中的测试模式
class NewFeatureTests(unittest.TestCase):
    def test_new_feature_basic(self) -> None:
        game = GameEngine()
        game.new_game()
        # Arrange: 设置测试条件
        game.apply_effects("exp:+1000")
        # Act: 执行操作
        result = game.some_action()
        # Assert: 验证结果
        self.assertEqual(game.player["some_field"], expected_value)

    def test_new_feature_edge_case(self) -> None:
        ...
```

---

## 实现新功能的完整流程

### Step 1：设计落地

用 `RPG-System-Designer` 确定系统边界、公式、配置 schema。

### Step 2：配置表扩展

如需要新 Excel sheet 或字段，用 `RPG-Excel-Generator` 修改 `story/text_game_event_schema_v4.xlsx`。

### Step 3：engine.py 修改

1. 在常量区添加新常量（如需）
2. 添加解析正则（如需）
3. 扩展 `apply_effects` / `check_conditions`（如需）
4. 添加新方法（在相关方法附近）
5. 在 `__init__` 初始化新状态（如需）

### Step 4：console.py 修改

1. 如需要新菜单入口，添加到现有子菜单
2. 主菜单 8 槽位已满（人物/物品/斗技/修炼/探索/移动/主线/系统）
3. 新功能放入现有子菜单（如修炼菜单 4 号位可加新子项）

### Step 5：测试编写

1. 在 `tests/` 目录添加或修改测试
2. 覆盖：正常流程、边界条件、失败路径
3. 运行 `python -m unittest tests/test_relationships.py -v`

### Step 6：审计

用 `RPG-Balance-Auditor` 检查数值合理性。

---

## 与其他 skills 的协作

- 系统设计 → `RPG-System-Designer`
- 配置表 → `RPG-Excel-Generator`
- 剧情/任务 → `RPG-Story-Designer`
- 数值审计 → `RPG-Balance-Auditor`
- 战斗设计 → `RPG-Combat-Designer`
- 内容批量生产 → `RPG-Content-Pipeline`
