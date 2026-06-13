# Changelog

## v0.1-demo (2026-06-13)

### 重大变更
- **去 IP 化**：将全部斗破苍穹专有名词替换为原创世界观（源火纪 / 灵玄大陆）
  - 能量：斗气 → 灵力，火焰：异火 → 源火，技能：斗技 → 灵技
  - 主角：萧炎 → 林烬，导师：药老 → 玄炉老人
  - 势力：云岚宗 → 青岚宗，魂殿 → 黑渊殿，古族 → 云族 等
  - 数据表：Excel 配置 118,054 处文本已替换

### 修正与清理
- 补全 `run.py`、`run_gui.py` 入口文件
- 重写 README：版本状态、运行环境、操作说明、完成度清单
- 更新 .gitignore：排除 build/dist/spec/stackdump
- 清理仓库：移除构建产物和临时文件
- 术语一致性：七属性克制、四币制经济

### 新增
- `scripts/smoke_test.py` — 烟雾测试（16 项检查，含 12 个玩家字段验证）
- `scripts/migrate_to_original_world.py` — 去 IP 迁移工具
- `docs/BUILD.md` — Windows .exe 打包指南
- Demo 结束提示（主线阶段 >= 5 时自动显示）
- CHANGELOG.md 和 TODO.md

### 测试
- 149 个单元测试全部通过
- 烟雾测试 16 项全部通过
- `python -m compileall src` 编译通过
