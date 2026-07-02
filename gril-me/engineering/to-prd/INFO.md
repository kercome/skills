# to-prd — 对话上下文转 PRD

| 项目 | 内容 |
|------|------|
| **来源** | `skills/engineering/to-prd/` |
| **格式** | PromptScript |
| **触发词** | "create a PRD", 从当前对话生成产品需求文档 |
| **文件** | SKILL.md（单文件） |

## 流程

1. **探索代码库** — 了解当前状态，使用领域术语 + 尊重 ADR
2. **确定测试 seam** — 在最高可行的 seam 处规划测试点，与用户确认
3. **编写 PRD** — 使用标准模板发布到 issue tracker，标记 `ready-for-agent`

## PRD 模板结构

- **Problem Statement** — 从用户视角描述问题
- **Solution** — 从用户视角描述方案
- **User Stories** — 大量编号的用户故事
- **Implementation Decisions** — 模块/接口/架构/数据模式/API 合约，不含文件路径和代码片段
- **Testing Decisions** — 测试策略、模块范围、前例
- **Out of Scope** — 明确排除的范围
- **Further Notes** — 补充说明
