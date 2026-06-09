# RPG 标准配置表 schema 参考

## 通用字段规则

- 主键字段必须放第一列。
- 外键字段使用目标主键名。
- 概率默认使用 0-100 百分制。
- 列表字段早期可用 `|` 分隔，长期建议拆子表。

## Meta

| Field | Value | Description |
|---|---|---|
| Config_Version | 0.1.0 | 配置版本 |
| Game_Genre | turn_based_rpg | 游戏类型 |
| Probability_Unit | percent_0_100 | 概率单位 |
| ID_Case | snake_case | ID 命名 |
| Encoding | utf-8 | 编码 |

## Characters

```text
Character_ID, Display_Name, Character_Type, Faction_ID,
Level, HP, ATK, DEF, SPD, Combat_Role, Story_Role,
Personality, Goal, Secret, Description
```

## Character_Relations

```text
Relation_ID, Source_ID, Target_ID, Relation_Type,
Relation_Value, Visible, Pre_Condition, On_Reach,
Gameplay_Effect, Description
```

## Factions

```text
Faction_ID, Display_Name, Type, Leader_ID,
Territory_Map_ID, Core_Belief, Description
```

## Maps

```text
Map_ID, Display_Name, Region, Level_Min, Level_Max,
Faction_ID, Unlock_Condition, Encounter_Table_ID,
NPC_List, Safe_Zone, Description
```

## Enemies

```text
Enemy_ID, Display_Name, Enemy_Type, Level,
HP, ATK, DEF, SPD, Skill_List, AI_Profile_ID,
Loot_Table_ID, XP_Reward, Silver_Reward, Description
```

## Skills

```text
Skill_ID, Display_Name, Skill_Type, Element,
Power_Multiplier, Flat_Power, Cost_Type, Cost_Value,
Cooldown, Target_Rule, Effect_List, Unlock_Condition, Description
```

## Status_Effects

```text
Status_ID, Display_Name, Category, Duration_Type, Duration_Value,
Stack_Mode, Max_Stacks, Stat_Modifier_List, Dispel_Rule, Description
```

## Items

```text
Item_ID, Display_Name, Item_Type, Rarity,
Max_Stack, Buy_Price, Sell_Price, Use_Effect_List, Description
```

## XP_Level

```text
Level, XP_To_Next, HP_Growth, ATK_Growth, DEF_Growth,
SPD_Growth, EXP_Per_Progress, Unlock_List
```

## Loot_Tables

```text
Loot_Table_ID, Display_Name, Roll_Mode, Roll_Count, Description
```

## Loot_Entries

```text
Loot_Entry_ID, Loot_Table_ID, Entry_Type, Entry_ID,
Quantity, Probability, Condition, Description
```

## Quests

```text
Quest_ID, Display_Name, Quest_Type, Chapter,
Giver_ID, Start_Condition, Complete_Condition,
Step_List, Reward_List, Set_Flags, Description
```

## Dialogues

```text
Dialogue_ID, Display_Name, Speaker_ID, Text,
Condition, Next_Node_ID, Set_Flags, Give_Items, Notes
```

## Encounters

```text
Encounter_ID, Map_ID, Encounter_Type, Enemy_Group_ID,
Weight, Condition, Min_Level, Max_Level, Description
```

## Enemy_Groups

```text
Enemy_Group_ID, Display_Name, Enemy_List,
Formation, Recommend_Level, Reward_Modifier
```

## Flags

```text
Flag_ID, Scope, Type, Default_Value,
Set_By, Read_By, Meaning, Notes
```
