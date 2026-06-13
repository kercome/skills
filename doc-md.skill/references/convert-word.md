# Convert Word (DOCX)

## Goal
Convert .docx file to Markdown with image extraction using Pandoc or python-docx.

## Flow

```
Input: path/to/document.docx
  → Create output directory: document/
  → Create images directory: document/images/
  → Try Pandoc (preferred):
    → Verify pandoc installed (which pandoc)
    → Run: pandoc "path/to/document.docx" -o "document/document.md" --extract-media=document/
    → Move extracted media to document/images/, rename to image_N.ext
    → Update image refs in .md to images/image_N.ext format
  → Fallback python-docx (if Pandoc unavailable):
    → Verify python-docx installed (pip install python-docx)
    → Extract paragraphs + inline images
    → Images saved as document/images/image_N.ext
    → Insert inline refs: ![image_N.ext](images/image_N.ext)
  → Verify document/document.md exists
  → Return output directory path
```

## Image Extraction

Pandoc with `--extract-media` saves images to a subdirectory. Post-process to:
1. Move all images into `document/images/`
2. Rename to `image_N.ext` format
3. Update Markdown references

## Key Params

| Param | Type | Default | Constraint |
|-------|------|---------|------------|
| input_file | path | required | .docx extension |
| output_dir | path | same as input | writable |

## Output Architecture

```
document/                   ← named directory
├── document.md             ← Markdown with text + inline image refs
└── images/                 ← extracted images
    ├── image_1.png
    ├── image_2.jpg
    └── ...
```

## Failure Modes

❌ Pandoc not found → try python-docx fallback; if also missing → install: pip install python-docx
❌ Output empty → corrupted docx or all images → inform user
❌ Command fails → show stderr to user

## Cross-refs

Depends on convert-dispatch.md for input validation and output architecture
