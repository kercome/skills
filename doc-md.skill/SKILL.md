---
name: doc2md
description: "Triggers on document-to-markdown requests. Converts DOCX/PDF/XLSX/PPTX to .md files with embedded image extraction."
---

## Trigger Routes

User says "转成 md" / "转为 Markdown" / "提取内容" + file attached → load references/convert-dispatch.md
DOCX file detected → load references/convert-word.md
PDF file detected → load references/convert-pdf.md
XLSX/XLS file detected → load references/convert-excel.md
PPTX/PPT file detected → load references/convert-ppt.md
No match → exit

## Usage

```bash
python scripts/doc2md.py <input_file> [output_dir] [--name <custom_name>]
```

Parameters:
- `input_file` (required): Path to the source document
- `output_dir` (optional): Parent directory for output (default: same as input)
- `--name` / `-n` (optional): Custom output directory/file name (default: input file stem)

## Constraints & Capabilities

✅ Document text → Markdown
✅ Image extraction from all supported formats (PDF, DOCX, XLSX, PPTX)
✅ Inline image references in output Markdown (`![name](images/xxx.png)`)
✅ Output wrapped in a named directory (same as source filename without extension)
❌ No scanned PDF OCR (image-only pages have no text to extract)
❌ No password-protected or encrypted documents
❌ No audio/video extraction

## Output Architecture

Every conversion produces a **named output directory** (same as source filename, no extension).
All output files reside inside this directory.

```
example/                    ← named directory = source filename (no ext)
├── example.md              ← main Markdown content
└── images/                 ← all extracted images live here
    ├── image_1.png
    ├── image_2.png
    └── ...
```

Rules:
- Directory name = source file stem (e.g. `report.pdf` → `report/`)
- `example.md` contains full text + inline image refs: `![caption](images/image_1.png)`
- All images go into `images/` subdirectory inside the named directory
- Image filenames: `image_N.ext` (1-based sequence number, zero-padded to 3 digits: `image_001.png`)
- Image format preserved from source (png/jpg/jpeg/gif/bmp)

## Auto Decisions

Output path unspecified → create named directory in same directory as input file
Format ambiguous → infer from file extension
Tool not installed → emit installation command and halt

## Failure Modes

❌ Output empty → scanned PDF or encrypted file → inform user
❌ Format unsupported → reject with supported format list
❌ Tool missing → provide install command, do not proceed

## Dependencies

scripts/doc2md.py | pandoc | marker | PyMuPDF | python-docx | openpyxl | python-pptx
