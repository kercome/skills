# Design Principles & Output Spec

## 8 Principles

| # | Principle | Practice |
|---|-----------|----------|
| P1 | AI-first | Keywords + constraints + decision trees, no explanations |
| P2 | Precise triggering | description = routing + boundary only, ≤50 words |
| P3 | Authorized decisions | Explicitly declare "when unspecified, AI does X" |
| P4 | Failures first | Document forbidden paths before success flows |
| P5 | Scan-friendly | Conditional branches / decision trees, not linear prose |
| P6 | Prompt-driven | Keywords let AI self-propel, no hand-holding steps |
| P7 | Existing tools first | Search > build, no reinventing wheels |
| P8 | User sovereignty | AI recommends, user decides, no black-box choices |

## Dual Output Architecture

```
Primary: AI-SKILL.md + references/ + tools/scripts
  → For: Agent / AI / Vibe Coding products
  → Keywords + constraints + decision trees, no explanation

Derived: HUMAN-SKILL.md
  → For: Human users
  → Derived from AI-SKILL.md, explains motivation + reasons + troubleshooting
  → Agent NEVER reads this file
  → Direction: irreversible (AI→Human only)
```

Mixing both = AI filters walls of text to find instructions; humans guess at decision trees. Serves neither.

## Context Budget

| Category | When loaded | Budget |
|----------|------------|--------|
| description | Always (resident) | ≤50 words |
| SKILL.md body | Always (resident) | ≤300 words |
| reference file | On-demand (per scene) | ≤1500 words each |

Rule: minimize resident overhead. Isolate on-demand by scene. Never load everything "just in case."

## Description Compression

description's sole job: let routing judge "should I load this skill?"

✅ Required: trigger keywords + negative boundary + constraints
❌ Remove: feature explanations / how-it-works / scenarios / examples

Examples:
- ❌ "A skill that helps users write text files, supports auto encoding detection and line ending adaptation, works on different operating systems"
- ✅ "Triggers on text file write. Auto-matches encoding and line endings. Does not handle binary files."

## Wrap Principle

Skill doesn't care about underlying implementation (3rd-party tool / custom script). Unified call interface:
- Input: what
- Output: what
- Failure: how to handle
- Constraints: what not to do

AI reading skill doesn't need to know implementation source, only the call interface.

## Sync Rule

When modifying skill: update AI-SKILL.md first → then sync derived HUMAN-SKILL.md.
Direction irreversible.
