---
status: complete
priority: p2
issue_id: 001
tags: [code-review, sprint:infra-exit-fidelity-001, semantics, gap-fill]
dependencies: []
---

# Document and test favorable-TP gap-fill precedence over intra-bar adverse stop

## Problem Statement

The architecture-strategist review flagged that the new gap-fill resolver in `src/forex_bot/backtesting/engine.py:285-330` has a precedence semantics that's *correct but undocumented and untested*: on a long with `gap_fill_policy="gap_through"`, when the bar opens ABOVE the TP AND the bar's low later wicks below the stop, the resolver fires the favorable TP gap-fill at `bid_open` (closes the trade in profit). The default-mode (`"none"`) chain would instead exit at the stop (adverse) because `bid_low <= stop_price` is checked first.

This is a real behavior flip from a loss to a gain that turns on `gap_fill_policy`. It is **the correct modeling** — a TP limit order would have filled at the bar's open (1.10700) before price ever reached the stop later in the bar — but the model doc only hints at it tangentially, and no test asserts the semantics.

## Findings

- **engine.py:285-330** — gap-fill resolver. `stop_breached` is checked BEFORE `tp_breached`; only adverse-then-favorable is exercised. The favorable-side-with-adverse-intra-bar case lives entirely inside the `elif tp_breached` branch with no test exercising it.
- **docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md:78-86** — the gap-fill table lists the four cases but does not explicitly say "the favorable TP open overrides the intra-bar adverse stop range check because the TP would have filled first chronologically".
- **tests/unit/test_gap_fill.py** — `_make_gap_scenario` (line ~322) constructs `bid_l = exit_bid_open - gap`, which for tp scenarios lands AT-OR-ABOVE the TP (never below the stop). No 16-case matrix combination exercises "favorable open + adverse low".

## Proposed Solutions

### Option A (recommended): document + test the precedence inversion explicitly

Add 1 new test `test_long_tp_gap_overrides_intra_bar_adverse_stop` to `tests/unit/test_gap_fill.py`. Construct a bar where `bid_open > tp_price` AND `bid_low < stop_price`. Assert:
- `exit_reason == "target"`
- `exit_price == bid_open`
- `gap_fill is True`
- The same bar under `gap_fill_policy="none"` exits at `stop_price` with `exit_reason == "stop"`

Add a 3-line note to `docs/research/GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md` § "Opt-in gap-through fill" explaining that the gap-fill resolver models the bar-open as the chronologically-first event, so a favorable open closes the trade BEFORE the intra-bar adverse range can fire. This is correct order-modeling, not a precedence override.

- **Pros**: closes the semantics ambiguity at near-zero cost; future reviewers can grep for the test and find the documented behavior.
- **Cons**: 1 test + 1 doc paragraph.
- **Effort**: Small (15 min).
- **Risk**: None — observation-only.

### Option B: change the resolver to reject favorable-TP when intra-bar adverse stop also fires

Make the favorable-TP branch also check `bid_low > pre_trailing_stop_price` (long) before firing. This preserves the existing default-mode stop-precedence even in gap_through mode.

- **Pros**: aligns gap_through with default-mode precedence.
- **Cons**: incorrect order modeling — a limit order that filled at the open IS closed before any later intra-bar move. Would mis-classify a profitable trade as a stop-out.
- **Effort**: Small.
- **Risk**: Wrong modeling. Reject.

### Recommended Action: Option A

## Acceptance Criteria

- [ ] Add `test_long_tp_gap_overrides_intra_bar_adverse_stop` (and short mirror) to `tests/unit/test_gap_fill.py`
- [ ] Both tests pass under `gap_fill_policy="gap_through"` (favorable TP wins) and under `"none"` (stop wins)
- [ ] `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md` gains a paragraph explaining bar-open-as-first-event semantics
- [ ] `pytest tests/` stays at 790+ passed, 0 failed
- [ ] `ruff check src tests scripts` clean

## Work Log

- 2026-05-24: created during /workflows:review synthesis from architecture-strategist IMPORTANT finding.
- 2026-05-24: **resolved**. Added `test_long_tp_gap_overrides_intra_bar_adverse_stop` + short mirror to `tests/unit/test_gap_fill.py` (both pass under gap_through AND none). Added "Semantics: bar-open as the first event" subsection to `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md` § 2 with a comparison table. pytest 792 passed, ruff clean.
