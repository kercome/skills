# Solution Search Strategy

## When to Search

After goal is locked (Stage 3 complete), execute at Stage 4 entry.

## Search Scope

| Source | Search pattern | Use case |
|--------|---------------|----------|
| GitHub | `{goal keywords} {domain keywords}` | Tools / libs / CLIs |
| npm | `{goal keywords}` | Node.js tools |
| pip | `{goal keywords}` | Python tools |
| API services | `{goal keywords} service/api` | Online services |

## Match Assessment

```
Results found
  → Exact match (covers goal 100%)
    → Path A: Recommend
      → Tell user: name / source / function / pros / cons
      → User confirms → fetch/install into skill directory
      → skill = call wrapper (input / output / failure / constraints)
      → User declines → ask why → switch path

  → Partial match (covers goal 50-99%)
    → Path C: Combine
      → Matched part = existing tool
      → Gap = custom script
      → Tell user the split plan
      → User confirms → implement both

  → No match
    → Path B: Build custom
      → Tell user "no existing tool found, need custom script"
      → User confirms → generate script to scripts/
      → skill = script call wrapper
```

## User Notification Format

```
🔍 Search Result:

Recommended path: {A/B/C}
{Name / source / brief function}

Pros:
- {pro 1}
- {pro 2}

Cons / Risks:
- {con 1}

Adopt this approach?
```

## Post-Fetch Directory Structure

```
skill-name/
├── SKILL.md
├── references/
├── scripts/
│   ├── {fetched tool}     ← 3rd-party tool
│   └── {custom script}    ← Custom script (if needed)
└── HUMAN-SKILL.md
```

## Wrap Principle

Regardless of underlying implementation (3rd-party or custom), skill presents unified interface to AI:

```
Input:  {what params/files}
Output: {what result}
Failure: {when it fails + how to recover}
Constraints: {what not to do / must do}
```

AI doesn't need implementation details, only the call interface.

## Common Goals → Search Directions

| Goal type | Search priority | Examples |
|-----------|----------------|---------|
| Document conversion | GitHub CLI tools | pandoc, marker, mammoth |
| File processing | Python/Node libs | pdfplumber, sharp, ffmpeg |
| Data extraction | API + libs | Tesseract OCR, Whisper |
| Web automation | Browser tools | Playwright, Puppeteer |
| Format conversion | Specialized libs | xlsx, python-docx |
| Text processing | Custom script (usually no search needed) | encoding / substitution / templates |
