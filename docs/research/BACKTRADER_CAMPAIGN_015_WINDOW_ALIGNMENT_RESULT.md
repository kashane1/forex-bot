# Backtrader CAMPAIGN_015 Window Alignment — Result

**Sprint:** [Window Alignment 001](BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_001_PLAN.md)
**Branch:** `infra-backtrader-campaign-015-window-alignment-001`
**Date:** 2026-05-26
**Recommended label:** **`BT_WINDOW_ALIGNED_DIVERGENCE_NEEDS_DEBUG`**

> Does **not** approve any strategy. CAMPAIGN_015 remains unapproved.

## Decision matrix

| # | question | answer |
|---|---|---|
| 1 | Did BT-on-fold-windows run? | **Yes** — 8 folds × 7 pairs, ~11s wall time |
| 2 | Same 8 test windows as bespoke? | **Yes** — rehydrate `plan.json`, 90-day warmup margin |
| 3 | Did trade-count gap shrink (575 vs 164)? | **Partially** — 575→**532** vs 164 (−43 trades, −7.5% of excess) |
| 4 | Classification improved from TIMESTAMP_MISMATCH? | **Yes** — TIMESTAMP_MISMATCH resolved; dominant label now **SIGNAL_RULE_MISMATCH** |
| 5 | New blocker? | BT adapter lacks bespoke **RiskEngine** signal rejection; ~3.2× uniform trade inflation persists after window alignment |
| 6 | CAMPAIGN_015 approval status altered? | **No** — remains unapproved, `approved: []` |
| 7 | Backtrader precondition satisfied? | **Partially** — window coverage aligned; rule-level parity not yet demonstrated |
| 8 | Recommended next move? | **Debug remaining BT divergence** (RiskEngine parity or rule-level diff trace on one fold×pair) before any H4 re-run or stop decision |

## Interpretation

Window alignment was necessary and successful: the comparison is no longer
invalidated by different time coverage. However, aligning windows alone
did not produce trade-count parity — the BT lane still fires ~3.2× more
often than bespoke across all folds and both sides.

The most probable cause is the absence of the bespoke **RiskEngine** in the
BT adapter loop (documented in the provenance-repair comparison). A
follow-on infra sprint should either wire read-only RiskEngine rejection
into the BT adapter or produce a bar-level diff on a single fold×pair cell
to isolate the first diverging signal.

Collecting more H4 data or re-running frozen CAMPAIGN_015 bespoke is **not**
the priority until rule-level divergence is understood — data coverage is
already sufficient for the 8-fold test windows.

Stopping CAMPAIGN_015 outright is **not** warranted by this sprint alone;
the candidate remains `SPARSE_BUT_PROMISING` on bespoke evidence with
fold-count gate failure unchanged.

## Label

**`BT_WINDOW_ALIGNED_DIVERGENCE_NEEDS_DEBUG`**

- Window alignment: done
- TIMESTAMP_MISMATCH: collapsed
- Residual: SIGNAL_RULE_MISMATCH (~532 vs 164)
- Approval: unchanged blocked
