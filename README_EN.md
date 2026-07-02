# QClaw Skills Repository

A collection of practical skills for the QClaw / OpenClaw platform, covering document conversion, video processing, engineering development, and AI-assisted creation.

## 📦 Skills Directory

### 📄 Document & Format Conversion

| Skill | Description | Trigger Phrases |
|-------|-------------|-----------------|
| **doc-md.skill** | Document to Markdown: batch convert DOCX, PDF, XLSX, PPTX with image extraction and formatting preservation | `文档转Markdown` `doc to md` `word to markdown` `pdf to markdown` `xlsx to markdown` `pptx to markdown` `document conversion` |
| **yuque-scraper** | Yuque Knowledge Base Scraper: one-click download of any public Yuque knowledge base to local Markdown files with directory structure preserved | `拉取语雀知识库` `download yuque docs` `backup yuque kb` `export yuque` `scrape yuque` |

### 🎬 Video Processing

| Skill | Description | Trigger Phrases |
|-------|-------------|-----------------|
| **info-aware-slicer** | Information-aware Video Slicer: adaptive sampling based on motion detection + tail-head template matching for gap detection. Outputs sliced images and document_chain.json. Ideal for document/webpage screencasts | `视频切片` `video slicing` `video to images` `extract document frames` `slice every page from video` |
| **smart-dedup** | Smart Video Slice Deduplication: SSIM 3-tier structural similarity filtering + EasyOCR gray-zone arbitration. Automatically identifies and removes duplicate frames from PPT recordings, code demos, and web scrolling videos | `去重` `deduplicate` `remove duplicates` `smart dedup` `duplicate frames` |

### 🛠 Engineering Development — gril-me/engineering/

A collection of 9 development-assistant skills adapted from Matt Pocock's engineering skill set.

| Skill | Description | Trigger Phrases |
|-------|-------------|-----------------|
| **diagnose** | Disciplined diagnosis loop: Reproduce → Minimize → Hypothesize → Instrument → Fix → Regression-test. For hard bugs and performance regressions | `diagnose this` `debug this` `bug` `broken` `throwing` `failing` `performance regression` |
| **grill-with-docs** | Documentation grilling session: challenges your plan against the domain model, sharpens terminology, and updates CONTEXT.md and ADRs inline | `grill with docs` `document review` `ADR` `stress-test plan` `decision review` |
| **improve-codebase-architecture** | Architecture improvement: find deepening opportunities, consolidate tightly-coupled modules, improve testability and AI-navigability | `improve architecture` `refactoring` `improve codebase` `find opportunities` |
| **prototype** | Rapid prototyping: terminal app for state/business-logic questions, multi-style UI variations for design exploration | `prototype` `mock up` `sanity-check` `try a few designs` `quick prototype` |
| **setup-matt-pocock-skills** | Initialize engineering skill environment: configures `## Agent skills` block in AGENTS.md and `docs/agents/` so all skills know the project's issue tracker, triage labels, and domain doc layout | `setup skills` `initialize skill environment` |
| **tdd** | Test-Driven Development: standard red → green → refactor cycle with integration and unit testing | `TDD` `red-green-refactor` `test-driven` `test-first development` |
| **to-issues** | Plan to Issues: break a plan/spec/PRD into independently-grabbable issues using tracer-bullet vertical slices | `break into issues` `create tickets` `plan to issues` `break down work` |
| **to-prd** | Context to PRD: distill the current conversation context into a Product Requirements Document and publish to the issue tracker | `create PRD` `PRD` `product requirements document` |
| **triage** | Issue Triage: state-machine-driven issue management through triage roles, managing full issue lifecycle | `triage` `issue workflow` `triage issues` `manage issues` |
| **zoom-out** | High-level perspective: when unfamiliar with a section of code, step back to see the bigger picture | `zoom out` `broad context` `high-level view` |

### 🤖 AI-Assisted Creation — builtin-skills-workbuddy/

5 skills from the WorkBuddy built-in collection.

| Skill | Description | Trigger Phrases |
|-------|-------------|-----------------|
| **ardot-design-assistant** | Ardot Design Assistant: unified entry for all visual design tasks—pages, screens, layouts, components, dashboards, landing pages, mobile apps, style guides, design systems, and design-to-code conversion via Ardot MCP Server | `generate a page` `create a landing page` `make a dashboard` `design a screen` `create wireframe` `build a UI` `generate slides` `design to code` `convert design to HTML` |
| **buddy-multimodal-generation** | Multimodal Content Generation: text-to-video, text-to-3D, image-to-3D, and template-based image/video effects via cloud services | `generate video` `text to video` `generate 3D` `image to 3D` `video effects` `AI generate` |
| **cloudstudio-deploy** | CloudStudio Deployment: deploy local static site build directories to CloudStudio sandbox with shareable preview URLs | `deploy` `deploy to cloudstudio` `preview` `publish` `static site deployment` |
| **expert-manager** | Expert Package Manager: full lifecycle operations—create experts from repos/projects, modify, validate, batch update, quality review | `create expert` `convert expert` `expert ops` `modify expert` `review expert` |
| **skill-creator** | Skill Creator: standard workflow and best practices for creating and updating high-quality skills | `create skill` `create a new skill` `update skill` `skill creation` |

### 🎯 Skill Creation Tools

| Skill | Description | Trigger Phrases |
|-------|-------------|-----------------|
| **skill-forge.skill** | Skill Forge: 8-stage automated pipeline—from requirements analysis, research, framework design to code generation—forge complete QClaw/OpenClaw skills in one shot | `创建Skill` `forge a skill` `build a skill` `create a skill` `generate skill` |

---

## 🚀 Usage

### Method 1: Import to QClaw

1. Copy the desired skill directory to QClaw's skills load path (e.g. `C:\Users\<username>\.qclaw\skills\`)
2. Enable the skill under `skills.entries` in `openclaw.json`
3. Restart QClaw Gateway

### Method 2: Standalone

Each skill directory contains standalone Python scripts. Run them directly from the command line. See SKILL.md in each skill directory for details.

---

## 📂 Repository Structure

```
skills/
├── doc-md.skill/              # Document to Markdown
├── skill-forge.skill/          # Skill Forge Tool
├── info-aware-slicer/          # Video Smart Slicer
├── smart-dedup/                # Slice Smart Dedup
├── yuque-scraper/              # Yuque KB Scraper
├── gril-me/engineering/        # Engineering Skills (9)
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
├── builtin-skills-workbuddy/   # AI Creation Skills (5)
│   ├── ardot-design-assistant/
│   ├── buddy-multimodal-generation/
│   ├── cloudstudio-deploy/
│   ├── expert-manager/
│   └── skill-creator/
├── README.md
└── README_EN.md
```

---

## 🤝 Contributing

Issues and PRs are welcome. New skills should include:
- `SKILL.md` (required): yaml front matter (name, description) and complete workflow
- `references/` (optional): reference materials
- `scripts/` (optional): executable scripts
