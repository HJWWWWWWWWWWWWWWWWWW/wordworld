---
name: claude-mem-config
description: claude-mem 配置会话上下文
metadata: 
  node_type: memory
  type: project
  originSessionId: dc8474e2-a29d-4723-85a7-18aa4e82dbfc
---

用户要求配置 claude-mem 的自动记录功能。
- claude-mem v13.4.2 已安装，MCP 插件已启用
- 当前缺少自动记录 hooks
- 用户要求：1) 手动记录重要内容 2) 配置 hooks 实现自动记录
- 注意：`observation_add` 需要 CLAUDE_MEM_RUNTIME=server-beta，当前为 worker 模式

**Why:** claude-mem 需要 hooks 才能自动记录对话
**How to apply:** 在 settings.json 中配置 Stop/PostToolUse hooks
