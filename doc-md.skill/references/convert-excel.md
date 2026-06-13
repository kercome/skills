# Convert Excel (XLSX/XLS)

## Goal
Convert Excel spreadsheet to Markdown tables with embedded chart/image extraction using Python script.

## Flow

```
Input: path/to/spreadsheet.xlsx
  → Create output directory: spreadsheet/
  → Create images directory: spreadsheet/images/
  → Verify Python + openpyxl installed
    → No → emit: pip install openpyxl
  → Run: python scripts/xlsx2md.py "path/to/spreadsheet.xlsx" "spreadsheet/spreadsheet.md"
  → Script reads all sheets
  → Each sheet → Markdown table
  → Extract embedded images/charts → spreadsheet/images/image_N.ext
  → Insert inline refs in .md where images appear
  → Verify spreadsheet/spreadsheet.md exists
  → Return output directory path
```

## Key Params

| Param | Type | Default | Constraint |
|-------|------|---------|------------|
| input_file | path | required | .xlsx or .xls |
| output_dir | path | same as input | writable |

## Output Architecture

```
spreadsheet/                ← named directory
├── spreadsheet.md          ← Markdown tables + inline image refs
└── images/                 ← extracted charts/images
    ├── image_1.png
    └── ...
```

## Output Format

```markdown
# Sheet: SheetName

| Column1 | Column2 | Column3 |
|---------|---------|---------|
| data1   | data2   | data3   |

![chart](images/image_1.png)

# Sheet: AnotherSheet

| ... |
```

## Failure Modes

❌ openpyxl not found → pip install openpyxl
❌ File corrupted → inform user
❌ Empty sheet → skip with note

## Cross-refs

Depends on convert-dispatch.md for input validation and output architecture
