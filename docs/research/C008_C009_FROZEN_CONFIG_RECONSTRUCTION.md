# C008/C009 Frozen Config Reconstruction

**Date:** 2026-05-26  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`  
**Artifact:** [`research/deduped_c008_c009_rerun/frozen_config_reconstruction.json`](../../research/deduped_c008_c009_rerun/frozen_config_reconstruction.json)

> **Forensic only** — `strategy_evidence: false`. Reconstruction status: **COMPLETE**. No silent parameter inference.

---

## Reconstruction status

| check | result |
|---|---|
| C008 config YAML matches precommit | yes |
| C009 config YAML matches precommit | yes |
| Strategy code paths identified | yes |
| Split windows documented | yes |
| Test lockbox authorized | **no** |
| Uncertainty blocking replay | **none** |

---

## CAMPAIGN_008 — frozen rules

| field | value |
|---|---|
| version | `mean_reversion 0.1.0-c008` |
| config | `configs/campaign_008_range_mean_reversion.yaml` |
| midline_exit | **false** (absent → default) |
| hard stop | 1.5 × ATR-14 |
| time stop | 40 bars |
| universe | 6 majors H4 |
| data | `data/campaign_002.sqlite3`, oanda-practice |

**Authorized forensic windows:** train + validation (base cost); full window for cost-stress only (base / stress_15x / stress_2x). **Test lockbox not authorized.**

**Original failed gate:** train expectancy ≥ 0 → observed **−0.017 R**.

---

## CAMPAIGN_009 — frozen rules

| field | value |
|---|---|
| version | `mean_reversion 0.2.0-c009` |
| config | `configs/campaign_009_mean_reversion.yaml` |
| midline_exit | **true** (only change vs C008) |
| hard stop | 1.5 × ATR-14 |
| midline target | rolling mean over 20 bars |
| time stop | 40 bars backstop |
| all other parameters | identical to C008 |

**Authorized forensic windows:** train + validation under all three cost regimes. **Test lockbox not authorized.**

**Original failed gate:** train expectancy ≥ 0 → observed **−0.062 R**.

---

## Split windows (both campaigns)

| split | window | forensic replay |
|---|---|---|
| train | 2020-01-01 → 2022-12-31 | yes |
| validation | 2023-01-01 → 2024-12-31 | yes |
| test_untouched | 2025-01-01 → 2026-05-20 | **no** |
| full | 2020-01-01 → 2026-05-20 | C008 cost-stress only |

---

## Dedupe mechanism

Same as C011–C017 dedup-safe campaigns:

- `CandleRepo.list()` applies `dedupe_candles()` at load boundary
- Policy: `keep_last` on `(instrument, granularity, UTC time)`
- Preflight records duplicate rows detected/dropped

Original C008/C009 runs used pre-fix loading → **LIKELY_CONTAMINATED**.

---

## Original artifact references

| campaign | index | report |
|---|---|---|
| C008 | `backtests/campaign_008_range_mean_reversion/runs/_index.json` | `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md` |
| C009 | `backtests/campaign_009_mean_reversion/runs/_index.json` | `backtests/CAMPAIGN_009_MEAN_REVERSION_REPORT.md` |

Trade CSVs exist locally (gitignored) under original run trees.

---

## Uncertainty

None identified that blocks exact frozen replay. Config YAML, precommits, and strategy module are aligned.
