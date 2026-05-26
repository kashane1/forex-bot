# Exit Artifact Inventory

**Date:** 2026-05-26  
**Branch:** `research-stop-and-exit-diagnostics-001`  
**Machine-readable:** [`research/exit_diagnostics/exit_artifact_inventory.json`](../../research/exit_diagnostics/exit_artifact_inventory.json)

> **Diagnostic only** — `strategy_evidence: false`. Trade CSVs are local/gitignored; this inventory records paths and field availability only.

---

## Summary

| metric | value |
|---|---|
| campaigns scanned | 14 |
| trade lists found | 14 / 14 |
| usable for diagnostics | 14 / 14 |
| DEDUP_SAFE | 1 (C015 deduped) |
| LIKELY_CONTAMINATED | 11 |
| NULL_BASELINE_REQUIRES_RERUN | 1 (C011 deduped) |
| UNKNOWN | 2 (C016, C017) |

---

## Per-campaign inventory

Evidence integrity labels from `research/contamination_audit/campaign_integrity_classification.json`. **Never mix contaminated and dedup-safe results without labels.**

| campaign | family | integrity | trades | exit_reason | bars_held | r_multiple | spread | stop_price | ambiguous | gap_fill | usable |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C002 | trend_following | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | no | no | yes |
| C003 | trend_adx | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | no | no | yes |
| C004 | volatility_breakout | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | no | no | yes |
| C007 | pullback | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | no | no | yes |
| C008 | mean_reversion | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | no | no | yes |
| C009 | mean_reversion | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | no | no | yes |
| C010 | session_breakout | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | yes | no | yes |
| C011 | random_entry_null | NULL_BASELINE_REQUIRES_RERUN | yes | yes | yes | yes | yes | yes | yes | no | yes |
| C012 | regime_switcher | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | yes | no | yes |
| C013 | cross_pair_rotation | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | yes | no | yes |
| C014 | calendar_event | LIKELY_CONTAMINATED | yes | yes | yes | yes | yes | yes | yes | no | yes |
| C015 | failed_breakout_reversal | **DEDUP_SAFE** | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| C016 | weekly_momentum | UNKNOWN | yes | yes | yes | yes | yes | yes | yes | yes | yes |
| C017 | vol_contraction_breakout | UNKNOWN | yes | yes | yes | yes | yes | yes | yes | yes | yes |

---

## Sample artifact paths

| campaign | sample path |
|---|---|
| C008 | `backtests/campaign_008_range_mean_reversion/runs/baseline/full/baseline_AUD_USD_H4_full_trades.csv` |
| C009 | `backtests/campaign_009_mean_reversion/runs/train/base/train_base_AUD_USD_H4_trades.csv` |
| C010 | `backtests/CAMPAIGN_010_session_breakout/folds/fold_00/fold_00_AUD_USD_trades.csv` |
| C011 deduped | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/folds/fold_00/fold_00_AUD_USD_trades.csv` |
| C015 deduped | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/folds/base/fold_00/fold_00_AUD_USD_trades.csv` |

---

## Gaps and notes

- **C006:** blocked — no trade artifacts (excluded from scan).
- **C011 original (non-deduped):** superseded; use deduped folder only.
- **C008/C009:** artifacts present but **LIKELY_CONTAMINATED** — descriptive exit forensics only; not promotion evidence.
- **C015 deduped:** preferred canonical lane for cross-campaign comparison where dedup-safe evidence is required.
- **ambiguous_exit / gap_fill:** recorded on C010–C017 fold campaigns; absent on C002–C009 baseline CSV schema.
- Trade CSVs remain **gitignored**; compact JSON summaries under `research/exit_diagnostics/` are committed.

---

## Generator

`python scripts/run_exit_diagnostics.py` — inventory phase only regenerates `exit_artifact_inventory.json`.
