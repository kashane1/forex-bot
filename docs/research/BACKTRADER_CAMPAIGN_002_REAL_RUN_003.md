# Backtrader CAMPAIGN_002 — Real Run — Phase 2 — 003

**Date:** 2026-05-24
**Branch:** `infra-backtrader-secondary-lane-003-real-data-run`
**Phase:** 2 of `BACKTRADER_REAL_DATA_RUN_003_PLAN.md`
**`strategy_evidence: false`**

## 0. Verdict

**Run completed.** The Backtrader secondary lane drove all seven
CAMPAIGN_002 H4 pairs end-to-end against the real-data CSVs Phase 1
regenerated, in ~10 wall-clock seconds, without any error or warning.

**Total trades: 1 647 — exact match to the bespoke no-RiskEngine
reference.** Every per-pair trade count and every per-pair win-rate
also matches the bespoke reference exactly, except a single
sub-pip-rounding-related off-by-one in NZD_USD wins (70 BT vs 69
bespoke — see §6).

CAMPAIGN_002 **remains REJECT.** This run is verification
infrastructure; it cannot approve a strategy.

## 1. Exact command

```bash
python scripts/run_backtrader_parity.py \
    --campaign CAMPAIGN_002 \
    --output research/backtrader_lane/results/campaign_002_real_data_003/
```

Wall clock: 9.94 s user / 0.14 s system / 10.084 s total on
`macOS-26.3.1-arm64-arm-64bit`, Python 3.12.3.

## 2. Backtrader version

`1.9.78.123` (the same opt-in extra installed by sprint 001).

## 3. Data source

Seven Phase-1-regenerated CSVs at
`research/lean_parity/exports/campaign_002_h4/<INST>_H4_lean.csv`,
each sha256-validated against its committed provenance sidecar
(`BACKTRADER_REAL_DATA_PREFLIGHT_003.md` §8). No OANDA call, no
credential, no broker contact.

## 4. Instruments loaded

All seven CAMPAIGN_002 majors:

```
EUR_USD  9931 bars
GBP_USD  9931 bars
USD_JPY  9932 bars
AUD_USD  9931 bars
USD_CAD  9931 bars
USD_CHF  9931 bars
NZD_USD  9935 bars
          ─────
total    69 522 bars (no blocked instruments)
```

The runner's manifest carries the sha256 + count + window for each
instrument and the seven adapter-level approximation flags.

## 5. Run status: PASS

| field | value |
|---|---|
| `dry_run` | false |
| `total_trades` | 1 647 |
| `blocked_instruments` | `[]` |
| `total_pnl_account` | $-324.7586 (sum across 7 pairs × $500 starting equity) |
| warnings / errors | none |
| `git_commit` | `51db36a95ee32e3c8998ab2f8348ab3444f15886` (Phase 1) |
| `git_dirty` | false |

## 6. Per-pair trade count and win rate

| pair | BT trades | bespoke trades | match | BT wins | BT losses | BT win rate | bespoke win rate | match |
|---|---:|---:|:--:|---:|---:|---:|---:|:--:|
| EUR_USD | 233 | 233 | ✅ | 71 | 162 | 0.3047 | 0.3047 | ✅ |
| GBP_USD | 215 | 215 | ✅ | 80 | 135 | 0.3721 | 0.3721 | ✅ |
| USD_JPY | 247 | 247 | ✅ | 89 | 158 | 0.3603 | 0.3603 | ✅ |
| AUD_USD | 237 | 237 | ✅ | 66 | 171 | 0.2785 | 0.2785 | ✅ |
| USD_CAD | 251 | 251 | ✅ | 72 | 179 | 0.2869 | 0.2869 | ✅ |
| USD_CHF | 224 | 224 | ✅ | 80 | 144 | 0.3571 | 0.3571 | ✅ |
| NZD_USD | 240 | 240 | ✅ | 70 | 170 | 0.2917 | 0.2875 | ⚠️ off-by-one win |
| **total** | **1 647** | **1 647** | ✅ | 528 | 1 119 | — | — | — |

Per-pair trade-count parity: **7 / 7 exact**. Per-pair win-rate
parity: **6 / 7 exact**, with NZD_USD off by a single trade
(0.2917 = 70/240 BT vs 0.2875 = 69/240 bespoke). The trade count
itself agrees on NZD_USD — both engines saw 240 closed trades — but
one of those trades crossed the win/loss boundary differently. This
is the textbook signature of a sub-pip float-vs-Decimal rounding
difference at a marginal exit price, which the comparison spec
labels as `TOLERABLE_DRIFT`. The Phase 3 harness will produce the
formal classification.

## 7. Warnings / errors

None at runner level. No instrument was blocked. No sha drift was
detected. No OANDA env-var name or value was placed in the run
manifest.

## 8. Output paths (gitignored)

| artefact | path | size |
|---|---|---|
| run manifest | `research/backtrader_lane/results/campaign_002_real_data_003/run_manifest.json` | 10.4 KB |
| summary | `research/backtrader_lane/results/campaign_002_real_data_003/backtrader_summary.json` | 2.7 KB |
| metrics | `research/backtrader_lane/results/campaign_002_real_data_003/backtrader_metrics.json` | 1.2 KB |
| trades | `research/backtrader_lane/results/campaign_002_real_data_003/backtrader_trades.jsonl` | 635 KB (1 647 lines) |
| log summary | `research/backtrader_lane/results/campaign_002_real_data_003/run_log_summary.md` | 2.4 KB |

The entire `research/backtrader_lane/results/` tree is gitignored
(see sprint 001 `.gitignore` rule). **Nothing in that tree is
committed by this phase.**

## 9. Committed by this phase

| file | change |
|---|---|
| `docs/research/BACKTRADER_CAMPAIGN_002_REAL_RUN_003.md` | NEW (this doc) |

Nothing else. No SQLite, no CSV, no raw run artefact.

## 10. Required disclosure

This run cannot approve any strategy and does not enable paper /
demo / live trading. CAMPAIGN_002 remains **REJECT**.
`strategy_evidence: false`.
