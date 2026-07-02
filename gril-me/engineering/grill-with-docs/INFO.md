# grill-with-docs — 带文档上下文的方案拷问

| 项目 | 内容 |
|------|------|
| **来源** | `skills/engineering/grill-with-docs/` |
| **格式** | PromptScript |
| **触发词** | "grill with docs", 压力测试计划 |
| **文件** | SKILL.md, ADR-FORMAT.md, CONTEXT-FORMAT.md |

## 功能

- **领域意识** — 读取 `CONTEXT.md`（领域术语表）和 `docs/adr/`（架构决策记录）
- **术语挑战** — 当用户使用的术语与已有 glossary 冲突时立即指出
- **模糊语言锐化** — 将模糊/过载术语提议为精确规范术语
- **代码交叉验证** — 用户说系统如何工作时，检查代码是否真的同意
- **实时文档更新** — 术语解析后即时更新 `CONTEXT.md`
- **ADR 审慎决策** — 只在三个条件（难逆、无上下文则意外、真实权衡）都满足时才创建 ADR
