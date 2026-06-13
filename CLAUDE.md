# CLAUDE.md — WordWorld（残火长明 RPG）

## 项目概述

原创玄幻世界观沉浸式回合制 RPG 游戏。玩家在据点修炼、探索地图、回合制战斗、推进剧情，逐步成长。当前为 v0.1-demo 原型阶段。

## 技术栈

- **语言**: Python 3.x（纯标准库，无第三方依赖）
- **测试**: `unittest`（`python -m unittest discover -s tests -v`）
- **数据格式**: Excel（`story/text_game_event_schema_v4.xlsx`），通过内置 XML 解析读取
- **GUI**: 基于 `tkinter` 的 TUI + 简化 GUI

## 项目结构

```
wordworld/
├── src/wordworld/
│   ├── core/engine.py       # 游戏引擎：战斗、修炼、剧情、关系、技能、掉落
│   ├── data/workbook.py     # Excel 配置解析与游戏数据加载
│   ├── ui/console.py        # 命令行主界面
│   ├── ui/tui.py            # 文本 UI（基于 tkinter 的终端风格界面）
│   ├── ui/gui.py            # 图形 UI
│   └── config/paths.py      # 路径常量（PROJECT_ROOT, STORY_DIR 等）
├── story/                   # 剧情脚本与 Excel 配置文件
├── saves/                   # 玩家存档（JSON）
├── tests/                   # 单元测试
├── docs/                    # 设计文档与审计报告
├── run.py                   # CLI 入口
├── run_gui.py               # GUI 入口
└── CLAUDE.md
```

## 核心架构

### GameEngine（`core/engine.py`）

全局状态机，统一入口。包含：

| 系统 | 职责 |
|------|------|
| 剧情推进 | STORY_PHASES（38 阶段 × 118 子节点），按条件解锁，不是逐章线性 |
| 战斗系统 | 回合制：普攻/灵技/防御/丹药/逃跑/自动战斗 |
| 属性系统 | 境界、等级、灵力、攻击力、防御力、灵魂力量 |
| 关系系统 | 角色好感度（rel_*），部分关系免疫事件影响 |
| 地图系统 | 134 张地图，按剧情阶段解锁 |
| 技能系统 | 等级里程碑解锁灵技（Lv10/20/30/40/50） |
| 装备系统 | 武器、防具、饰品，有稀有度 |
| 丹药系统 | 使用丹药回复生命/灵力 |
| 时间系统 | 四个时段（清晨/午后/傍晚/深夜），不同时段影响消耗与收益 |
| 掉落系统 | 战斗掉落：银两、道具、装备 |

### 数据流

```
story/*.xlsx  →  workbook.py  →  GameEngine  →  ui/console.py|tui.py|gui.py
                                       ↕
                                  saves/*.json
```

### DSL 指令系统

游戏动作和事件效果通过字符串 DSL 表达：
- `"exp:+250"` — 增加经验
- `"hp:-50"` — 减少生命
- `"rel:xun_er:+10"` — 好感度变化
- `"item:sword:1"` — 获得物品
- `"skill:flame"` — 学习技能

## 常用命令

```bash
# 运行游戏（CLI）
python run.py

# 运行游戏（GUI）
python run_gui.py

# 运行所有测试
python -m unittest discover -s tests -v

# 运行单个测试
python -m unittest tests.test_relationships -v
```

## 代码约定

- **编码**: UTF-8，中文注释和字符串直接使用
- **命名**: 常量 `UPPER_SNAKE_CASE`，函数/变量 `snake_case`
- **类型注解**: 使用 `typing` 模块（`Dict[str, Any]`, `List[...]`, `Optional[...]`）
- **导入顺序**: 标准库 → 项目内部模块
- **不可变性**: 优先用 `frozen=True` dataclass 或 `NamedTuple`，避免原地修改共享状态
- **测试**: `unittest.TestCase`，方法名 `test_xxx`，AAA 模式
- **游戏状态**: 全部保存在 `self.player` 字典中，通过 `apply_effects()` 统一修改
- **配置数据**: 从 Excel 动态读取，不硬编码数值

## 关键约束

1. **不要硬编码剧情文本** — 所有内容从 Excel 配置读取
2. **保持无第三方依赖** — 优先使用标准库
3. **修改 engine.py 后必须运行测试** — 游戏逻辑相互耦合
4. **关系系统** — `IMMUNE_RELATIONSHIPS` 中的关系不受事件影响
5. **境界系统** — 突破有概率，`REALM_BREAKTHROUGH_CHANCE_BP` 控制
6. **地图解锁** — 只随剧情阶段开放，等级不提前解锁区域
