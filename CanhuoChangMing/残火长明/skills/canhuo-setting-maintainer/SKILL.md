---
name: canhuo-setting-maintainer
description: Maintain and extend the Chinese fantasy novel repository 《残火长明》 while preserving canonical setting, nine-part chapter continuity, faction/family character records, open-ended finale constraints, and generated category summaries. Use whenever editing plot cards, characters, factions, families, timeline, world rules, ending, or 分类汇总 files in this repository.
---

# 残火长明设定维护

## 权威顺序

开始修改前，按以下优先级读取并处理冲突：

1. `全局设定定稿基准.txt`
2. `长篇规划/02_正式章节卡/*正式章节卡.txt`
3. 较新的独立人物志、势力文档、家族根部文档
4. `长篇规划/01_规则与总纲/九部结构与扩容总纲.txt`
5. `长篇规划/04_旧版核心事件/*.txt` 与 `残火长明-剧情大纲.txt`
6. `分类汇总/*.txt`，仅为机械汇总，不作为独立设定来源

读取 [references/canon-constraints.md](references/canon-constraints.md) 获取不可破坏的全局硬约束。

## 标准工作流

1. 先扫描相关正式章节卡、人物志、势力文档和全局基准。
2. 列出受影响的人物、时间、地点、九灯、遗物与后续章节。
3. 修改原始来源文档，不直接把分类汇总当作来源编辑。
4. 检查同名人物、死亡/失踪状态、信息知情范围与跨州旅行时间。
5. 涉及人物时，按 [references/character-faction-rules.md](references/character-faction-rules.md) 建档。
6. 涉及章卡或终局时，按 [references/plot-ending-rules.md](references/plot-ending-rules.md) 修改。
7. 运行 `scripts/check_continuity.ps1`。
8. 运行 `scripts/rebuild_summaries.ps1`。
9. 再运行一次连续性检查，确认汇总无缺失来源。
10. 涉及正文初稿时，运行 `scripts/check_drafts.ps1`，检查已完成章节连续、净汉字数与现代措辞。

## 编辑原则

- 保留已有具体选择、代价和后果；扩写不能只是延长战斗。
- 普通人、执行者和反对者都应有具体利益与恐惧。
- 新增牺牲必须交代知情程度、拒绝权、受益者和记录方式。
- 新增遗物不得成为无代价万能解法。
- 新增州名先判断是行政州、旧称、地理区还是军区；不得扩出第十三州。
- 角色只能知道亲历、被告知或从档案读取的信息。
- 不确定时保留异议与无法确认，不为整齐结论虚构答案。

## 修改范围判断

### 只改人物志

同时检查人物所属势力、家族、正式章卡中的关键选择与最终状态。

### 改正式章节卡

保持第1章至第1250章编号连续、无重复；若用户明确扩写导致顺延，则同步所有后续正式章卡范围和全局基准。

### 改终局

不得将开放式结尾封死。林烬最终点火后失踪，不确认死亡或归来；最后炉火来源不明。

### 改分类

先更新 `分类汇总/00_分类索引.txt`，再运行汇总脚本。跨属人物允许在多个分类重复收录。

## 验证命令

在仓库根目录运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\skills\canhuo-setting-maintainer\scripts\check_continuity.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\skills\canhuo-setting-maintainer\scripts\rebuild_summaries.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\skills\canhuo-setting-maintainer\scripts\check_drafts.ps1
```

检查失败时，先修正原始文档，再重建汇总。
