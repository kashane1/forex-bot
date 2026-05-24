---
status: complete
priority: p3
issue_id: 004
tags: [code-review, sprint:infra-exit-fidelity-001, docs, agent-native]
dependencies: []
---

# Add README mention of `--gap-fill-policy` flag + model-doc link

## Problem Statement

The agent-native-reviewer flagged that an agent operating without `--help` access (e.g., handed only the README + a config path) has no way to discover the new `--gap-fill-policy` flag. The model doc lives at `docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md` but is reachable only via the CLI's `--help` text — not indexed from the top-level README.

The same applies to `--fill-timing`, which has been in the repo since `infra-execution-fidelity-001`. So this is a chance to fix both at once.

## Findings

- **README.md** — does not mention `--fill-timing` or `--gap-fill-policy`. Only references `bot backtest --config ... --instrument`.
- **src/forex_bot/cli.py:408** — the `--gap-fill-policy` help text already points to `docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`.

## Proposed Solutions

### Option A (recommended): 3-line addition under README's "Run a backtest" section

Add a small "Exit-fidelity options" subsection listing both flags with one-line summaries + links to the respective model docs.

- **Pros**: agent-findable; matches the model doc's discoverability story; trivial.
- **Cons**: None.
- **Effort**: Small (5 min).
- **Risk**: None.

### Recommended Action: Option A

## Acceptance Criteria

- [ ] README.md mentions `--fill-timing` with link to `docs/research/FILL_TIMING_MODEL.md`
- [ ] README.md mentions `--gap-fill-policy` with link to `docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`
- [ ] Both bullets fit in ≤ 5 lines total

## Work Log

- 2026-05-24: created from agent-native-reviewer item 7.
- 2026-05-24: **resolved**. Added "Exit fidelity" bullet to README parallel to existing "Execution fidelity" bullet (both flags now mentioned with model-doc links). Added "Infrastructure exit-fidelity sprint" links subsection.
