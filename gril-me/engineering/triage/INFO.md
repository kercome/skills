# triage — Issue 分诊

| 项目 | 内容 |
|------|------|
| **来源** | `skills/engineering/triage/` |
| **格式** | PromptScript |
| **触发词** | 创建/分诊 Issue、审查 bug/功能请求、为 AFK Agent 准备 Issue |
| **文件** | SKILL.md, AGENT-BRIEF.md, OUT-OF-SCOPE.md |

## 角色状态机

**分类角色**: `bug` / `enhancement`

**状态角色**: `needs-triage` → `needs-info` ←→ `ready-for-agent` / `ready-for-human` / `wontfix`

## 分诊流程

1. **收集上下文** — 读取 Issue 全文、过往分诊笔记、代码库、`.out-of-scope/`
2. **推荐** — 告知维护者分类 + 状态建议及理由
3. **复现（仅 bug）** — 尝试复现，报告结果
4. **拷问（如需）** — 运行 `/grill-with-docs` 完善 Issue
5. **执行结果** — 根据状态执行对应操作（写 Agent Brief / 打标签 / 关闭等）
