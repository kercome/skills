# tdd — 测试驱动开发

| 项目 | 内容 |
|------|------|
| **来源** | `skills/engineering/tdd/` |
| **格式** | PromptScript |
| **触发词** | "TDD", "red-green-refactor", 测试优先开发 |
| **文件** | SKILL.md, deep-modules.md, interface-design.md, mocking.md, refactoring.md, tests.md |

## 核心理念

- **好的测试** = 集成测试风格，通过公共接口验证行为，不关心实现细节
- **坏的测试** = 耦合实现，mock 内部协作者，修改内部函数就崩溃
- **禁止水平切片** — 不要写全部测试再写全部实现

## 工作流

```
RED:   写一个测试 → 失败
GREEN: 最简实现代码 → 通过
REFACTOR: 提取重复、深化模块、应用 SOLID
         ↑ 每次重构后重新运行测试
```

一个测试 → 一个实现 → 重复。每个测试响应上一个周期学到的东西。
