# CAMPAIGN_011 — Deduped Run Verification

**Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001  
**Date:** 2026-05-26  
**Method:** Inspect local artifacts (no rerun, no OANDA)

## Verdict: **INSPECTED — SUITABLE FOR PROMOTION**

The local deduped walk-forward at
`backtests/CAMPAIGN_011_random_entry_anchor_deduped/` is complete,
consistent with frozen CAMPAIGN_011 settings, and suitable as the
source for the committed canonical rollup. Bulky per-fold trade CSVs
remain **local-only**.

## Run identity

| field | observed |
|---|---|
| `campaign_id` | CAMPAIGN_011 |
| `strategy_name` | `random_entry_anchor` |
| `strategy_version` | `0.1.0-c011` |
| `master_seed` | **20260523** (frozen) |
| `config_path` | `configs/campaign_011_random_entry_anchor.yaml` |
| `config_hash` | `6f2c04981a3f02f08bae65b73b09f873de6a42cb067b9462885c5ffd2c6a1206` |
| `data_source` | `oanda-practice` |
| `null_model` | true |
| `approval_path` | none (null model by design) |

## Data dedupe policy

| check | result |
|---|---|
| Dedupe fix in tree | commit `30b4654` — `CandleRepo.list` → `dedupe_candles`, policy `keep_last` |
| Runner uses `CandleRepo.list` | **yes** — `scripts/run_campaign_011.py` |
| Duplicate UTC H4 rows reaching backtest | **no** (load-boundary dedupe) |
| Dedupe probe (local SQLite, all fold windows × 7 pairs) | **42,710** duplicate rows dropped at load (cumulative across fold×pair `CandleRepo.list` calls; see rollup `dedupe_probe`) |

## Universe and walk-forward

| check | result |
|---|---|
| Pair universe | 7 majors (EUR/GBP/USD/JPY/AUD/CAD/CHF/NZD) |
| Fold count | **8** rolling frozen folds |
| Fold windows | 2021-12-21 → 2025-11-29 (matches CAMPAIGN_010/012–015 plan) |
| Parameter mode | frozen (no tuning) |

## Aggregate metrics (deduped local run)

| metric | deduped | pre-fix contaminated (superseded) |
|---|---:|---:|
| total_trades | **1,180** | 1,177 |
| aggregate expectancy R | **−0.0029** | −0.0024 |
| aggregate return % | **−0.677** | −0.53 |
| profit_factor | **0.894** | 0.91 |
| pairs_positive | **3 / 7** | 3 / 7 |
| fold_pass_rate | **0 / 8** | 0 / 8 |
| overall_verdict | **REJECT** | REJECT |

Per-fold expectancy R (deduped): mean **−0.0027**, std **0.0479**.

## Safety gates

| gate | result |
|---|---|
| Strategy approved | **no** |
| `approved_strategies.yaml` modified | **no** |
| Broker / OANDA calls | **none** (local SQLite read only) |
| CAMPAIGN_011 settings/seed changed | **no** |

## Artifacts present locally

| path | role | git |
|---|---|---|
| `walk_forward/fold_detail.json` | compact rollup source | **local-only** (promoted to `research/null_baselines/`) |
| `walk_forward/results.json` | WalkForwardResults | local-only |
| `walk_forward/results.md` | human summary | local-only |
| `folds/**/**_trades.csv` | bulky trade dumps | **never commit** |
| `folds/**/**_summary.json` | per-pair summaries | local-only |

## Promotion action

Run:

```bash
PYTHONPATH=src .venv/bin/python scripts/promote_campaign_011_deduped_null_baseline.py --probe-dedupe
```

Outputs committed in Phase 2 (not the local `backtests/..._deduped/folds/` tree).
