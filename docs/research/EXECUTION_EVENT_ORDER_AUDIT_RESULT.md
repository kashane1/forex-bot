# Execution Event Order Audit — Result

**Sprint:** Audit 001 · Phase 6  
**Classification:** **PASS** (engine chain documented and tested; C019 compatible)

## Exit priority (`backtesting/engine.py`)

When `thesis_invalidation_enabled` (CAMPAIGN_019 path):

1. **thesis_invalidation** (z-score vs frozen long/short thresholds) — bid/ask close
2. **gap_through** (opt-in): adverse stop at bar open, then favorable TP at open
3. **Range chain** (if no gap fill): stop/trailing/protective → target → time
4. Conservative: stop side checked before target on ambiguous bars

Trailing stop updates occur **before** exit evaluation on the same bar.

## C019 compatibility

Precommitted C019 thesis-invalidation priority is enforced:

- `tests/unit/test_mean_reversion_thesis_invalidation.py`:
  - `test_thesis_invalidation_priority_before_stop`
  - `test_process_bar_exit_thesis_invalidation_*`
- Engine flag wiring from `configs/campaign_019_*.yaml` — **not modified** this sprint

## Ambiguous same-bar cases

- Documented in `GAP_FILL_AND_AMBIGUOUS_EXIT_MODEL.md`
- `tests/unit/test_ambiguous_exit.py`, `tests/unit/test_gap_fill.py`

## EOD / weekend

- Session filter blocks **entries** in rollover window; not a separate “EOD exit” for open trades unless strategy/time stop applies.
- Native D1 EOD contamination avoided via D1AGG design (Phase 1).

## Tests added

None required — existing suite sufficient. This phase is documentation + verification.

## Classification

**PASS** for deterministic ordering where enabled. Campaigns without thesis_invalidation use stop → target → time sub-chain only.
