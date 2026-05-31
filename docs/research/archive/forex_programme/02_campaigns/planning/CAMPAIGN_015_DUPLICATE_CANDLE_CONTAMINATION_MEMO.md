# CAMPAIGN_015 Duplicate-Candle Contamination Memo

**Branch:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`
**Date:** 2026-05-26
**Sprint:** data-correctness + evidence rerun (NOT strategy approval)

> **No strategy is approved.** `configs/approved_strategies.yaml` remains
> `approved: []`. Paper / demo / live remain blocked.

## What was found

The CAMPAIGN_015 cell parity drilldown (`infra-backtrader-campaign-015-cell-parity-drilldown-001`) proved a **CSV vs SQLite data mismatch** on fold 1 × AUD_USD:

| lane | accepted trades |
|---|---:|
| Bespoke rehydrate (SQLite) | 2 |
| Backtrader RiskEngine/fill parity (deduped CSV) | 13 |

**Root cause:** `CSV_SQLITE_DATA_MISMATCH`

- SQLite `campaign_002.sqlite3` stores **two rows per H4 bar** for the same instrument when an earlier fetch used a local-offset ISO timestamp and a later refresh stored the same bar at UTC. Raw `time` strings differ, so SQL `GROUP BY time` shows zero duplicates, but UTC-normalised timestamps collide.
- Example fold-1 AUD_USD load: **2328 rows**, **1162 UTC-duplicate timestamps** (~2× per H4 bar).
- Backtrader reads **deduped** Lean CSV exports (`export_lean_parity_data.py`, `keep='last'` policy).
- Bespoke reads **undeduplicated** SQLite via `CandleRepo.list` → `CandleFrame.from_candles`.
- Duplicate bars corrupt ATR / ADX / range windows, suppressing bespoke signals that BT still fires.
- Isolated probe with `keep='last'` on deduped SQLite emitted the same long signal as BT at the first divergence bar (`2022-05-06T17:00:00+00:00`).

**Secondary issue:** BT fold-window parity used `strict_test_window=False`; 3/13 BT trades had `entry_time` before fold `test_start`. This is a counting/window issue, not the primary +8 inside-window gap.

## Artifacts superseded / stale

Until the deduped rerun completes, treat **all prior CAMPAIGN_015 bespoke evidence as evidence-contaminated**:

| artifact | status |
|---|---|
| `backtests/CAMPAIGN_015_failed_breakout_reversal/` walk-forward outputs | **STALE** |
| `docs/research/CAMPAIGN_015_POST_RUN_INTERPRETATION.md` | **STALE** |
| `docs/research/CAMPAIGN_015_NULL_AND_ANTI_OVERFIT_POST_RUN.md` | **STALE** |
| `docs/research/CAMPAIGN_015_CONCENTRATION_DIAGNOSTICS.md` | **STALE** |
| `docs/research/CAMPAIGN_015_GATE_FAILURE_AUTOPSY.md` | **STALE** |
| `docs/research/CAMPAIGN_015_POST_RUN_DIAGNOSTICS_001_SUMMARY.md` | **STALE** |
| Backtrader comparison docs using contaminated bespoke rehydrate | **STALE** |
| Prior `ROBUST_ABOVE_NULL` / `SPARSE_BUT_PROMISING` labels | **STALE** |

### Contaminated headline metrics (do not use for decisions)

| metric | contaminated value |
|---|---:|
| base aggregate exp_r | +0.2300 |
| 2x-cost aggregate exp_r | +0.1909 |
| total trades | 164 |
| fold pass count | 0 / 8 |
| anti-overfit label | `ROBUST_ABOVE_NULL` (diagnostic only, now stale) |

## Why old metrics cannot be used

1. **Input corruption:** indicator warm-up and signal generation ran on ~2× duplicated H4 bars.
2. **Lane asymmetry:** BT lane was already deduped; bespoke was not — parity comparisons were invalid.
3. **False precision:** aggregate expectancy, fold pass rates, null comparison, and concentration diagnostics all inherit the corrupted signal path.

## Dedupe policy to implement

At the **canonical `CandleRepo.list` load boundary**:

1. Normalise each candle `time` to UTC.
2. Deduplicate by `(instrument, granularity, utc_time)`.
3. **`keep='last'`** — last row in deterministic SQL `ORDER BY time ASC, rowid ASC` wins (matches CSV export policy).
4. Return monotonic UTC-sorted candles.
5. Report `duplicates_detected`, `duplicates_dropped`, `dedupe_policy=keep_last`.
6. **Do not mutate** the SQLite file in this sprint.

## Rerun scope

This sprint will:

1. Implement canonical dedupe (Phase 1).
2. Add campaign preflight duplicate reporting (Phase 2).
3. Rerun CAMPAIGN_015 bespoke to `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/`.
4. Rerun null / anti-overfit diagnostics on deduped inputs.
5. Rerun Backtrader fold-window comparison against deduped bespoke.
6. Mark prior docs **SUPERSEDED BY DEDUP RERUN**.

## Outcome uncertainty

The deduped rerun may **improve**, **worsen**, or **invalidate** the prior contaminated result. No approval path is opened by this sprint.

## References

- `docs/research/BACKTRADER_CAMPAIGN_015_CELL_PARITY_ROOT_CAUSE.md`
- `docs/research/BACKTRADER_CAMPAIGN_015_CELL_PARITY_FIX_DESIGN.md`
- `scripts/export_lean_parity_data.py` (CSV dedupe precedent)
