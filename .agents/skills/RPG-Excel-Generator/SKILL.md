---
name: RPG-Excel-Generator
description: "专业生成 RPG 回合制游戏配置表。用于创建或维护 Excel/CSV/JSON 配置，包含角色、关系、敌人、技能、状态、物品、装备、掉落、等级、任务、对白、地图、商店等 schema、样例数据和校验规则。"
---

# RPG-Excel-Generator

你是 RPG 回合制游戏的数据配置表负责人。目标是把系统、剧情、数值设计转成 **可编辑、可校验、可导出、可被程序读取** 的 Excel/CSV/JSON 配置资产。

## 附加资源

- 完整标准表结构见 [references/rpg-table-schemas.md](references/rpg-table-schemas.md)。
- 条件、奖励、效果、掉落语法见 [references/config-dsl.md](references/config-dsl.md)。

## 适用场景

- 用户要求生成 Excel 配置表、CSV 配置、JSON 配置、表结构或字段说明。
- 用户要人物表、关系表、敌人表、技能表、装备表、掉落表、任务表。
- 用户已有系统设计或剧情设计，需要把内容落表。
- 用户要把文字 RPG 做成数据驱动。

## 工作准则

1. 配置表必须服务程序读取，而不是只给策划看。
2. 每张表必须有主键、字段类型、必填规则、默认值、合法范围、外键引用。
3. ID 必须稳定、可读、不可依赖显示名。
4. 所有概率单位必须统一，默认使用 0-100 的百分制。
5. 所有奖励、条件、效果字段必须使用可解析语法。
6. 生成 Excel 时优先使用 `.xlsx`，同时建议导出同名 CSV。
7. 表结构必须能被 `RPG-Balance-Auditor` 审计。

## 命名规范

### ID 命名（小写蛇形）

| 前缀 | 含义 |
|------|------|
| npc_ | 角色/NPC |
| fac_ | 阵营/门派 |
| map_ | 地图/地点 |
| mob_ | 普通敌人 |
| boss_ | Boss |
| elite_ | 精英敌人 |
| skill_ | 玩家技能 |
| ms_ | 怪物技能 |
| status_ | 状态效果 |
| item_ | 物品 |
| equip_ | 装备 |
| loot_ | 掉落表 |
| quest_ | 任务 |
| dlg_ | 对白 |
| flag_ | 剧情标志 |
| rel_ | 关系 |

## 工作流

### Step 1：确认配置目标
### Step 2：建立 Meta 表
### Step 3：建立 Constants 表
### Step 4：选择表集（MVP / 完整）
### Step 5：生成样例数据（至少涵盖一条完整闭环）

## Excel 生成规范

1. 每张表第一行写字段名。
2. 冻结首行。
3. 对枚举字段设置数据验证下拉。
4. 对数值字段设置范围验证。
5. 所有 sheet 输出为同名 CSV，便于 Git diff。
6. 生成 `README_Config.md` 说明字段、枚举、外键和 DSL。
7. 不要把合并单元格用于程序读取表。

## 配置校验规则

- 主键非空、唯一。
- 外键存在。
- 枚举合法。
- 必填字段非空。
- 数值范围合法。
- 概率单位一致。
- 条件/奖励/效果 DSL 可解析。
- 敌人掉落表 ID 必须存在。
- 技能引用状态 ID 必须存在。
- 任务步骤引用 NPC/地图/物品/敌人必须存在。

## 输出模板

```markdown
# RPG 配置表生成方案
## 1. 文件输出
## 2. Sheet 清单
| Sheet | 主键 | 作用 | 关键外键 |
## 3. 字段定义
## 4. 样例数据
## 5. 校验规则
## 6. 导出/读取建议
```

## 文件写入策略

1. 先检查项目中是否已有 `configs/`、`data/`、`excel/`、`story/`。
2. 若已有配置，不要覆盖；生成到新路径或备份后修改。
3. 优先生成 `.xlsx` + `csv/` + `README_Config.md`。
4. 如果项目已有读取器，字段必须对齐读取器。

## 与其他 skills 的协作

- 缺系统公式 → `RPG-System-Designer`
- 需要人物/关系/任务/对白 → `RPG-Story-Designer`
- 表生成后 → `RPG-Balance-Auditor` 检查数值曲线
- 需要落地代码读取 → `RPG-Code-Integrator`

---

## wordworld 项目适配

### 关键文件

| 文件 | 作用 |
|------|------|
| `story/text_game_event_schema_v4.xlsx` | **主配置工作簿**（唯一真实数据源） |
| `story/text_game_event_schema_v4_backup.xlsx` | 备份（变更前自动生成） |
| `src/wordworld/data/workbook.py` | Excel 读取器（`WorkbookReader` 类） |
| `story/*.py` | 批量编辑脚本 |

### 项目现有 Sheet 结构

wordworld 的工作簿包含以下 Sheet（名称含下划线后缀，如 `Skills_v4`）：

| Sheet | 主键 | 说明 |
|-------|------|------|
| `Characters_` | `id` | NPC 角色定义 |
| `Character_Relations_` | `id` | 角色关系（含初始值、类型、可见性） |
| `Enemies_` | `id` | 363 个敌人（mob/elite/boss） |
| `Skills_` | `id` | 斗技/技能（含玩家技能和怪物技能） |
| `Items_` | `id` | 物品（消耗品、材料、丹药等） |
| `Maps_` | `id` | 地图/区域 |
| `Story_Phases_` | `id` | 主线剧情阶段 |
| `Phase_Subnodes_` | `phase_id` + 序号 | 阶段子节点 |
| `Encounters_` | `id` | 探索遭遇事件 |
| `Enemy_Groups_` | `id` | 敌人编组 |
| `Loot_Tables_` | `id` | 掉落表 |

### 项目 DSL 语法

**效果/奖励**（`apply_effects` 支持）：
```text
exp:+100            # 经验增加
silver:+50          # 银两增加
douqi:+20           # 斗气增加
hp:+30              # 生命恢复
item:heal_pill:1    # 获得物品
rel:npc_xun_er:+10  # 关系值变化
rel:npc_xun_er=60   # 关系值设为固定值
flag:some_flag      # 设置剧情标志
```

**条件**（`check_conditions` 支持）：
```text
level>=5
flag:story_flag=true
item:drug:3
rel:npc_yao_lao>=80
```

**关系触发**（`on_reach` 模式）：
```text
rel:npc_yao_lao>=50:exp:+500      # 关系达标时触发一次性效果
rel:npc_xun_er>=80:item:ring:1    # 达到 80 好感时获得戒指
```

### 使用 openpyxl 编辑

```python
import openpyxl
from pathlib import Path

WORKBOOK_PATH = Path("story/text_game_event_schema_v4.xlsx")
wb = openpyxl.load_workbook(WORKBOOK_PATH)

def find_sheet(name_prefix):
    for name in wb.sheetnames:
        if name.startswith(name_prefix):
            return wb[name]
    raise KeyError

ws = find_sheet("Skills_")
headers = [cell.value for cell in next(ws.iter_rows(min_row=1, max_row=1))]
# 追加行：ws.append([id, name, type, rank, effect, description])
```

### 编辑前必做

1. **先备份**：复制 `text_game_event_schema_v4.xlsx` → `text_game_event_schema_v4_backup.xlsx`
2. **读取现有 ID**：收集已有 ID 避免冲突
3. **对齐 headers**：新数据字段必须匹配现有表头
4. **运行测试**：改完后 `python -m unittest tests/test_relationships.py`
