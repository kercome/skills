# improve-codebase-architecture — 代码架构深化

| 项目 | 内容 |
|------|------|
| **来源** | `skills/engineering/improve-codebase-architecture/` |
| **格式** | PromptScript |
| **触发词** | 改善架构、找重构机会、让代码库更可测/AI 可导航 |
| **文件** | SKILL.md, DEEPENING.md, HTML-REPORT.md, INTERFACE-DESIGN.md, LANGUAGE.md |

## 核心术语

- **Module** — 有接口和实现的任何东西
- **Interface** — 调用者需要知道的一切（类型、不变性、错误模式等）
- **Depth** — 接口的杠杆效应：小接口背后的大行为 = Deep
- **Seam** — 接口所在的位置；可改变行为而不原地编辑的地方
- **Adapter** — 在 seam 处满足接口的具体实现

## 流程

1. **探索** — 读取领域术语表 + ADR，使用 `Explore` 子代理走查代码
2. **HTML 报告** — 将候选重构项生成为自包含的 HTML 报告（Tailwind + Mermaid 可视化）
3. **拷问循环** — 用户选择候选后逐层追问，实时更新 `CONTEXT.md` 和 ADR
