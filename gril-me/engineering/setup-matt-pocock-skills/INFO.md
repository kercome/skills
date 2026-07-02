# setup-matt-pocock-skills — 技能初始化配置

| 项目 | 内容 |
|------|------|
| **来源** | `skills/engineering/setup-matt-pocock-skills/` |
| **格式** | PromptScript（无模型调用，纯 prompt 驱动） |
| **触发词** | 首次使用工程技能前运行，或技能缺失 issue tracker/标签/文档上下文时 |
| **文件** | SKILL.md, domain.md, issue-tracker-github.md, issue-tracker-gitlab.md, issue-tracker-local.md, triage-labels.md |

## 配置的三项决策

A. **Issue Tracker** — 选择问题追踪位置（GitHub / GitLab / Local markdown / Other）
B. **Triage 标签词汇** — 映射 5 个规范分诊角色到仓库实际标签字符串
C. **领域文档布局** — 单上下文 vs 多上下文（全局 CONTEXT.md 或 CONTEXT-MAP.md）

产出：在 `CLAUDE.md` / `AGENTS.md` 中添加 `## Agent skills` 块，并写入 `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md`, `docs/agents/domain.md`。
