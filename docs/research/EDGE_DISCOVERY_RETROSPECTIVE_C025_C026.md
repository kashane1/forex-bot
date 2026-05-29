# EDGE_DISCOVERY_RETROSPECTIVE_C025_C026

**Branch:** `research-edge-discovery-null-benchmark-lab-001`
**Date:** 2026-05-28
**Kind:** retrospective diagnostic. Artifact-first, DB-optional. Applies the
edge-discovery lab to the *already-rejected* C025 and C026 evidence to prove the
lab works and to extract process lessons.

> **No verdict changes.** C025 stays `REJECT_MATRIX_NO_TRAIN_CANDIDATE /
> TEST_LOCKBOX_CLOSED / NOT_APPROVED`; C026 stays
> `REJECT_TIMEFRAME_LADDER_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED /
> NOT_APPROVED`. Nothing approved; no test lockbox opened. C011 remains the
> null benchmark, not a strategy.

Reproduce: `python scripts/run_edge_discovery_c025_c026_retrospective.py`
Artifacts: `research/edge_discovery/retrospectives/`.

---

## What the lab confirms

Run against the committed C025/C026 candidate-metrics + spread/ATR diagnostics,
with the C011 deduped null as the reference (aggregate expectancy −0.0029 R;
per-fold expectancy std 0.0479 used as the noise scale):

### Cost feasibility (would have warned at step 1)

| TF | spread/ATR | flag |
|---|---:|---|
| C025 M5 | ~0.45–0.50 | **COST_HOSTILE** (16/16 candidates) |
| C026 M3 | 0.637 | **COST_HOSTILE / TIMEFRAME_TOO_FAST** |
| C026 M15 | 0.218 | COST_FEASIBLE |
| C026 M30 | 0.144 | COST_FEASIBLE |

C025's M5 target is uniformly cost-hostile — the campaign's central finding,
obtainable from a one-shot cost-feasibility check before any matrix run. C026's
M3 rung is cost-hostile too, but **M15/M30 pass cost feasibility** — so cost
alone does *not* explain C026's rejection.

### Matrix sanity / matched-to-null (the deeper lesson)

| campaign | best expectancy_r | best − C011 null | prob(best ≤ best-of-N noise) | flags |
|---|---:|---:|---:|---|
| C025 | −0.0767 | −0.0738 | 1.000 | INCONCLUSIVE · LIKELY_SELECTION_NOISE |
| C026 | −0.0083 | −0.0054 | 1.000 | INCONCLUSIVE · LIKELY_SELECTION_NOISE · FRAGILE_SINGLE_PAIR_RESULT |

For **both** campaigns the best candidate is **below the C011 null** (negative
best-vs-null), so the matrix is `INCONCLUSIVE` and the best is fully consistent
with best-of-N selection noise (`prob_best_le_null_max = 1.000`). C026's best
additionally **flips sign under pair-holdout** (`FRAGILE_SINGLE_PAIR_RESULT`,
USD_JPY-dominant) — what little it has is a single-pair artifact, not a
portfolio edge. This is the lab's mechanical statement of C026's prose verdict:
"removing cost reveals a coin-flip, not a hidden edge."

## Which diagnostics would have warned us earlier

1. **Cost feasibility** → C025 dead at step 1 (M5 ≈ 0.45 hostile). C026's M3
   rung dead at step 1. **A campaign would not have been built for C025 at all.**
2. **Matrix sanity vs the C011 null** → C026's M15/M30 (cost-feasible) still
   below null and selection-noise-consistent → no campaign earned. The "cheaper
   execution is necessary but not sufficient" lesson is produced mechanically.
3. **Pair-holdout fragility** → C026's least-bad candidate is single-pair
   fragile, which the gates treat as a block.

Net: the full C025 and C026 campaigns were avoidable. Cost-feasibility +
matrix-sanity-vs-matched-null, run on screening data in minutes, reach the same
"no" the two campaigns reached in days.

## Which artifacts were compatible

Runnable from committed C025/C026 artifacts:
- `train_matrix_metrics.csv` → **matrix sanity** ✓
- `train_matrix_pair_metrics.csv` → **pair-holdout fragility** ✓
- `train_matrix_spread_atr_diagnostics.json` (+ `avg_spread_atr_ratio`) →
  **cost feasibility** ✓

## Retrospective compatibility gaps

C025/C026 persisted only **rolled-up candidate metrics** — the per-`Trade`
objects existed only in memory. So these diagnostics **could not run** and are
recorded as skipped (never fabricated) in
`research/edge_discovery/retrospectives/retrospective_compatibility_gaps.json`:

| diagnostic | required input | skip reason |
|---|---|---|
| matched-null benchmark | per-trade/signal ledger + frames | `SKIPPED_TRADE_LEDGER_UNAVAILABLE` |
| forward-return information | signal ledger + frames | `SKIPPED_SIGNAL_LEDGER_UNAVAILABLE` |
| entry/exit decomposition | per-trade ledger (exit_reason, r_multiple) | `SKIPPED_TRADE_LEDGER_UNAVAILABLE` |
| filter ablation | per-signal funnel (pass columns + value) | `SKIPPED_SIGNAL_LEDGER_UNAVAILABLE` |

(Raw OHLC also lives only in a Postgres research DB / gitignored sqlite in the
primary checkout, absent from this worktree — consistent with the local-only
policy. We did not copy DB files, fetch broker data, or use credentials.)

## How future campaigns should emit better ledgers

So the lab can re-screen a campaign end-to-end, future campaigns must emit a
**signal ledger**, a **trade ledger** (the canonical
`fold_NN_<PAIR>_trades.csv` schema), a **filter-stage / funnel ledger**,
**pair/side/session metadata**, **hold-duration metadata**, **spread/cost
fields**, **split-window metadata**, and the **candidate registry + matrix
result table**. The binding list is
[`FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`](FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md).

## No approval, no verdict change

This retrospective is diagnostic only. It approves nothing, adds nothing to
`configs/approved_strategies.yaml`, opens no test lockbox, and leaves C011 (null
benchmark) and C025/C026 (REJECT) exactly as they were.
