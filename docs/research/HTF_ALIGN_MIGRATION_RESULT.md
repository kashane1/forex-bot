# HTF Align — Migration Result

**Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001` · **Date:** 2026-05-27

## Migrated code path

| Before | After |
|--------|-------|
| Inline D1AGG ATR + regime math in `regime_switcher_atr_percentile.py` | `forex_bot.features.d1agg_htf` + thin strategy wrapper |
| Implicit last-completed D1 bar | `htf_align.align_last_completed()` via `regime_gate_from_h4_candles` / `aligned_d1_atr_at_decision` |

Strategy file: ~117 lines removed (duplicate logic), re-exports preserved for unit tests.

## Tests added

`tests/unit/test_d1agg_htf_migration.py`:

- `_wilder_atr_over_d1agg` ≡ `d1agg_htf.wilder_atr_over_d1agg`
- `_compute_regime` ≡ `d1agg_htf.compute_regime_label`
- `aligned_d1_atr_at_decision` matches gate reference at signal bar

`tests/unit/test_regime_switcher_atr_percentile.py`: percentile assertion targets `d1agg_htf.compute_regime_label`.

## Behavior equivalence result

**PASS** on synthetic fixtures — no `BLOCKED_BEHAVIOR_CHANGE_RISK`. Gate labels and reference ATR match pre-migration helpers.

## Signal provenance (additive)

Regime-switcher signals may include `decision_time`, `htf_feature_times`, `d1agg_htf_time` when emitted post-migration.

## Remaining unmigrated HTF paths

- Weekly strategies (C016/C017)
- Confluence / cross-asset diagnostics
- CAMPAIGN_013 cross-pair alignment

## Future recommendation

Next: migrate research confluence diagnostic alignment behind feature flag + fixture parity; document weekly exception in [`HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md`](HTF_ALIGNMENT_POLICY_FOR_FUTURE_STRATEGIES.md).

## No-approval statement

Infrastructure only. CAMPAIGN_012 verdict unchanged.
