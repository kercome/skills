# Convert PDF

## Goal
Convert text-based PDF to Markdown with image extraction using Marker (preferred) or PyMuPDF (fallback).

## Flow

```
Input: path/to/document.pdf
  → Create output directory: document/
  → Create images directory: document/images/
  → Try Marker (preferred):
    → Verify marker installed
    → Run: marker_single "path/to/document.pdf" --output_dir "document/"
    → Locate generated .md file, rename to document.md
    → Move extracted images to document/images/
  → Fallback PyMuPDF (if Marker unavailable):
    → Verify PyMuPDF installed (pip install PyMuPDF)
    → Extract text page by page
    → Extract images: document/images/image_N.ext
    → Insert inline refs: ![image_N.ext](images/image_N.ext)
    → Pages separated by ---
  → Verify document/document.md exists
  → Return output directory path
```

## Image Extraction (PyMuPDF fallback)

```python
import fitz

doc = fitz.open(input_path)
for page in doc:
    for img in page.get_images(full=True):
        base_img = doc.extract_image(img[0])
        img_count += 1
        fname = f"image_{img_count}.{base_img['ext']}"
        write to document/images/fname
        md_parts.append(f"![{fname}](images/{fname})")
```

## Key Params

| Param | Type | Default | Constraint |
|-------|------|---------|------------|
| input_file | path | required | .pdf extension, text-based |
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

❌ Marker not found → try PyMuPDF fallback; if also missing → install: pip install PyMuPDF
❌ Output empty → scanned PDF (no text layer) → inform user
❌ Command fails → show stderr, suggest checking PDF is text-based

## Notes

- Marker requires Python 3.9+, produces higher quality layout
- PyMuPDF works on any Python 3.8+, simpler but page-by-page
- First Marker run downloads models (auto)
- For batch processing use marker command instead of marker_single

## Cross-refs

Depends on convert-dispatch.md for input validation and output architecture
