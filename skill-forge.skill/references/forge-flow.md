# Forge Flow — Full 8-Stage Pipeline

## Stage 1: Collect

Extract signals from user's words:

| User says | Extract |
|-----------|---------|
| "Make a skill for X" | Topic + intent |
| "I keep repeating X every time" | Pain point + repeat pattern |
| "Can AI auto-handle X" | Automation target |
| "Skill should do X" | Design preference |
| Drops link/file | Content source → distill direction |

AI behavior: no explaining what a skill is, go straight to collection. Unclear parts → give options. No design judgment, only collection.

Follow-up probes:
- Target reader? (AI itself / end user / both)
- Trigger scenario?
- Expected output?

---

## Stage 2: Abstract

Distill into: **When [trigger condition], do [action], achieving [effect]**

Examples:
- ❌ "A skill that helps write files, watch out for encoding"
- ✅ "When writing text files, auto-match target platform encoding, ensure zero garble cross-platform"

AI behavior:
- Too specific → abstract up (concrete problem → general pattern)
- Too vague → concrete down (vague intent → specific scenario)
- Must get user confirmation

---

## Stage 3: Lock Goal ★User Gate★

AI converges, user confirms goal.

Convergence loop:
```
User speaks → AI distills into goal → User corrects → AI re-distills → User confirms → Locked
```

Four convergence rules:
1. **One goal per iteration** — no menus, propose the most likely distillation
2. **User's language** — keep original keywords, no jargon substitution
3. **Subtract, don't add** — user says 3 things → ask "same goal?"
4. **Flag "and/plus"** — two independent intents → ask if split needed

Goal format: **This skill exists for one reason: [one sentence]**

Validation:
- Verifiable: can judge if skill achieves it
- Non-redundant: removing any word breaks completeness
- In-scope: doesn't include what skill won't do
- Contains "and/plus" with independent intents → split skill

---

## Stage 4: Search & Path Select

Search existing tools/libs/APIs → match assessment → recommend path.

Search scope:
- GitHub: `{goal keywords} {domain keywords}`
- npm/pip: `{goal keywords}`
- API services: `{goal keywords} service/api`

Path selection:

| Match | Path | Action |
|-------|------|--------|
| Exact | A: Use existing | Recommend → user confirms → fetch/install → skill=call wrapper |
| Partial | C: Combine | Matched part=existing + gap=custom → user confirms → implement both |
| None | B: Build custom | Inform user → confirm → generate script → skill=script wrapper |

Tell user: what it is / source / pros / cons / why recommended.
User declines → ask why → switch path.

Wrap principle: skill doesn't care about underlying implementation. Unified interface: input / output / failure handling / constraints.

---

## Stage 5: Serve Goal

Based on chosen solution, expand:

### Alignment Gate

| Problem type | AI behavior | Output |
|-------------|-------------|--------|
| Ambiguity | Convert to options, no guessing | ❓ Clarify: {option A/B/C} |
| Conflict | Expose conflict, offer trade-offs | ⚠️ Conflict: {A} vs {B} → pick one? |
| Missing decision | List decision points + options | 🔲 Unspecified: {decision} → {A/B/C} |

Any unresolved → halt at alignment, do not proceed.

### Scene Split

Total content > 2000 words → split → identify independent scenes → each gets own reference → SKILL.md keeps only routing.

Single reference > 1500 words → sub-split within that scene.

Split signals:
| Signal | Split direction |
|--------|----------------|
| 3+ unrelated operations | By operation |
| "also need to..." appears 2+ | By goal |
| Single flow > 5 branches | By branch |
| Different systems/APIs/data sources | By domain |
| Some features condition-only | By frequency (hot=resident, cold=reference) |

### Constraints

❌ Forbidden paths (what not to do / must do differently)
✅ Required paths

### Auto Decisions

Default behavior when user doesn't specify — declare explicitly.

### Failure Modes

Identify → cause → recovery.

### Implicit Needs (AI proactively fills)

- Compatibility: cross-platform / cross-version / cross-model
- Safety: no data leakage / operations reversible
- Performance: large data / high frequency
- Degradation: fallback when script unavailable

---

## Stage 6: User Confirm

Confirm item by item:
- ✅ Final goal correct
- ✅ Implementation path approved
- ✅ Scene split reasonable
- ✅ Constraints and defaults accepted

**No confirmation = no generation.**

---

## Stage 7: Generate AI-SKILL.md + references/ + tools/scripts

### AI-SKILL.md template

```markdown
---
name: {skill-name}
description: "{trigger keywords}. {negative boundary}. {constraints}"
---

## Trigger Routes

{condition1} → load references/{ref1}.md
{condition2} → load references/{ref2}.md
No match → exit

## Constraints

❌ {forbidden paths}
✅ {required paths}

## Auto Decisions

{unspecified X} → {default behavior}

## Failure Modes

❌ {symptom} → {cause} → {recovery}

## Dependencies

{scripts/tools/env, relative paths}
```

### Reference template

```markdown
# {Scene Name}

## Goal
{One sentence}

## Flow
{Decision tree}

## Key Params
{param}: {type} | {default} | {constraint}

## Failure Modes
❌ {symptom} → {cause} → {recovery}

## Cross-refs
{depends on} → load references/{other}.md
```

---

## Stage 8: Derive HUMAN-SKILL.md

Derived from AI-SKILL.md. Direction irreversible (AI→Human).

### HUMAN-SKILL.md template

```markdown
# {Skill Name}

## What It Does
{Natural language, includes motivation}

## When It Activates
{Scenario description}

## How It Works
{Steps + reason for each}

## Decisions AI Makes For You
- {decision}: {default behavior} (override via {method})

## Capability Modules
| Module | When Triggered | What It Does |
|--------|---------------|-------------|

## Troubleshooting
{Symptom → cause → fix}

## Customization
{Overridable params + how}
```
