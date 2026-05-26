# Backtrader CAMPAIGN_015 Deduped Comparison

**Branch:** `infra-canonical-candle-dedup-and-campaign015-rerun-001`
**Date:** 2026-05-26
**Classification:** **`TOLERABLE_DRIFT`**

> Prior comparisons using contaminated bespoke rehydrate are **SUPERSEDED
> BY DEDUP RERUN**.

## Run configuration

| setting | value |
|---|---|
| BT run mode | `fold_windows` |
| strict_test_window | **true** (trades before test_start excluded) |
| risk_engine_parity | true |
| entry_bar_stop_policy | `bespoke_current_no_entry_bar_stop` |
| data | deduped Lean CSV exports |
| bespoke | deduped SQLite via canonical `CandleRepo.list` |

## Trade counts

| lane | total trades |
|---|---:|
| Backtrader | 288 |
| Bespoke deduped | 375 |
| delta | +87 (+30.2%) |

## Prior vs current

| comparison | prior (contaminated bespoke) | deduped |
|---|---|---|
| classification | `TIMESTAMP_MISMATCH` / `DATA_MISMATCH` | **`TOLERABLE_DRIFT`** |
| fold 1 × AUD_USD | bespoke 2 vs BT 13 | bespoke 13 vs BT 10 |

Dedupe removed the dominant CSV/SQLite signal mismatch. Residual drift
(≈23% aggregate) likely reflects fill-timing / RiskEngine / NZD_USD
sparse-cell differences — not duplicate-candle corruption.

## fold 1 × AUD_USD (spot check)

| lane | trades |
|---|---:|
| BT strict | 10 |
| Bespoke deduped | 13 |

Parity improved materially vs the contaminated 2 vs 13 gap.

## Artifacts

- `research/campaign_015/diagnostics/backtrader_fold_window_deduped/`
- `research/campaign_015/diagnostics/backtrader_fold_window_deduped/fold_window_comparison.json`

## Approval status

Diagnostic only. `configs/approved_strategies.yaml` remains `approved: []`.
