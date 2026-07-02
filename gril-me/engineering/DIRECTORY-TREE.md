# 📁 Engineering Skills 完整目录树

> 来源: `https://github.com/mattpocock/skills/tree/main/skills/engineering`
> 共计 10 个技能 · 44 个文件 · 约 130 KB

```
engineering/
│
├── 📄 README.md                                          (2.1 KB)
│   └─ 目录总览：10 技能速览表 + 触发词 + 文件清单
│
├── 📄 DECISION-TREE.md                                   (5.7 KB)
│   └─ 路由决策树：Agent 如何根据用户意图命中正确的 skill（元数据预加载原理 + 串联调用链）
│
├── 📁 diagnose/                    🐛 硬 Bug 诊断循环
│   │
│   ├── 📄 SKILL.md                                       (7.2 KB)
│   │   └─ 主技能文件：6 阶段诊断流程
│   │      ① 建立反馈回路（10 种构造方法 → 让循环更快、信号更锐）
│   │      ② 复现 → ③ 假设（3-5 个可证伪假说）→ ④ 仪表（一次改一个变量）
│   │      ⑤ 修复 + 回归测试 → ⑥ 清理 + 事后复盘
│   │
│   ├── 📄 INFO.md                                        (1.0 KB)
│   │   └─ 技能概要：元数据、来源、触发词、6 阶段速览 + 反馈回路优先层级
│   │
│   └── 📁 scripts/
│       └── 📄 hitl-loop.template.sh                      (1.2 KB)
│           └─ HITL（人工在环）bash 模板：当无法自动化反馈回路时，
│              用 step/capture 驱动人工操作 → 捕获结果回传给 Agent
│
├── 📁 grill-with-docs/              🔬 基于领域模型的方案拷问
│   │
│   ├── 📄 SKILL.md                                       (3.6 KB)
│   │   └─ 主技能文件：逐层追问 → 术语挑战 → 代码交叉验证 → 实时更新文档
│   │      每条决策边走边录：术语入 CONTEXT.md，架构决策入 ADR
│   │
│   ├── 📄 ADR-FORMAT.md                                  (2.8 KB)
│   │   └─ ADR 格式规范：何时创建（难逆 + 无上下文则意外 + 真实权衡）、
│   │      编号规则、可选字段（Status/Considered Options/Consequences）、
│   │      哪些决策值得记录 vs 哪些不值得
│   │
│   ├── 📄 CONTEXT-FORMAT.md                              (2.3 KB)
│   │   └─ 领域术语表格式规范：单行定义 + _Avoid_ 字段、
│   │      单上下文 vs 多上下文（CONTEXT-MAP.md）布局、分组规则
│   │
│   └── 📄 INFO.md                                        (0.9 KB)
│       └─ 技能概要：元数据、功能清单、ADR 创建三条件
│
├── 📁 improve-codebase-architecture/  🏗️ 架构深化与重构
│   │
│   ├── 📄 SKILL.md                                       (6.5 KB)
│   │   └─ 主技能文件：三阶段流程
│   │      ① 探索（有机走查 + 删除测试 + 摩擦感知）
│   │      ② HTML 报告（Tailwind + Mermaid 可视化、before/after 图）
│   │      ③ 拷问循环（逐层追问 → 实时写 CONTEXT.md + ADR）
│   │
│   ├── 📄 LANGUAGE.md                                    (3.8 KB)
│   │   └─ 词汇规范：Module / Interface / Implementation / Depth /
│   │      Seam / Adapter / Leverage / Locality 的精确定义 +
│   │      术语关系图 + 被拒绝的替代表述 + 核心原则：
│   │      删除测试、接口即测试面、一个 adapter=假设 seam，两个=真实 seam
│   │
│   ├── 📄 DEEPENING.md                                   (2.6 KB)
│   │   └─ 深化方法论：4 种依赖分类 → 对应测试策略
│   │      ① In-process（直接合并）② Local-substitutable（本地替身）
│   │      ③ Ports & Adapters（网络边界）④ Mock（外部服务）
│   │      + Seam 纪律：一个 adapter vs 两个 adapter 的差别
│   │
│   ├── 📄 INTERFACE-DESIGN.md                            (2.7 KB)
│   │   └─ 接口设计方法：Design It Twice 原则
│   │      并行派生 3+ 子代理 → 给定不同设计约束（最简/最灵活/最常见调用者）
│   │      → 对比 Depth、Locality、Seam 位置 → 给出有观点的推荐
│   │
│   ├── 📄 HTML-REPORT.md                                 (6.7 KB)
│   │   └─ HTML 报告规范：Tailwind CDN + Mermaid CDN 脚手架、
│   │      5 种图表模式（Mermaid 流程图 / 手绘盒线图 / 横截面图 / 体量图 /
│   │      调用树折叠）、卡片模板、样式规范、术语使用指令
│   │
│   └── 📄 INFO.md                                        (1.0 KB)
│       └─ 技能概要：核心术语、三阶段流程、输出物
│
├── 📁 prototype/                    🎨 快速原型验证
│   │
│   ├── 📄 SKILL.md                                       (3.3 KB)
│   │   └─ 主技能文件：路由到 Logic 或 UI 分支
│   │      通用规则：可丢弃标记、一键运行、无持久化、跳过润色、
│   │      展示状态、完成后删除或吸收
│   │
│   ├── 📄 LOGIC.md                                       (5.6 KB)
│   │   └─ 逻辑原型分支：构建最小交互终端（TUI）
│   │      ① 声明问题 ② 选语言 ③ 纯逻辑模块（reducer/状态机/纯函数）
│   │      ④ 每帧重绘的轻量 TUI（ANSI 粗/暗色）→ 按键驱动 → 循环
│   │      ⑤ 一键运行 ⑥ 交付 → ⑦ 捕捉答案 → 删除原型壳
│   │
│   ├── 📄 UI.md                                          (6.8 KB)
│   │   └─ UI 原型分支：生成 3-5 个完全不同的 UI 变体
│   │      子形状 A（嵌入现有页面，?variant= 切换）优先于 B（独立路由）
│   │      浮动底栏切换器（← → 箭头 + 半透明 + 生产禁用）→ 折叠 winner
│   │
│   └── 📄 INFO.md                                        (0.9 KB)
│       └─ 技能概要：两条分支、核心规则
│
├── 📁 setup-matt-pocock-skills/      🔧 工程技能初始化配置
│   │
│   ├── 📄 SKILL.md                                       (6.9 KB)
│   │   └─ 主技能文件：三步决策流程
│   │      ① 探索当前仓库（git remote / AGENTS.md / CONTEXT.md / .scratch/）
│   │      ② 逐段展示 + 确认（A.Issue Tracker → B.Triage 标签 → C.文档布局）
│   │      ③ 编辑写入（CLAUDE.md/AGENTS.md 的 ## Agent skills 块 + docs/agents/）
│   │
│   ├── 📄 issue-tracker-github.md                        (1.1 KB)
│   │   └─ GitHub 问题追踪器约定：gh CLI 指令速查（create/view/list/comment/edit/close）
│   │
│   ├── 📄 issue-tracker-gitlab.md                        (1.5 KB)
│   │   └─ GitLab 问题追踪器约定：glab CLI 指令速查 + MR 操作说明
│   │
│   ├── 📄 issue-tracker-local.md                         (0.8 KB)
│   │   └─ 本地 Markdown 问题追踪器约定：.scratch/<feature>/ 目录结构
│   │      PRD.md → issues/NN-slug.md → ## Comments 会话记录
│   │
│   ├── 📄 triage-labels.md                               (1.0 KB)
│   │   └─ Triage 标签映射表：5 个规范角色 → 仓库实际标签字符串的映射模板
│   │
│   ├── 📄 domain.md                                      (2.0 KB)
│   │   └─ 领域文档消费规则：何时读 CONTEXT.md / CONTEXT-MAP.md / ADR、
│   │      单/多上下文文件布局、用术语表词汇命名、标记 ADR 冲突
│   │
│   └── 📄 INFO.md                                        (1.0 KB)
│       └─ 技能概要：三项配置决策、产出物
│
├── 📁 tdd/                           🟢 测试驱动开发
│   │
│   ├── 📄 SKILL.md                                       (4.4 KB)
│   │   └─ 主技能文件：红→绿→重构 工作流
│   │      ① 规划（确认接口 + 行为优先级 + 深模块机会）
│   │      ② Tracer Bullet（1 测试 + 1 实现）
│   │      ③ 增量循环（垂直切片，禁止水平切片）
│   │      ④ 重构（RED 状态绝不重构）
│   │
│   ├── 📄 tests.md                                       (1.6 KB)
│   │   └─ 好测试 vs 坏测试：通过公共接口验证行为 vs 耦合实现细节、
│   │      代码示例对比（mock 内部协作者 → ❌ / 验证可观察行为 → ✅）
│   │
│   ├── 📄 mocking.md                                     (1.5 KB)
│   │   └─ Mock 指南：只在系统边界 mock（外部 API/数据库/时间）、
│   │      不 mock 自有模块、依赖注入 + SDK 风格接口设计
│   │
│   ├── 📄 deep-modules.md                                (1.2 KB)
│   │   └─ 深模块概念（Ousterhout）：小接口 + 深实现 = Deep，
│   │      大接口 + 薄实现 = Shallow，3 个自检问题
│   │
│   ├── 📄 interface-design.md                            (0.7 KB)
│   │   └─ 可测试接口三原则：接受依赖不创建、返回结果不产生副作用、小表面积
│   │
│   ├── 📄 refactoring.md                                 (0.4 KB)
│   │   └─ 重构候选清单：重复→提取、长方法→私有帮助函数、
│   │      浅模块→深化、特征嫉妒→数据所在即逻辑所在、原始类型迷恋→值对象
│   │
│   └── 📄 INFO.md                                        (0.9 KB)
│       └─ 技能概要：核心理念、禁止水平切片、RED→GREEN→REFACTOR 循环
│
├── 📁 to-issues/                     📋 计划 → 实现 Issue
│   │
│   ├── 📄 SKILL.md                                       (3.6 KB)
│   │   └─ 主技能文件：5 步操作流程
│   │      ① 收集上下文 ② 探索代码库 ③ 起草垂直切片（HITL/AFK 标注）
│   │      ④ 询问用户（粒度/依赖/HITL标记）⑤ 发布 Issue（依赖顺序 + 模板）
│   │
│   └── 📄 INFO.md                                        (0.9 KB)
│       └─ 技能概要：流程、切片规则、HITL vs AFK
│
├── 📁 to-prd/                         📝 对话 → 产品需求文档
│   │
│   ├── 📄 SKILL.md                                       (2.9 KB)
│   │   └─ 主技能文件：3 步合成流程
│   │      ① 探索代码库（领域术语 + ADR 尊重）
│   │      ② 确定测试 Seam（最高可行点的 seam → 用户确认）
│   │      ③ 按模板写 PRD → 发布 ready-for-agent
│   │
│   └── 📄 INFO.md                                        (1.0 KB)
│       └─ 技能概要：流程、PRD 模板八段结构
│
├── 📁 triage/                         🚦 Issue 分诊
│   │
│   ├── 📄 SKILL.md                                       (4.9 KB)
│   │   └─ 主技能文件：状态机驱动的 Issue 管理
│   │      bug/enhancement 分类角色 + needs-triage→needs-info↔ready-for-agent/
│   │      human/wontfix 状态角色，自然语言调用（"triage #42"）
│   │
│   ├── 📄 AGENT-BRIEF.md                                 (6.2 KB)
│   │   └─ Agent Brief 书写规范：持久性优先（不写文件路径/行号）、
│   │      行为描述而非步骤描述、完整验收标准、明确范围边界 +
│   │      ✅ 好例（bug/enhancement 各一）+ ❌ 坏例对比
│   │
│   ├── 📄 OUT-OF-SCOPE.md                                (4.3 KB)
│   │   └─ .out-of-scope/ 知识库规范：机构记忆 + 去重机制、
│   │      文件格式 × 命名规则 × 何时写/何时读/何时更新删除
│   │
│   └── 📄 INFO.md                                        (0.9 KB)
│       └─ 技能概要：角色状态机、5 步分诊流程
│
└── 📁 zoom-out/                       🔭 宏观上下文概览
    │
    ├── 📄 SKILL.md                                       (0.4 KB)
    │   └─ 主技能文件：极简 prompt，仅 430 字节
    │      "我不熟悉这段代码，上升一层抽象，给我模块地图 + 调用者图"
    │
    └── 📄 INFO.md                                        (0.5 KB)
        └─ 技能概要：功能说明
```

