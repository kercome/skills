# 🔀 Engineering Skills 决策树

> Agent 如何在没有轮询的情况下，精准命中正确的 Skill
> 原理：YAML frontmatter 的 `description` 字段在系统 prompt 中就可见，Agent 做意图→匹配

---

## ⚙️ 底层路由机制

```
系统启动
  │
  ├─ 扫描所有 skills 目录
  ├─ 读取每个 SKILL.md 的 YAML frontmatter
  │   └─ 只加载 name + description（~100 字/skill，总成本极低）
  ├─ 注入到系统 prompt 的 <available_skills> 块中
  │
  ▼
用户输入 → Agent 收到完整 prompt（含 skill 描述列表）
  │
  ├─ 匹配规则：description 触发
  │   ├─ "User mentions 'grill me'" → grill-with-docs
  │   ├─ "User says 'diagnose this'" → diagnose
  │   ├─ "User wants to stress-test plan" → grill-with-docs
  │   └─ ...
  │
  └─ 命中后：read SKILL.md body → 按指令执行
```

**关键点**：每个 skill 的 description 就是路由标签。不需要轮询，不需要 AI 遍历文件，因为所有 skill 的 `name + description` 已经在上下文里了。

---

## 🌳 决策树

```
用户输入
│
├─ 提到 bug / 坏了 / 崩了 / 性能问题 / "debug this" / "diagnose this"
│   └─ ⚡ diagnose
│       └─ 6 阶段：复现→最小化→假设→仪表→修复→回归测试
│
├─ 提到 "grill me" / 压力测试某个方案 / 拷问计划 / "这个设计有问题吗"
│   ├─ 项目有 CONTEXT.md / docs/adr/ ？
│   │   ├─ YES → ⚡ grill-with-docs  （带领域模型交叉验证）
│   │   └─ NO  → ⚡ grill-me          （纯方案拷问，不涉及文档）
│   │
├─ 提到重构 / 架构改进 / 代码库难以测试 / 模块耦合 / "improve architecture"
│   └─ ⚡ improve-codebase-architecture
│       └─ 探索→HTML报告（Tailwind+Mermaid）→逐层追问→更新ADR
│
├─ 提到 "prototype this" / 试几个方案 / "let me play with it" / "sanity check 数据模型"
│   ├─ 问题涉及逻辑/状态机？
│   │   └─ ⚡ prototype → LOGIC 分支 → 终端交互应用
│   ├─ 问题涉及 UI/视觉？
│   │   └─ ⚡ prototype → UI 分支 → 多变体切换页面
│
├─ 提到 TDD / "red-green-refactor" / "先写测试" / 测试驱动
│   └─ ⚡ tdd
│       └─ 红→绿→重构 循环，垂直切片（每轮 1 测试 + 1 实现）
│
├─ 提到 "create issues" / 把计划拆成任务 / "分解工作" / "生成 Issue"
│   └─ ⚡ to-issues
│       └─ 收集→探索→起草垂直切片→问用户意见→发布到 tracker
│
├─ 提到 "create a PRD" / "生成PRD" / 把对话整理成产品需求
│   └─ ⚡ to-prd
│       └─ 探索→确定 seam→按模板写 PRD→发布 ready-for-agent
│
├─ 提到 "triage" / 分诊 Issue / "这个 Issue 怎么处理" / 审查 bug 列表
│   └─ ⚡ triage
│       └─ 收集→推荐→复现(bug)→拷问→打标/写Agent Brief
│
├─ 提到 "zoom out" / "不太熟悉这段代码" / "给我全局背景"
│   └─ ⚡ zoom-out
│       └─ 上升一层抽象，输出模块地图 + 调用关系
│
├─ 首次使用 / 技能缺失上下文 / "setup skills"
│   └─ ⚡ setup-matt-pocock-skills
│       └─ 配置 IssueTracker + Label + 文档布局 → 写入 AGENTS.md
│
└─ 以上都不匹配？
    └─ 该对话不需要工程 skill，Agent 正常处理
```

---

## 🔗 技能的串联调用链

这些技能不是孤立的——Agent 可以串联调用：

```
用户说："我有个新功能想法，帮我整理一下"
  │
  ├─ to-prd          ← 把对话综合成 PRD
  │   └─ 输出 Issue（ready-for-agent 标签）
  │
  ├─ grill-with-docs ← 拿着 PRD 做方案压力测试
  │   └─ 更新 CONTEXT.md，可能产出 ADR
  │
  ├─ to-issues       ← 把 PRD 拆成可实现 Issue
  │   └─ 发布到 issue tracker
  │
  ├─ prototype       ← 如果某个决策需要验证
  │   └─ 终端应用 或 UI 多方案对比
  │
  ├─ tdd             ← 选定方案后测试驱动开发
  │   └─ 红→绿→重构 循环
  │
  └─ diagnose        ← 如果过程中出 bug
      └─ 反馈回路→假设→修复
```

---

## 📊 意图→技能 快速对照表

| 用户说什么 | 命中 skill | 关键词 |
|-----------|-----------|--------|
| "这 bug 修了一天了" | diagnose | bug, broken, perf, debug |
| "你觉得这个架构有问题吗" | grill-with-docs / grill-me | grill, stress-test |
| "这个代码库太乱了" | improve-codebase-architecture | architecture, refactor, coupling |
| "先做个雏形看看" | prototype | prototype, sanity-check, play |
| "我先写测试再写代码" | tdd | tdd, red-green-refactor |
| "帮我把这个拆成 Issue" | to-issues | issues, breakdown |
| "把这个需求写成 PRD" | to-prd | prd, spec |
| "这 Issue 该给谁处理" | triage | triage, label |
| "这段代码是干嘛的" | zoom-out | zoom out, unfamiliar |

---

## 🧠 为什么不轮询也能精准命中

```
❌ 轮询方式（低效）：
   read 每个 SKILL.md → 判断 → 下一个 → 直到找到
   代价：N 次 I/O + N 次 token 消耗 + 慢

✅ 元数据预加载方式（高效）：
   description 已在系统 prompt 中 → Agent 看一眼就知道用哪个
   代价：每个 skill ~50 words × 10 skills = 500 words（基本免费）
```

这就是为什么每个 skill 的 description 写得好不好，直接决定了路由的准确度。description 里必须包含：**做什么 + 什么时候用 + 触发词**。
