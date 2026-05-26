# External Data Blocker Resolution — Diagnostic Impact

**Diagnostic only** — `strategy_evidence: false`

## Executive summary

Full-window FRED ingest **did not execute** — `FRED_API_KEY` absent, no local CSVs. Pipeline infrastructure is ready; data blocker **unresolved**.

## Comparison vs prior sprint

| metric | after_real_cross_asset (prior) | full_window (this sprint) | delta |
|---|---|---:|---:|
| `cross_asset_missing` | 2,142 | **2,142** | **0** |
| `cross_asset_status` | REAL_DATA_NORMALIZED | REAL_DATA_NORMALIZED | — |
| Normalized manifest status | FIXTURE_ONLY | **BLOCKED_FULL_WINDOW** | auth blocked |
| Normalized row count | 7 (fixture) | 7 (retained) | 0 |
| H4 observation target | partial | 2018-01-01 → 2026-05-24 | window defined |

## Grade distribution (unchanged — data unchanged)

| grade | count |
|---|---:|
| B | 4,842 |
| A | 1,527 |
| REJECT | 394 |
| C | 153 |

## Trade performance computed?

**No.** No win-rate, expectancy, profit factor, or confluence-bucket PnL.

## Stale-feature impact

H4 alignment stale rates ~99.5% on core features because fixture data ends 2022-01 while H4 runs to 2026-05. Forward-filled stale values dominate post-fixture period.

## Why `cross_asset_missing` did not decrease

1. Live FRED fetch blocked
2. No operator CSV drop
3. Retained 7-row fixture CSV does not cover 2020–2021 H4 contexts
4. Diagnostics correctly flag missing dxy/vix/us10y on early bars

## Explicit disclaimer

- No strategy approved
- No CAMPAIGN_018
- No confluence lift validation
- No profitability claims
- Diagnostic data-readiness only

## Recommended next step

Configure `FRED_API_KEY` or drop full-window CSVs per [`EXTERNAL_FEATURE_LOCAL_CSV_TEMPLATE.md`](EXTERNAL_FEATURE_LOCAL_CSV_TEMPLATE.md), then re-run:

```bash
python scripts/run_external_data_full_window_pipeline.py
python scripts/align_cross_asset_features_to_h4.py
python scripts/run_mtf_confluence_diagnostics.py \
  --skip-doc \
  --summary-name confluence_diagnostic_summary_full_window_cross_asset.json \
  --counts-name confluence_reason_code_counts_full_window_cross_asset.csv
```

## Outputs

- `research/confluence_diagnostics/confluence_diagnostic_summary_full_window_cross_asset.json`
- `research/confluence_diagnostics/confluence_reason_code_counts_full_window_cross_asset.csv`
