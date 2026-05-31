# CAMPAIGN_015 Deduped vs Deduped Null — Check

**Sprint:** CAMPAIGN_011_DEDUPED_NULL_BASELINE_001  
**Date:** 2026-05-26  
**Status:** **RUN** (non-gating diagnostic; does not change CAMPAIGN_015 verdict)

## Inputs

| role | path |
|---|---|
| CAMPAIGN_015 deduped | `backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/fold_detail.json` |
| CAMPAIGN_011 deduped null | `backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json` |
| Canonical null rollup | `research/null_baselines/campaign_011_deduped_null_baseline.json` |

Tool: `scripts/run_campaign_015_anti_overfit_diagnostics.py` (read-only classifier).

## Result

| field | value |
|---|---|
| **anti_overfit_label** | **WITHIN_NULL** |
| CAMPAIGN_015 verdict (unchanged) | **REJECT** |
| null config hash match | `6f2c04981a3f02f08bae65b73b09f873de6a42cb067b9462885c5ffd2c6a1206` |
| mean per-fold gap R (campaign − null) | −0.00293 |
| worse_than_null | false |

The deduped null baseline does **not** change the CAMPAIGN_015 anti-overfit classification relative to the prior deduped diagnostic run against the same local null fold detail. CAMPAIGN_015 remains **REJECT** with **WITHIN_NULL** anti-overfit (informational only — not approval).

## Command (repro)

```bash
PYTHONPATH=src .venv/bin/python scripts/run_campaign_015_anti_overfit_diagnostics.py \
  --campaign-fold-detail backtests/CAMPAIGN_015_failed_breakout_reversal_deduped/walk_forward/fold_detail.json \
  --null-fold-detail backtests/CAMPAIGN_011_random_entry_anchor_deduped/walk_forward/fold_detail.json \
  --out-json research/campaign_015/diagnostics/null_and_anti_overfit_vs_deduped_canonical.json \
  --out-md research/campaign_015/diagnostics/null_and_anti_overfit_vs_deduped_canonical.md
```

(Optional committed copies under `research/campaign_015/diagnostics/` may be added in a follow-up; this sprint documents the check outcome only.)
