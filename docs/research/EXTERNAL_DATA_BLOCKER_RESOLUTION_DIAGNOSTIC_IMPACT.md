# External Data Blocker Resolution — Diagnostic Impact

**Diagnostic only** — `strategy_evidence: false`

## Executive summary

Full-window FRED ingest **succeeded** with `FRED_API_KEY` configured locally. All 7 registry series fetched. Normalized CSV: 2,148 daily rows. H4 alignment: 100% coverage. `cross_asset_missing` **eliminated** (2,142 → 0).

## Comparison vs prior sprint (blocked run)

| metric | blocked run (prior) | FRED key configured (this run) | delta |
|---|---|---:|---:|
| `cross_asset_missing` | 2,142 | **0** | **−2,142** |
| `cross_asset_status` | REAL_DATA_NORMALIZED | REAL_DATA_NORMALIZED | — |
| Normalized manifest status | BLOCKED_FULL_WINDOW | **FRED** | resolved |
| Normalized row count | 7 (fixture) | **2,148** | +2,141 |
| H4 feature coverage | ~68.6% | **100%** | +31.4 pp |
| H4 stale rate (core) | ~99.5% | **~0%** | resolved |

## Grade distribution (diagnostic only — not trade performance)

| grade | blocked run | FRED key run | delta |
|---|---:|---:|---:|
| B | 4,842 | 3,580 | −1,262 |
| A | 1,527 | 2,203 | +676 |
| REJECT | 394 | 394 | 0 |
| C | 153 | 739 | +586 |

Grade shifts reflect real cross-asset regime signals (e.g. `usd_headwind`, `risk_off_headwind`) replacing `cross_asset_missing` rejections. **Not trade performance.**

## Top reason codes (after FRED ingest)

| reason_code | count |
|---|---:|
| d1_aligned | 6,422 |
| grade_b | 3,580 |
| usd_headwind | 3,458 |
| grade_a | 2,203 |
| risk_off_headwind | 764 |
| grade_c | 739 |
| mixed_htf | 494 |
| cost_hostile | 394 |

`cross_asset_missing` **absent** from reason codes.

## Trade performance computed?

**No.** No win-rate, expectancy, profit factor, or confluence-bucket PnL.

## Stale-feature impact

H4 alignment stale rates ~0% on all core features. Prior ~99.5% stale rate was caused by 7-row fixture ending 2022-01 while H4 runs to 2026-05.

## Why `cross_asset_missing` decreased

1. Live FRED fetch succeeded for all required series
2. Full-window normalized CSV (2,148 rows) covers 2018 warmup through 2026-05
3. D+1 availability rule correctly aligns daily obs to H4 bars
4. Diagnostics no longer flag missing dxy/vix/us10y on any sampled context

## Explicit disclaimer

- No strategy approved
- No CAMPAIGN_018
- No confluence lift validation
- No profitability claims
- Diagnostic data-readiness only

## Outputs

- `research/confluence_diagnostics/confluence_diagnostic_summary_full_window_cross_asset.json`
- `research/confluence_diagnostics/confluence_reason_code_counts_full_window_cross_asset.csv`
