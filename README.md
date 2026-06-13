# Skills - QClaw 技能包

本仓库包含两个为 [QClaw](https://qclaw.ai) / OpenClaw 平台设计的技能包，用于增强 AI Agent 的文档转换与技能开发能力。

---

## 📄 技能一：doc-md.skill — 文档转 Markdown

**一键将办公文档转换为结构化的 Markdown 文件。**

### 功能特性

- 支持 **DOCX / PDF / XLSX / PPTX** 四大主流格式
- 自动提取文档中的**内嵌图片**，保存到独立的 `images/` 目录
- 生成的 Markdown 中包含图片引用：`![caption](images/image_001.png)`
- 输出保持源文件名，组织结构清晰
- 支持自定义输出目录和文件名

### 使用方式

```bash
python scripts/doc2md.py <input_file> [output_dir] [--name <custom_name>]
```

### 技术栈

| 文档格式 | 依赖库 |
|---------|--------|
| DOCX | python-docx, pandoc |
| PDF | PyMuPDF, marker, pandoc |
| XLSX | openpyxl |
| PPTX | python-pptx |

### 输出结构

```
report/                      ← 以源文件（无扩展名）命名的输出目录
├── report.md                ← 主 Markdown 内容
└── images/                  ← 提取的图片
    ├── image_001.png
    ├── image_002.png
    └── ...
```

### 限制说明

- ❌ 不支持扫描版 PDF（纯图片页面）
- ❌ 不支持加密或密码保护文档
- ❌ 不支持音视频提取

---

## 🔨 技能二：skill-forge.skill — 技能锻造

**一个结构化的技能开发框架，帮助用户从需求到成品高效创建 QClaw / OpenClaw 技能。**

### 功能介绍

skill-forge 提供从需求分析到技能文件生成的全流程引导，遵循 **8 阶段流水线**：

```
收集 → 抽象 → 锁定目标 ★用户确认★ → 搜索方案 → 服务目标 → 用户确认 → 生成 AI 版本 → 派生人类版本
```

### 核心原则

- **AI-SKILL.md 为主，HUMAN-SKILL.md 派生**（不可逆）
- 每个阶段设有关卡，确保用户意图准确锁定
- 在创建前先搜索已有解决方案，避免重复造轮子
- 支持精确匹配（包装复用）、部分匹配（组合）、无匹配（自定义脚本 + 包装）三种模式

### 包含的参考文件

| 文件 | 说明 |
|------|------|
| `references/forge-flow.md` | 锻造流程详细指南 |
| `references/design-principles.md` | Skill 设计原则 |
| `references/scene-split.md` | 场景拆分指南 |
| `references/solution-search.md` | 解决方案搜索策略 |

### 适用场景

- 需要创建全新技能时
- 需要修改/更新/升级已有技能时
- 不确定如何设计技能结构和触发词时
- 需要拆分复杂技能为多个独立技能时

---

## 快速开始

1. 将这两个技能目录放入 QClaw 的 skills 加载路径中
2. 在 QClaw 配置中启用所需技能
3. 按照各技能的 SKILL.md 配置触发词和参数

## 许可

本项目采用 MIT 许可证。