---

## 📐 文件角色分类

### 🔵 主技能文件（SKILL.md）— 10 个
每个技能的主指令文件，Agent 命中后读取。包含 YAML 元数据（name + description 路由标签）和 Markdown 正文（执行流程 + 约束规则）。

### 🟢 子模块文件 — 21 个
被 SKILL.md 内部引用的专项规范，负责细化特定子流程：

| 文件 | 所属技能 | 定位 |
|------|---------|------|
| `hitl-loop.template.sh` | diagnose | 反馈回路最后一招：人工在环 bash 模板 |
| `ADR-FORMAT.md` | grill-with-docs | ADR 何时写、怎么写、何时不写的判断标准 |
| `CONTEXT-FORMAT.md` | grill-with-docs | 领域术语表的格式与布局规则 |
| `LANGUAGE.md` | improve-* | 8 个核心术语精确定义（唯一真相源） |
| `DEEPENING.md` | improve-* | 4 类依赖的深化策略与测试方法 |
| `INTERFACE-DESIGN.md` | improve-* | Design It Twice：并行子代理方法 |
| `HTML-REPORT.md` | improve-* | 架构报告的前端脚手架与视觉规范 |
| `LOGIC.md` | prototype | TUI 原型制作全流程 |
| `UI.md` | prototype | UI 变体原型制作全流程 |
| `domain.md` | setup-* | 领域文档消费规则 |
| `issue-tracker-github.md` | setup-* | GitHub Issue 操作指令集 |
| `issue-tracker-gitlab.md` | setup-* | GitLab Issue 操作指令集 |
| `issue-tracker-local.md` | setup-* | 本地 Markdown Issue 操作指令集 |
| `triage-labels.md` | setup-* | 5 规范角色 ↔ 实际标签映射表 |
| `tests.md` | tdd | 好测试 vs 坏测试判据 + 代码示例 |
| `mocking.md` | tdd | Mock 策略：边界 mock、依赖注入、SDK 风格接口 |
| `deep-modules.md` | tdd | Ousterhout 深模块概念 |
| `interface-design.md` | tdd | 可测试接口三原则 |
| `refactoring.md` | tdd | 重构候选检查清单 |
| `AGENT-BRIEF.md` | triage | Agent Brief 写作规范 + 好例/坏例对比 |
| `OUT-OF-SCOPE.md` | triage | .out-of-scope/ 知识库全生命周期 |

