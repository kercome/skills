# QClaw Skills 仓库

一个面向 QClaw / OpenClaw 平台的实用技能（Skill）集合，覆盖文档转换、视频处理、工程开发、AI 创作等多个领域。

## 📦 技能列表

### 📄 文档与格式转换

| Skill | 说明 | 触发提示词 |
|-------|------|-----------|
| **doc-md.skill** | 文档转 Markdown：支持 DOCX、PDF、XLSX、PPTX 批量转换，含图片提取与格式保持 | `文档转Markdown` `doc转md` `word转markdown` `pdf转markdown` `xlsx转markdown` `pptx转markdown` `docx转md` `ppt转md` `文档转换` |
| **yuque-scraper** | 语雀知识库批量拉取：一键下载任意公开语雀知识库全部文档到本地 Markdown，自动提取目录结构并按原文档层级保存 | `拉取语雀知识库` `下载语雀文档` `备份语雀知识库` `导出语雀内容` `语雀知识库下载` `爬语雀` |

### 🎬 视频处理

| Skill | 说明 | 触发提示词 |
|-------|------|-----------|
| **info-aware-slicer** | 视频智能切片：基于运动感知的自适应步长采样 + 尾首模板匹配断层检测，输出切片图片和 document_chain.json 状态链。尤其适用于文档/网页录屏视频的动态切片 | `视频切片` `录屏切片` `视频转图片` `提取文档帧` `视频每一页切出来` `info_aware_slicer` |
| **smart-dedup** | 切片智能去重：SSIM 结构相似度三层分流 + EasyOCR 灰色地带裁决，自动识别 PPT 录屏、代码演示、网页滚动场景下的重复帧并移除 | `去重` `视频切片去重` `图片去重` `智能去重` `重复帧` `去掉重复图片` `smart_dedup` |

### 🛠 工程开发 — gril-me/engineering/

一套来自 Matt Pocock 工程技能集的 9 个开发辅助 skill。

| Skill | 说明 | 触发提示词 |
|-------|------|-----------|
| **diagnose** | 严格诊断循环：复现 → 最小化 → 假设 → 插桩 → 修复 → 回归测试。用于疑难 Bug 和性能回归 | `diagnose this` `debug this` `诊断` `调试` `bug` `broken` `throwing` `failing` `性能回归` |
| **grill-with-docs** | 文档对抗审查：用领域模型挑战你的计划，打磨术语，同步更新 CONTEXT.md 和 ADR | `grill with docs` `文档审查` `ADR` `stress-test plan` `决策审查` |
| **improve-codebase-architecture** | 架构改进：发现代码库中的深化机会，识别紧耦合模块，提升可测试性和 AI 导航性 | `improve architecture` `refactoring` `improve codebase` `架构改进` `重构` `代码结构优化` |
| **prototype** | 快速原型：数据处理/状态机问题走终端 App 路线，UI 探索走多风格切换路线，投石问路不先造轮子 | `prototype` `原型` `mock up` `sanity-check` `try a few designs` `快速原型` `试几种设计` |
| **setup-matt-pocock-skills** | 初始化工程技能环境：在 AGENTS.md 中配置 `## Agent skills` 块和 `docs/agents/`，使所有技能知晓项目的 Issue Tracker、Triage Labels、领域文档布局 | `setup skills` `initialize skill environment` `初始化技能` `配置工程技能` |
| **tdd** | 测试驱动开发：标准的 red → green → refactor 循环，包含集成测试与单元测试 | `TDD` `red-green-refactor` `test-driven` `测试驱动` `测试驱动开发` |
| **to-issues** | 计划拆 Issue：将计划/规格/PRD 拆分为可独立领取的 Issue，采用 tracer-bullet 纵向切片 | `break into issues` `create tickets` `plan to issues` `转成issue` `拆分任务` |
| **to-prd** | 上下文转 PRD：将当前对话上下文提炼为产品需求文档并发布到 Issue Tracker | `create PRD` `PRD` `产品需求文档` `写PRD` |
| **triage** | Issue 状态机管理：通过分诊角色驱动状态流转，管理 issue 的全生命周期 | `triage` `issue workflow` `分类` `分流` `issue管理` `issue流程` |
| **zoom-out** | 高层视角：当你不熟悉某段代码或需要理清它在全局中的位置时，让你退一步看清全局 | `zoom out` `broad context` `高层视角` `全局视角` |

