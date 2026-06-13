# 配置工作簿 schema 摘要

## Sheet 清单

| Sheet | 主键 | 作用 | 关键外键 |
|-------|------|------|----------|
| Meta | Field | 配置版本和元信息 | - |
| Characters | Character_ID | 角色/NPC 定义 | Faction_ID, Map_ID |
| Character_Relations | Relation_ID | 角色关系 | Source_ID→Characters, Target_ID→Characters |
| Enemies | Enemy_ID | 敌人定义 | Loot_Table_ID→Loot_Tables |
| Skills | Skill_ID | 技能/斗技定义 | - |
| Items | Item_ID | 物品定义 | - |
| Equipment | Equipment_ID | 装备定义 | - |
| Maps | Map_ID | 地图/区域 | Faction_ID, Encounter_Table_ID |
| Loot_Tables | Loot_Table_ID | 掉落表 | - |
| Loot_Entries | Loot_Entry_ID | 掉落条目 | Loot_Table_ID, Entry_ID |
| Encounters | Encounter_ID | 探索遭遇 | Map_ID, Enemy_Group_ID |
| Enemy_Groups | Enemy_Group_ID | 敌人编组 | - |
| XP_Level | Level | 等级经验曲线 | - |
| Story_Phases | Phase_ID | 主线剧情阶段 | - |
| Phase_Subnodes | Phase_ID + Order | 阶段子节点 | Phase_ID→Story_Phases |
| Flags | Flag_ID | 剧情标志 | - |
| Shops | Shop_ID | 商店 | Map_ID |

## 通用约定

- 所有概率使用 0-100 百分制
- ID 使用小写蛇形命名
- 外键引用目标表主键
- 必填字段不能为空
