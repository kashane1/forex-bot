---
status: complete
priority: p3
issue_id: 005
tags: [code-review, sprint:infra-exit-fidelity-001, docs, agent-native]
dependencies: []
---

# Add "when to use which" decision table to model doc § Recommendation

## Problem Statement

The agent-native-reviewer noted that the model doc's § 5 "Recommendation" has prose guidance but no one-line decision table. An agent making a policy choice has to read several paragraphs to triangulate. A 4-row decision table at the top of § 5 would turn prose into agent-actionable rules.

## Findings

- **docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md** § 5 Recommendation — currently 5 bulleted recommendations covering different goals (canonical reference, measurement, parity, snapshot regeneration).

## Proposed Solutions

### Option A (recommended): add a 4-row decision table

Insert at the top of § 5:

```markdown
### When to use which policy

| Goal | gap_fill_policy |
|---|---|
| Reproduce a CAMPAIGN_001–009 verdict byte-for-byte | `none` |
| Measure how often gap-through fills would change a verdict | `gap_through` |
| Compare against Lean parity (today) | `none` (baselines were captured here) |
| New D1AGG research from scratch | `gap_through` (daily gaps are largest) |
```

- **Pros**: one-line decision; agent-actionable; complements the existing prose.
- **Cons**: None.
- **Effort**: Small (5 min).
- **Risk**: None.

### Recommended Action: Option A

## Acceptance Criteria

- [ ] `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md` § 5 starts with the 4-row decision table
- [ ] Existing 5 prose recommendations preserved (table is additive, not replacing)

## Work Log

- 2026-05-24: created from agent-native-reviewer recommendation #2.
- 2026-05-24: **resolved**. Added 4-row "When to use which policy" decision table at the top of § 5 in `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`. Existing 5 prose bullets preserved under new "Detailed guidance" subheading.
