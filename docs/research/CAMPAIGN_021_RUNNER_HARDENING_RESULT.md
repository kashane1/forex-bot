# CAMPAIGN_021 — Runner Hardening Result

**Date:** 2026-05-27  
**Branch:** `research-campaign-021-ltf-mtf-confluence-execution-001`

## Changes

- Extended `scripts/run_campaign_021_ltf_mtf_confluence.py` with gate-disciplined commands:
  - `train-only`, `train-validation`, `validation`, `test`, `full`
  - `--data-feature-preflight`
- Added `src/forex_bot/research/campaign_021_gates.py` (frozen gate evaluation)
- Added `src/forex_bot/research/campaign_021_loader.py` (Postgres M1 → frames + native D1AGG)
- `gate_state.json` persists train/validation/parity lockbox eligibility
- Validation refuses to run if `train_gate_pass` is false
- Test refuses to run unless `test_lockbox_allowed` is true
- Rejects `signal_bar_close`, M1-derived D1AGG, non-empty approved registry
- Raw trade CSVs written to `research/campaign_021/raw/` (gitignored)

## Tests

- `tests/unit/test_campaign_021_gates.py`
- `tests/unit/test_campaign_021_runner_guards.py`

## No approval

`configs/approved_strategies.yaml` remains `approved: []`.
