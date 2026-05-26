# Backtrader Fold-Window vs Bespoke Rehydrate Comparison — CAMPAIGN_015

> **SUPERSEDED / STALE DUE TO DUPLICATE-CANDLE CONTAMINATION** — see
> [`BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md`](BACKTRADER_CAMPAIGN_015_DEDUPED_COMPARISON.md).

**Sprint:** [Window Alignment 001](BACKTRADER_CAMPAIGN_015_WINDOW_ALIGNMENT_001_PLAN.md)
**Branch:** `infra-backtrader-campaign-015-window-alignment-001`
**Date:** 2026-05-26
**Classification:** **`SIGNAL_RULE_MISMATCH`** (dominant, post-alignment)
**Prior classification:** **`TIMESTAMP_MISMATCH`** (575 full-window BT vs 164 bespoke)

> Diagnostic-only. Does **not** approve any strategy.
> `configs/approved_strategies.yaml` remains `approved: []`.

## 1 · What ran

| lane | path | mode |
|---|---|---|
| Backtrader (this sprint) | `research/campaign_015/diagnostics/backtrader_fold_window/` | 8 fold test windows × 7 pairs, equity reset per cell |
| Bespoke reference | `research/campaign_015/diagnostics/walk_forward_rehydrate/` | rehydrated walk-forward base-cost trades |
| Prior Backtrader | `research/campaign_015/diagnostics/backtrader_lane/` | full CSV ~2020–2026 (575 trades) |

Fold plan source of truth:
`research/campaign_015/diagnostics/walk_forward_rehydrate/walk_forward/plan.json`

## 2 · Headline trade counts

| dimension | Backtrader fold-window | Bespoke rehydrate | Δ |
|---|---:|---:|---:|
| **total trades** | **532** | **164** | **+368 (+224%)** |
| prior full-window BT | 575 | 164 | +411 (+250%) |

**Window-alignment effect:** full-window excess shrank by **43 trades** (575→532).
The dominant gap vs bespoke remains **~3.2×** per fold on average.

## 3 · Per-fold comparison

| fold | BT | bespoke | Δ | BT/bespoke |
|---:|---:|---:|---:|---:|
| 0 | 57 | 18 | +39 | 3.17× |
| 1 | 65 | 26 | +39 | 2.50× |
| 2 | 70 | 26 | +44 | 2.69× |
| 3 | 69 | 28 | +41 | 2.46× |
| 4 | 66 | 24 | +42 | 2.75× |
| 5 | 61 | 14 | +47 | 4.36× |
| 6 | 65 | 14 | +51 | 4.64× |
| 7 | 79 | 14 | +65 | 5.64× |

## 4 · Per-pair comparison

| pair | BT | bespoke | Δ |
|---|---:|---:|---:|
| AUD_USD | 101 | 24 | +77 |
| EUR_USD | 79 | 27 | +52 |
| GBP_USD | 95 | 41 | +54 |
| NZD_USD | 53 | 5 | +48 |
| USD_CAD | 81 | 23 | +58 |
| USD_CHF | 70 | 27 | +43 |
| USD_JPY | 53 | 17 | +36 |

## 5 · Side distribution

| side | BT | bespoke |
|---|---:|---:|
| long | 276 | 85 |
| short | 256 | 79 |

Both sides inflated ~3.2× — not a directional bias artifact.

## 6 · BT exit reasons (fold-window run)

| exit_reason | count |
|---|---:|
| stop | 269 |
| time | 196 |
| stop_same_bar | 66 |
| eod | 1 |

## 7 · Classification rationale

### TIMESTAMP_MISMATCH — **resolved**

Both lanes now process the same 8 test windows with the same 90-day warmup
margin and per-fold × per-pair isolation. The prior 575-trade full-window
run is no longer the comparison baseline.

### SIGNAL_RULE_MISMATCH — **dominant residual**

Trade-count delta exceeds the ±10% harness band on every fold and pair.
The ~3.2× uniform inflation across folds and sides is consistent with the
**bespoke RiskEngine rejecting signals that the BT adapter accepts** (the
provenance-repair comparison doc hypothesized this; fold alignment did not
collapse the ratio).

Other published BT approximations (`FILL_TIMING_APPROXIMATION`,
`MANUAL_SIZING_RISK_FRACTION`) may contribute marginally but cannot
explain a uniform ~3× count inflation.

### Not observed

- `DATA_MISMATCH` — same CSV/provenance bundle drives both lanes
- `SIZING_OR_PNL_MISMATCH` — not assessed at trade-list level this sprint
- `BLOCKED` — both sides produced runnable trade lists

## 8 · Machine-readable outputs

- [`fold_window_comparison.json`](../../research/campaign_015/diagnostics/backtrader_fold_window/fold_window_comparison.json)
- [`fold_window_comparison.md`](../../research/campaign_015/diagnostics/backtrader_fold_window/fold_window_comparison.md)
- [`backtrader_summary.json`](../../research/campaign_015/diagnostics/backtrader_fold_window/backtrader_summary.json)

## 9 · Safety invariants

Unchanged. No strategy approval. No registry mutation. No live paths touched.
