---
name: skill-forge
description: "触发词：做skill、创建skill、制作skill、写skill、开发skill、修改skill、更新skill、升级skill、skill模板、skill框架、skill结构、锻造skill、技能制作、技能创建、技能开发、怎么创建一个skill、帮我做个skill、我不想每次都手动做。也保留英文触发。NOT for: 使用现有skill、询问什么是skill、skill概念科普。EN: make skill, create skill, build skill, skill forge, update skill."
---

# Skill Tool

## Trigger Routes

Creating/updating skill → load references/forge-flow.md
"how to write a skill" → load references/design-principles.md
Scene split needed → load references/scene-split.md
Solution search needed → load references/solution-search.md
No match → exit

## Constraints

❌ Never decide for user — propose options, user chooses
❌ Never advance without confirmed goal
❌ Never bulk-load references — by scene only
❌ No human explanations in AI-SKILL.md
✅ description ≤ 50w | SKILL.md body ≤ 300w | single ref ≤ 1500w
✅ AI-SKILL.md first → then derive HUMAN-SKILL.md (irreversible)

## Auto Decisions

Encoding/line-end unspecified → infer from target platform
Trigger keywords unspecified → derive from goal
Constraints unspecified → AI fills + marks [AI-inferred]
Goal has "and/plus" with independent intents → ask user if split
Exact match in search → recommend, user confirms

## Pipeline

```
1.Collect → 2.Abstract → 3.Lock Goal ★user gate★
→ 4.Search Solutions → 5.Serve Goal (align/split/constraints)
→ 6.User Confirm → 7.Generate AI version → 8.Derive Human version
```

**Stage 3**: Converge loop — User→AI distill→User correct→AI re-distill→Confirm→Lock. One goal. User's words. Subtract don't add. Flag "and/plus".

**Stage 4**: Search before build. A:exact match→fetch→wrapper. B:no match→custom script→wrapper. C:partial→combine.

**Stage 5**: Alignment gate. Ambiguous→options. Conflicting→trade-offs. Missing→decision points. Any unresolved→halt.

**Stage 7 output**: AI-SKILL.md (trigger routes + constraints + auto decisions + deps) + references/{scene}.md (goal + flow + params + failures + cross-refs)

**Stage 8**: Derive HUMAN-SKILL.md (what/when/how + AI decisions + modules + troubleshoot + customize)

## Deps

references/forge-flow.md | design-principles.md | scene-split.md | solution-search.md
