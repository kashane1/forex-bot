# Backtrader Entry Parity Hardening — Result

**Branch:** `infra-backtrader-entry-parity-hardening-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## Summary

After formalizing quote→USD PnL conversion (`home_currency_v1`) and defaulting
to engine-aligned risk windows, entry timestamp comparison confirms **±1 trade
tolerance** for C008, C009, and C018.

| Campaign | Bespoke | Backtrader | Gap | BT-only |
|---|---:|---:|---:|---:|
| C008 | 354 | 353 | 1 | 0 |
| C009 | 403 | 402 | 1 | 0 |
| C018 | 378 | 377 | 1 | 0 |

**100%** of Backtrader entries are a subset of bespoke. Common trades share
identical entry and exit timestamps.

---

## Remaining bespoke-only entry

All three campaigns share one unexplained bespoke-only entry:

- **Instrument:** GBP_USD  
- **Time:** 2024-01-16T06:00:00+00:00 (validation split)  
- **Attribution:** `risk_engine_or_orchestration_divergence`

No Backtrader-only entries. No position-overlap explanation required.

---

## Adjustment experiment (post-hardening)

From `research/entry_parity/backtrader_adjustment_experiment.json`:

| Campaign | Delta | Delta % |
|---|---:|---:|
| C008 | 1 | 0.28% |
| C009 | 1 | 0.25% |
| C018 | 1 | 0.26% |

Pre-fix legacy BT counts (279/332/314) are superseded by refreshed parity
artifacts (353/402/377).

---

## Exit parity (unchanged classification)

Exit-reason shares remain **CLOSE_MATCH** for all campaigns. See
`research/backtrader_exit_parity/exit_reason_comparison.csv`.

---

## No approval

No strategy approved. `configs/approved_strategies.yaml` remains `approved: []`.
All campaign verdicts unchanged.