### 🟡 文档索引文件 — 14 个
| 文件 | 定位 |
|------|------|
| `README.md` | 顶层总览：10 技能速览表 + 触发词 |
| `DECISION-TREE.md` | 路由决策树：意图→技能匹配逻辑 |
| ×12 `INFO.md` | 每个技能的基础信息速查卡 |

---

## 🔗 文件引用依赖图

```
SKILL.md (主文件)
  │
  ├──→ 引用同目录子模块 .md 文件
  │     │
  │     ├─ diagnose/SKILL.md ──→ scripts/hitl-loop.template.sh
  │     ├─ grill-with-docs/SKILL.md ──→ ADR-FORMAT.md, CONTEXT-FORMAT.md
  │     ├─ improve-*/SKILL.md ──→ LANGUAGE.md, DEEPENING.md,
  │     │                         HTML-REPORT.md, INTERFACE-DESIGN.md
  │     ├─ prototype/SKILL.md ──→ LOGIC.md, UI.md
  │     ├─ setup-*/SKILL.md ──→ domain.md, issue-tracker-*.md, triage-labels.md
  │     ├─ tdd/SKILL.md ──→ tests.md, mocking.md, deep-modules.md,
  │     │                   interface-design.md, refactoring.md
  │     └─ triage/SKILL.md ──→ AGENT-BRIEF.md, OUT-OF-SCOPE.md
  │
  ├──→ 跨技能引用（..）
  │     │
  │     ├─ improve-*/SKILL.md ──→ ../grill-with-docs/CONTEXT-FORMAT.md
  │     ├─ improve-*/SKILL.md ──→ ../grill-with-docs/ADR-FORMAT.md
  │     └─ prototype/SKILL.md ── 兄弟引用 LOGIC.md / UI.md
  │
  └──→ 无子模块的独立 skill
        ├─ to-issues/SKILL.md ── 单文件，全部逻辑内联
        ├─ to-prd/SKILL.md    ── 单文件，全部逻辑内联
        └─ zoom-out/SKILL.md  ── 单文件，极简 430B
```
