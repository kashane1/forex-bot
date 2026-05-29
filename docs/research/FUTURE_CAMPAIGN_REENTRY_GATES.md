# FUTURE_CAMPAIGN_REENTRY_GATES

**Status:** process doc (binding). Strict gates an idea must pass *before* a
new strategy campaign is created. Diagnostic/governance only — approves
nothing, opens no test lockbox, creates no campaign.

> Built on the edge-discovery lab (`research/edge_discovery/`). See
> [`EDGE_DISCOVERY_PROTOCOL.md`](EDGE_DISCOVERY_PROTOCOL.md) for the why, and
> [`PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md`](PRE_CAMPAIGN_EDGE_DISCOVERY_CHECKLIST.md)
> for the per-idea checklist.

---

These gates are intentionally hard. They exist because ~26 campaigns mostly
re-discovered, expensively, that an idea had no edge over a fair null. Each gate
references a lab flag so the decision is mechanical, not vibes.

## G1 — Signal beats a *matched* null after estimated cost

The idea's forward-return expectancy, computed at its real entries and signed
by its real side, must exceed its **matched null** (same pair/side/session/
weekday/hold structure), measured **post-cost**. Use
`matched_nulls.matched_null_baseline(..., apply_cost_overlay_fn=apply_cost_overlay)`.

- PASS: `BEATS_MATCHED_NULL` (strategy mean above null p95), or at minimum
  `ABOVE_MATCHED_NULL` with a positive effect size on the mode that matches the
  idea's claimed structure.
- BLOCK: `WITHIN_MATCHED_NULL` / `BELOW_MATCHED_NULL`, or `MATCHED_NULL_SPARSE`
  with no denser data available.

Beating a *random timestamp* null is necessary but not sufficient — random
timestamps must be beaten *on the same pair/timeframe/split*, and the structure
matched null must also be beaten.

## G2 — Candidate beats a matched null, not just a generic null

Passing G1 on `timestamp_random_same_pair` alone is insufficient. The idea must
also clear the modes that encode its claimed source of edge (e.g. if the thesis
is directional, it must beat `side_shuffled`; if session-timed, it must beat
`session_matched_random`). If the edge disappears once the matched structure is
reproduced, the "edge" was structure, not skill → BLOCK.

## G3 — Cost feasibility passes for the target timeframe/session

`cost_feasibility` must return `COST_FEASIBLE` for the target cell. Any
`COST_HOSTILE` / `TIMEFRAME_TOO_FAST` / `SESSION_HOSTILE` on the intended
trading cell is an automatic BLOCK (the C025/C026 trap). If only a slower
timeframe or a specific session is feasible, the precommit must trade *there*.

## G4 — Each filter improves edge, not only sample size

Run `filter_ablation`. Every filter retained in the precommit must be
`FILTER_ADDS_EDGE` (noise-aware: marginal expectancy gain exceeds the subset
mean's standard error). A `FILTER_ONLY_REDUCES_SAMPLE` or `FILTER_HURTS_EDGE`
filter must be dropped or justified in writing; a `FILTER_TOO_SPARSE` filter
needs more data before it can be judged.

## G5 — Not a single-pair artifact (unless precommitted single-pair research)

If the idea is portfolio-level, `multiple_comparison` pair-holdout must not
show `FRAGILE_SINGLE_PAIR_RESULT` (the aggregate must not flip sign when one
pair is dropped). A single-pair result is allowed only when the sprint is
**precommitted** as single-pair research up front.

## G6 — Matrix results survive a multiple-comparison sanity check

If the idea was found by screening many variants, `matrix_sanity` must NOT
return `LIKELY_SELECTION_NOISE` and NOT `TOO_MANY_VARIANTS_FOR_EVIDENCE`; the
best must clear the null reference and the best-of-N noise band
(`ROBUST_MATRIX_SIGNAL`). `FRAGILE_TIME_BLOCK_RESULT` is a BLOCK.

## G7 — Validation cannot be used to choose parameters

Parameters are chosen on **train only**. Validation is a confirmation, never a
selection set. If a campaign uses validation to pick among variants, the result
is not approvable. (This mirrors the C025/C026 "no validation selection" rule.)

## G8 — No test lockbox until train/validation and parity pass

The test lockbox (2025-01-01 → 2026-05-20) stays sealed until the campaign has
(a) a precommitted champion selected on train, (b) a validation confirmation,
and (c) Backtrader parity at the approval-bound fill timing (`next_bar_open`).
Lab diagnostics never touch the lockbox.

## G9 — Sufficient expected trade count and approval-bound fill timing

The idea must project enough trades to reach the campaign's gate minimums, and
the precommit must declare `fill_timing: next_bar_open` (the only
approval-eligible fill model; `signal_bar_close` is diagnostic/upper-bound and
`promotion_eligible: false`).

---

## Gate summary

| gate | check | lab handle | block flag |
|---|---|---|---|
| G1 | beats matched null post-cost | `matched_null_baseline` | `WITHIN/BELOW_MATCHED_NULL` |
| G2 | beats structure-matched, not just generic | matched-null modes | edge vanishes when matched |
| G3 | cost feasible on target | `cost_feasibility` | `COST_HOSTILE`/`TIMEFRAME_TOO_FAST` |
| G4 | filters add edge | `filter_ablation` | `FILTER_ONLY_REDUCES_SAMPLE` |
| G5 | not single-pair (unless precommitted) | `matrix_sanity` pair-holdout | `FRAGILE_SINGLE_PAIR_RESULT` |
| G6 | matrix survives selection-noise | `matrix_sanity` | `LIKELY_SELECTION_NOISE` |
| G7 | validation ≠ parameter selection | campaign discipline | validation-selected champion |
| G8 | lockbox sealed pre-parity | campaign discipline | lockbox opened early |
| G9 | trade count + next_bar_open | precommit | too few trades / non-approvable fill |

All gates are necessary. Passing them earns a **campaign**, not an approval —
approval remains a separate, reviewed human action on
`configs/approved_strategies.yaml`.
