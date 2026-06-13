# Convert Dispatch

## Goal
Receive document file, identify format, delegate to specialized converter, return output directory path.

## Flow

```
User request + file
  → Check file extension
    → .docx → convert-word.md
    → .pdf  → convert-pdf.md
    → .xlsx/.xls → convert-excel.md
    → .pptx/.ppt → convert-ppt.md
    → other → reject with supported list
  → Create output directory: <input_stem>/
  → Create images subdirectory: <input_stem>/images/
  → Execute conversion (text + image extraction)
  → Verify <input_stem>/<input_stem>.md exists
  → Verify images/ has extracted images (if any)
  → Return output directory path
```

## Output Architecture

```
<input_stem>/               ← named directory = source filename (no ext)
├── <input_stem>.md         ← main Markdown content
└── images/                 ← all extracted images
    ├── image_1.png
    └── image_2.png
```

## Key Params

| Param | Type | Default | Constraint |
|-------|------|---------|------------|
| input_file | path | required | must exist, readable |
| output_dir | path | same as input | must be writable |

## Failure Modes

❌ Extension not in [.docx, .pdf, .xlsx, .xls, .pptx, .ppt] → reject
❌ File not found → halt, inform user
❌ Permission denied → halt, inform user
❌ Output directory creation fails → halt, inform user

## Cross-refs

DOCX → convert-word.md
PDF → convert-pdf.md
Excel → convert-excel.md
PPT → convert-ppt.md