### 🤖 AI 辅助创作 — builtin-skills-workbuddy/

来自 WorkBuddy 内置的 5 个技能。

| Skill | 说明 | 触发提示词 |
|-------|------|-----------|
| **ardot-design-assistant** | Ardot 设计助手：所有视觉设计任务的统一入口——页面、屏幕、布局、组件、仪表盘、落地页、移动App、风格指南、设计系统，以及设计稿转代码。所有操作走 Ardot MCP Server | `generate a page` `create a landing page` `make a dashboard` `design a login screen` `create wireframe` `build a UI` `generate slides` `生成页面` `设计页面` `制作PPT` `设计稿转代码` `生成HTML` `复刻设计稿` |
| **buddy-multimodal-generation** | 多模态内容生成：支持文生视频、文生3D、图生3D 以及基于模板的图片视频特效 | `生成视频` `文生视频` `生成3D` `图生3D` `视频特效` `AI生成` `帮我做一个视频` `生成一段` |
| **cloudstudio-deploy** | CloudStudio 部署：将本地静态站点构建目录部署到 CloudStudio 沙箱，获取可分享的在线预览链接 | `deploy` `deploy to cloudstudio` `部署` `预览` `publish` `发布静态站点` |
| **expert-manager** | 专家包管理器：全生命周期运营——从开源仓库/本地项目创建专家包、修改已有专家、合规检查、批量更新、质量审查 | `创建专家` `转化专家` `生成专家包` `导入专家` `expert ops` `修改专家` `审查专家` |
| **skill-creator** | Skill 创建器：指导创建和更新高质量 skill 的标准流程与最佳实践 | `create skill` `create a new skill` `创建skill` `创建技能` `更新skill` |

### 🎯 Skill 创建工具

| Skill | 说明 | 触发提示词 |
|-------|------|-----------|
| **skill-forge.skill** | 技能锻造：8 阶段自动流水线，从需求分析、调研、框架设计到代码生成，一次性锻造完整的 QClaw/OpenClaw 技能 | `创建Skill` `生成技能` `锻造技能` `制作一个skill` `写个技能` `create a skill` `forge a skill` `build a skill` |

---

## 🚀 使用方式

### 方法一：导入到 QClaw

1. 将需要的 skill 目录复制到 QClaw 的 skills 加载路径（如 `C:\Users\<用户名>\.qclaw\skills\`）
2. 在 `openclaw.json` 中 `skills.entries` 启用对应 skill
3. 重启 QClaw Gateway

### 方法二：直接使用

每个 skill 目录都包含独立的 Python 脚本，可直接从命令行调用。详见各 skill 目录下的 SKILL.md。

---

## 📂 仓库结构

```
skills/
├── doc-md.skill/              # 文档转 Markdown
├── skill-forge.skill/          # 技能锻造工具
├── info-aware-slicer/          # 视频智能切片
├── smart-dedup/                # 切片智能去重
├── yuque-scraper/              # 语雀知识库拉取
├── gril-me/engineering/        # 工程开发技能集（9 个）
│   ├── diagnose/
│   ├── grill-with-docs/
│   ├── improve-codebase-architecture/
│   ├── prototype/
│   ├── setup-matt-pocock-skills/
│   ├── tdd/
│   ├── to-issues/
│   ├── to-prd/
│   ├── triage/
│   └── zoom-out/
├── builtin-skills-workbuddy/   # AI 创作技能集（5 个）
│   ├── ardot-design-assistant/
│   ├── buddy-multimodal-generation/
│   ├── cloudstudio-deploy/
│   ├── expert-manager/
│   └── skill-creator/
├── README.md
└── README_EN.md
```

---

## 🤝 贡献

欢迎提交 Issue 和 PR。新 skill 需包含：
- `SKILL.md`（必选）：包含 yaml front matter（name, description）和完整工作流
- `references/`（可选）：参考资料
- `scripts/`（可选）：执行脚本
