# Convert PowerPoint (PPTX/PPT)

## Goal
Convert PowerPoint presentation to Markdown with image extraction using Python script.

## Flow

```
Input: path/to/presentation.pptx
  → Create output directory: presentation/
  → Create images directory: presentation/images/
  → Verify Python + python-pptx installed
    → No → emit: pip install python-pptx
  → Run: python scripts/pptx2md.py "path/to/presentation.pptx" "presentation/presentation.md"
  → Script extracts:
    - Slide number
    - Slide title (first text frame)
    - Bullet points / text content
    - Embedded images → presentation/images/image_N.ext
    - Inline image refs inserted at slide position
  → Verify presentation/presentation.md exists
  → Return output directory path
```

## Image Extraction

```python
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

for slide in prs.slides:
    for shape in slide.shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            image = shape.image
            img_count += 1
            fname = f"image_{img_count}.{image.content_type.split('/')[-1]}"
            write to presentation/images/fname
            md_parts.append(f"![{fname}](images/{fname})")
```

## Key Params

| Param | Type | Default | Constraint |
|-------|------|---------|------------|
| input_file | path | required | .pptx or .ppt |
| output_dir | path | same as input | writable |

## Output Architecture

```
presentation/               ← named directory
├── presentation.md         ← Markdown slides + inline image refs
└── images/                 ← extracted slide images
    ├── image_1.png
    ├── image_2.jpg
    └── ...
```

## Output Format

```markdown
# Slide 1: Title of Slide

- Bullet point 1
- Bullet point 2

![slide_image](images/image_1.png)

# Slide 2: Next Title

Content text...
```

## Failure Modes

❌ python-pptx not found → pip install python-pptx
❌ File corrupted → inform user
❌ Empty slide → skip with note

## Cross-refs

Depends on convert-dispatch.md for input validation and output architecture
