# Skills - QClaw Skill Pack

This repository contains two skill packages designed for the [QClaw](https://qclaw.ai) / OpenClaw platform, enhancing AI Agent capabilities in document conversion and skill development.

---

## 📄 Skill 1: doc-md.skill — Document to Markdown

**One-click conversion of office documents into structured Markdown files.**

### Features

- Supports **DOCX / PDF / XLSX / PPTX** formats
- Automatically extracts **embedded images**, saved to a dedicated `images/` directory
- Generated Markdown includes image references: `![caption](images/image_001.png)`
- Output preserves the source filename with organized structure
- Supports custom output directory and filename

### Usage

```bash
python scripts/doc2md.py <input_file> [output_dir] [--name <custom_name>]
```

### Tech Stack

| Format | Library |
|--------|---------|
| DOCX | python-docx, pandoc |
| PDF | PyMuPDF, marker, pandoc |
| XLSX | openpyxl |
| PPTX | python-pptx |

### Output Structure

```
report/                      ← Output directory named after the source file (no ext)
├── report.md                ← Main Markdown content
└── images/                  ← Extracted images
    ├── image_001.png
    ├── image_002.png
    └── ...
```

### Limitations

- ❌ Scanned PDFs (image-only pages) not supported
- ❌ Encrypted or password-protected documents not supported
- ❌ Audio/video extraction not supported

---

## 🔨 Skill 2: skill-forge.skill — Skill Forge

**A structured skill development framework for creating QClaw / OpenClaw skills efficiently from requirements to deliverables.**

### Overview

skill-forge provides end-to-end guidance from requirements analysis to skill file generation, following an **8-stage pipeline**:

```
Collect → Abstract → Lock Goal ★user gate★ → Search Solutions → Serve Goal → User Confirm → Generate AI Version → Derive Human Version
```

### Core Principles

- **AI-SKILL.md is primary, HUMAN-SKILL.md is derived** (irreversible)
- Each stage has a gate to ensure accurate user intent capture
- Searches existing solutions before building to avoid reinventing the wheel
- Supports three modes: exact match (wrap & reuse), partial match (combine), no match (custom script + wrapper)

### Reference Files

| File | Description |
|------|-------------|
| `references/forge-flow.md` | Forge flow detailed guide |
| `references/design-principles.md` | Skill design principles |
| `references/scene-split.md` | Scene split guide |
| `references/solution-search.md` | Solution search strategy |

### Use Cases

- Creating a brand new skill
- Modifying/updating/upgrading an existing skill
- Unsure how to design skill structure and trigger keywords
- Splitting a complex skill into multiple independent skills

---

## Quick Start

1. Place these two skill directories into QClaw's skills load path
2. Enable the desired skills in QClaw configuration
3. Configure trigger keywords and parameters according to each skill's SKILL.md

## License

This project is licensed under the MIT License.
