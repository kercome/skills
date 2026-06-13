# Scene Split Decisions

## Split Judgment

```
Total content > 2000 words?
  → Yes → Split
    → Identify independent scenes
    → Each scene gets own reference file
    → SKILL.md keeps only routing + constraints + load instructions
  → No → Single file

Single reference > 1500 words?
  → Yes → Sub-split within that scene
  → No → Passes
```

## Split Detection Signals

| Signal | Split direction | Example |
|--------|----------------|---------|
| 3+ unrelated operations | By operation | auth / payment / report → separate references |
| "also need to..." ×2+ | By goal | encode + backup → two references |
| Single flow > 5 branches | By branch | 5+ format conversions → split by format |
| Different systems/APIs/sources | By domain | WeChat API / Feishu API → separate |
| Some features condition-only | By frequency | Hot path=resident + cold path=reference |

## Post-Split Directory Structure

```
skill-name/
├── SKILL.md              ← Routing + constraints + load instructions (≤300w)
├── references/
│   ├── scene-a.md        ← Scene A (≤1500w)
│   ├── scene-b.md        ← Scene B (≤1500w)
│   └── scene-c.md        ← Scene C (≤1500w)
└── HUMAN-SKILL.md        ← Derived human-readable version
```

## SKILL.md Routing Pattern

```markdown
## Trigger Routes

{trigger A} → load references/scene-a.md
{trigger B} → load references/scene-b.md
{trigger C} → load references/scene-c.md
No match → exit, load nothing
```

## Cross-References Between Scenes

When scenes depend on each other, declare inside the reference:

```markdown
## Cross-refs
{depends on scene} → load references/{other}.md
```

- Hard dependency (A must precede B) → declare execution order in SKILL.md
- Soft dependency (A output = B optional input) → cross-ref inside reference
- No dependency → fully independent

## When NOT to Split

- Content ≤ 2000 words → single file
- Scenes tightly coupled (splitting makes them incomprehensible alone) → keep single
- Single trigger entry point → don't split
