# C008/C009 Deduped Forensic Replay Results

**Date:** 2026-05-27  
**Branch:** `infra-deduped-c008-c009-rerun-forensic-only-001`  
**Command:** `python scripts/rerun_c008_c009_deduped_forensic.py replay`

> **Forensic only** — `strategy_evidence: false`. **No approval.** C008/C009 remain **REJECT**. Test lockbox **not opened**.

---

## Run configuration

| item | value |
|---|---|
| input DB | `data/campaign_002.sqlite3` |
| data source | `oanda-practice` |
| dedupe policy | `keep_last` |
| duplicates dropped (preflight) | **106,286** rows across train/val/full |
| C008 config | `configs/campaign_008_range_mean_reversion.yaml` |
| C009 config | `configs/campaign_009_mean_reversion.yaml` |
| C008 output | `backtests/CAMPAIGN_008_mean_reversion_deduped_forensic/` |
| C009 output | `backtests/CAMPAIGN_009_mean_reversion_midline_deduped_forensic/` |
| elapsed | 942.6s |
| C008 runs | 30 (train/val base + full cost stress) |
| C009 runs | 36 (train/val × 3 cost regimes) |
| test window | **NOT opened** |

---

## C008 deduped headline (base cost)

| split | trades | exp R | PF | pairs + | original exp R |
|---|---:|---:|---:|---:|---:|
| train | 216 | **−0.025** | 1.02 | 5/6 | −0.017 |
| validation | 138 | **+0.161** | 1.29 | 6/6 | +0.172 |
| full stress_15x | 469 | +0.043 | 1.07 | 4/6 | +0.040 |

**Screening gate:** FAIL — `train_expectancy_gte_zero` (same failed gate as original).

---

## C009 deduped headline (base cost)

| split | trades | exp R | PF | pairs + | original exp R |
|---|---:|---:|---:|---:|---:|
| train | 252 | **−0.025** | 0.97 | 2/6 | −0.062 |
| validation | 151 | **+0.186** | 1.37 | 4/6 | +0.170 |
| validation stress_2x | 151 | +0.135 | 1.25 | 3/6 | — |

**Screening gate:** FAIL — `train_expectancy_gte_zero` (same gate family as original).

---

## Key observations

1. **Trade counts identical** to original contaminated-era runs for train/validation base — duplicate SQLite rows were 1:1 redundant copies; dedupe did not change entry set.
2. **Train-fail / validation-positive shape persists** for both campaigns.
3. **C008 train exp** shifted slightly (−0.017 → −0.025) but remains negative.
4. **C009 train exp** improved vs original report (−0.062 → −0.025) but **still fails** gate; do not interpret as rescue.
5. **No broker/OANDA API calls** — local SQLite read only.

---

## Artifacts

| file | purpose |
|---|---|
| `research/deduped_c008_c009_rerun/metrics_summary.json` | aggregate metrics |
| `research/deduped_c008_c009_rerun/gate_result.json` | gate pass/fail |
| `research/deduped_c008_c009_rerun/run_manifest.json` | preflight + provenance |
| `research/deduped_c008_c009_rerun/evidence_status.json` | integrity flags |

Trade CSVs remain gitignored under forensic backtest directories.

---

## Explicit non-claims

- C008/C009 are **not** approved.
- Validation-positive metrics are **not** promotion evidence.
- This replay does **not** open the test lockbox or authorize paper/demo/live.
