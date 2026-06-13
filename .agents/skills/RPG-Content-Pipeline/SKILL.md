---
name: RPG-Content-Pipeline
description: "RPG 内容的批量生产、迁移和审计流水线。用于批量生成/修改 Excel 配置数据、迁移旧配置到新 schema、校验数据一致性、审计变更影响，以及管理 story/ 脚本的生命周期。"
---

# RPG-Content-Pipeline

你是 wordworld 项目的内容生产流水线负责人。目标是确保内容批量生产 **可审计、可回滚、可复现、与代码一致**。

## 适用场景

- 批量添加敌人、技能、物品、地图子区域。
- 迁移配置表字段（如旧格式转新格式）。
- 扫描现有内容并生成补充（如扫描章节生成敌人）。
- 修复配置表数据错误。
- 验证配置表与代码引用的一致性。
- 管理 story/ 脚本的创建、执行、归档。

## 工作准则

1. **先备份再操作**：任何修改 Excel 的脚本必须在执行前备份。
2. **脚本即文档**：每个 story/ 脚本必须包含文件头注释说明目的。
3. **幂等性**：脚本应能安全地重复执行（检查已有 ID 避免重复）。
4. **可审计**：修改后输出变更统计和可 diff 的结果。
5. **测试联动**：改完内容后必须运行测试验证。

---

## wordworld 内容生产流程

### 流水线总览

```
策划需求
  → RPG-System-Designer（系统设计）
  → RPG-Combat-Designer（战斗设计）
  → RPG-Story-Designer（剧情设计）
  → story/*.py（批量脚本，修改 Excel）
  → python -m unittest（验证）
  → RPG-Balance-Auditor（审计）
  → git commit（版本管理）
```

### story/ 脚本管理模式

#### 脚本命名规范

| 模式 | 说明 | 示例 |
|------|------|------|
| `add_*.py` | 添加新内容 | `add_city_subareas.py` |
| `expand_*.py` | 扩展现有内容 | `expand_enemies.py` |
| `fix_*.py` | 修复数据错误 | `fix_relationships.py` |
| `design_*.py` | 设计/生成内容 | `design_enemy_skills.py` |
| `redesign_*.py` | 重新设计 | `redesign_skills_from_novel.py` |
| `update_*.py` | 按规则更新 | `update_level_progression.py` |
| `scan_*.py` | 扫描/审计 | `chapter_scan.py` |
| `supplement_*.py` | 补充缺失 | `supplement_enemies.py` |

#### 脚本结构模板

```python
"""
脚本用途：一句话说明。
操作方法：如何执行、影响哪些 sheet、是否幂等。
备份位置：story/text_game_event_schema_v4_backup.xlsx
"""
from pathlib import Path
import openpyxl
import shutil

WORKBOOK_PATH = Path("story/text_game_event_schema_v4.xlsx")
BACKUP_PATH = Path("story/text_game_event_schema_v4_backup.xlsx")

# 1. 备份
shutil.copy(WORKBOOK_PATH, BACKUP_PATH)

# 2. 加载
wb = openpyxl.load_workbook(WORKBOOK_PATH)

def find_sheet(name_prefix):
    for name in wb.sheetnames:
        if name.startswith(name_prefix):
            return wb[name]
    raise KeyError

# 3. 收集已有数据
ws = find_sheet("TargetSheet_")
headers = [c.value for c in next(ws.iter_rows(min_row=1, max_row=1))]
existing_ids = set()
for row in ws.iter_rows(min_row=2):
    if row[0].value:
        existing_ids.add(str(row[0].value))

# 4. 执行变更
changed = 0
for data in NEW_DATA:
    if data["id"] not in existing_ids:
        ws.append([str(data.get(h, "")) for h in headers])
        changed += 1

# 5. 保存
wb.save(WORKBOOK_PATH)

# 6. 输出统计
print(f"Added: {changed}, Skipped: {len(NEW_DATA) - changed}")
print(f"Backup saved to: {BACKUP_PATH}")
```

### 配置表版本管理

#### 备份策略

```
story/
├── text_game_event_schema_v4.xlsx          ← 当前工作簿
├── text_game_event_schema_v4_backup.xlsx   ← 最近一次修改前的备份
└── archives/                                ← 可选：历史版本归档
```

#### 变更审计清单

每次修改 Excel 后检查：
- [ ] 备份已生成
- [ ] 新 ID 不与已有 ID 冲突
- [ ] 外键引用有效（如技能引用的状态 ID 存在）
- [ ] 概率值在 0-100 范围内
- [ ] 数值无越界（HP/ATK/DEF > 0）
- [ ] 故事引用有效（地图/敌人/NPC 在相关 sheet 中存在）
- [ ] `python -m unittest tests/test_relationships.py` 通过

---

## 常见内容生产任务

### 任务 A：批量添加敌人

1. 用 `RPG-Combat-Designer` 设计敌人模板
2. 编写 `add_*` 或 `expand_*` 脚本
3. 指定地图/等级段/数量
4. 运行并验证

### 任务 B：扩展地图子区域

1. 确认目标区域的 `map_` ID
2. 设计子区域（安全区/战斗区/商店/任务点）
3. 更新 Encounters sheet 添加新遭遇
4. 更新 Maps sheet（如需要）

### 任务 C：章节推进内容

1. 用 `chapter_scan.py` 扫描现有章节
2. 识别敌人数量缺口（每章应有足够敌人）
3. 用 `supplement_enemies.py` 模式补充
4. 更新 Encounters 和 Enemy_Groups

### 任务 D：关系数据修复

1. 扫描 Character_Relations sheet
2. 检查关系值、类型、可见性
3. 对照 `IMMUNE_RELATIONSHIPS` 检查一致性
4. 编写 `fix_relationships.py` 脚本

### 任务 E：技能体系重构

1. 审计现有技能 pool（Skills sheet）
2. 检查技能覆盖度（所有等级段/类型是否都有）
3. 用 `redesign_*` 模式重新设计
4. 更新 Enemies sheet 中的技能引用

---

## 数据一致性校验

### 代码引用检查

```python
# 检查 engine.py 中引用的所有 ID 是否在 Excel 中存在
# 常见检查项：
# - LEVEL_SKILL_MILESTONES 中的 skill ID
# - FINISHER_SKILLS 中的 skill ID
# - IMMUNE_RELATIONSHIPS 中的 rel ID
# - REGION_MAP_GROUPS 中的 map ID
# - LEGACY_STORY_PHASE_IDS_V2 中的 phase ID
```

### 测试覆盖检查

每次内容变更后必须：
1. `python -m unittest tests/test_relationships.py` 全绿
2. 如新增功能路径，添加对应测试
3. 如有边界条件，添加边界测试

---

## 与其他 skills 的协作

- 系统设计 → `RPG-System-Designer`
- 战斗设计 → `RPG-Combat-Designer`
- 剧情设计 → `RPG-Story-Designer`
- Excel 操作 → `RPG-Excel-Generator`
- 数值审计 → `RPG-Balance-Auditor`
- 代码落地 → `RPG-Code-Integrator`
