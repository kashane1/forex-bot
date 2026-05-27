# HTF Align — Migration Design

**Sprint:** `infra-next-bar-open-policy-and-htf-align-migration-001` · **Date:** 2026-05-27

## Candidate paths

| Path | HTF need | Risk |
|------|----------|------|
| **CAMPAIGN_012 regime_switcher D1AGG** | H4 → D1AGG gate; trailing ATR percentile | Low — pure refactor to shared helper; equivalence tests |
| Research confluence diagnostics | Cross-asset / MTF alignment | Medium — research-only, fewer production fixtures |
| Weekly C016/C017 | Completed-week compression | **Not migrated** — different period semantics |
| Cross-pair strength rotation | Availability alignment | Medium — multi-instrument timestamps |
| Native OANDA D1 | Invalid for D1AGG research | **Forbidden** where D1AGG required |

## Selected target

**`regime_switcher_atr_percentile` D1AGG regime gate** via new module `src/forex_bot/features/d1agg_htf.py`:

- `wilder_atr_over_d1agg`, `compute_regime_label` — extracted from strategy (aliases preserved on strategy module for tests)
- `regime_gate_from_h4_candles` — aggregates H4→D1AGG, uses `htf_align.align_last_completed()` for decision-time ATR
- `aligned_d1_atr_at_decision` — provenance helper

## Why selected

- Shared audit already introduced `htf_align.align_last_completed()` with HTF_UNAVAILABLE / HTF_STALE semantics.
- Regime switcher is the canonical D1AGG consumer in production strategy code.
- Fixture equivalence: ATR series and regime labels match pre-migration helpers (`tests/unit/test_d1agg_htf_migration.py`).
- Signals gain additive `decision_time`, `htf_feature_times`, `d1agg_htf_time` without changing gate math on fixtures.

## Behavior-preservation strategy

1. Keep strategy-facing aliases `_wilder_atr_over_d1agg`, `_compute_regime` delegating to `d1agg_htf`.
2. Compare old vs new ATR/regime on 600-bar synthetic fixture (finite values exact match; NaN pairs match).
3. Compare `regime_gate_from_h4_candles` reference ATR to `aligned_d1_atr_at_decision` at signal bar.
4. If any fixture diverges → stop, document `BLOCKED_BEHAVIOR_CHANGE_RISK`, revert behavior change.

## Explicitly not migrated

- Weekly momentum / volatility contraction (completed-week helpers remain separate).
- Confluence diagnostic path (future sprint).
- CAMPAIGN_012 walk-forward artifacts (no rerun).
- Cross-pair rotation alignment.

## Blocked conditions

- Future HTF timestamp > decision time in features
- Incomplete HTF bar drives signal
- Fixture mismatch on regime label or ATR reference

## No strategy verdict changes

CAMPAIGN_012 remains **REJECT**. No campaign rerun required for this infrastructure sprint.
