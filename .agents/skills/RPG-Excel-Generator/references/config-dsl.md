# RPG 条件/奖励/效果 DSL 参考

## wordworld 项目 DSL（实际代码实现）

### 效果语法（engine.py apply_effects）

效果用 **逗号 `,`** 分隔：

```text
exp:+100                    # 经验增加
silver:+50                  # 银两增加
hp:+30                      # 生命恢复
douqi:+20                   # 斗气恢复
atk:+5,def:+3,spd:+2        # 属性变化
stamina:+10                 # 体力变化
progress:+5                 # 修炼进度
item:heal_pill:1            # 获得物品
rel:npc_xun_er:+10          # 关系变化
rel:npc_xun_er=60           # 关系设值
flag:flag_id                # 设置剧情标志
soul:+2                     # 灵魂力量
adventure_points:+1         # 冒险阅历
```

组合效果示例：
```text
exp:+100,silver:+50,item:heal_pill:2
```

### 条件语法（engine.py check_conditions）

条件用 **逗号 `,`** 分隔，**全部为 AND 关系**：

```text
level>=5                    # 等级条件
flag:flag_id=true           # 标志条件
item:drug>=3                # 物品条件
rel:npc_target>=60          # 关系条件
progress>=100               # 进度条件
```

组合条件示例：
```text
level>=10,flag:phoenix_trial_passed=true,rel:npc_yao_lao>=80
```

注意：目前代码不支持 `||` (OR) 或 `&&` (AND) 语法，所有逗号分隔的条件为全 AND。

### 关系效果语法

```text
rel:target_ID:+value        # 关系值增加（target_ID 即关系表中的 target 字段）
rel:target_ID=-value        # 关系值减少
rel:target_ID=value         # 关系值设为指定值
```

免疫关系（`IMMUNE_RELATIONSHIPS`）中的关系不受 `rel:` 效果影响。

### 关系触发语法（on_reach）

```text
rel:target_ID>=threshold:effect1,effect2
```

示例：
```text
rel:npc_yao_lao>=50:exp:+500,flag:mentor_trust
rel:npc_xun_er>=80:item:strange_ring:1
```

### 掉落简写

掉落使用 **竖线 `|`** 分隔多个掉落条目：
```text
silver:50:80|item:heal_pill:1:30|equip:flame_sword:1:5
```
格式：`类型:ID或数量:概率`，概率为 0-100 百分制。

### 技能列表

技能列表使用 **逗号 `,`** 分隔：
```text
skill_bajibang,skill_flame_mantra,skill_alchemy
```

### 敌人编组

敌人编组使用 **竖线 `|`** 分隔：
```text
mob_wolf:2|mob_alpha_wolf:1
```
