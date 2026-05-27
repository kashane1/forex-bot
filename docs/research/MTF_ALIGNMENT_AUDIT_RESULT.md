# MTF / Higher-Timeframe Alignment Audit — Result

**Sprint:** Shared Signal and MTF Confluence Audit 001 · Phase 2  
**Classification:** **WARN** (no single shared MTF adapter; per-strategy + research paths audited)

## Modules inspected

| Area | Module / pattern |
|------|------------------|
| Cross-asset → H4 | `research/cross_asset_features/alignment.py` — availability_ts + `ffill` |
| D1AGG from H4 | `backtesting/d1_aggregation.py` + `regime_switcher_atr_percentile` |
| Weekly from H4 | `features/weekly_momentum.py`, `features/weekly_volatility.py` |
| Weekly strategies | `weekly_cross_sectional_momentum_low_turnover`, `weekly_volatility_contraction_breakout` |
| Confluence diagnostics | `scripts/run_mtf_confluence_diagnostics.py` (research-only) |

## Strategies using HTF features

| Strategy / area | HTF source | Join semantics |
|-----------------|------------|----------------|
| `regime_switcher_atr_percentile` | D1AGG from in-window H4 | Aggregate then filter `d1.time <= bar_ts`; regime uses trailing window **excluding** current D1 ATR reference from percentile window |
| Weekly momentum / vol breakout | H4 → weekly OHLC | `latest_completed_compressed_week` — completed week only |
| Cross-asset confluence | Daily external features | `observation_to_availability_ts` then backward `ffill` on H4 index |
| Most H4-only campaigns | None | N/A |

There is **no** universal shared `MTFAdapter` in `src/forex_bot/`. HTF logic is **strategy-specific** or **research/diagnostic**.

## Join semantics summary

| Pattern | Lookahead safe? |
|---------|----------------|
| `align_features_to_h4_with_availability` | **Yes** — daily close not available until `D+1 00:00 UTC` |
| D1AGG filtered to `<= decision_time` | **Yes** — forming day excluded until its close timestamp passed |
| Regime percentile window `[-(N+1):-1]` | **Yes** — current reference excluded from percentile denominator |
| Raw `ffill` without availability shift | **No** — not used for cross-asset production path |

## Evidence of no-lookahead

- `tests/research/test_cross_asset_h4_alignment.py` — weekend / stale flags
- `tests/unit/test_htf_backward_alignment_audit_001.py` — synthetic D1 vs H4 decision times (new)
- `regime_switcher` R3 invariants + structural tests in campaign scaffold tests

## Tests added

- `tests/unit/test_htf_backward_alignment_audit_001.py` (3 tests)

## Shared MTF adapter

**Does not exist** in production `src/`. Recommendation:

```text
forex_bot.features.htf_align.align_last_completed(
  decision_times, htf_frame, value_columns
) -> DataFrame
```

Contract: at each `decision_time`, use max `htf_time` where `htf_time <= decision_time` and `complete=True`. Emit `blocked_reason=HTF_UNAVAILABLE` when missing. Preserve `htf_feature_time` in `Signal.features`.

**Not implemented this sprint** — documented only to avoid invasive refactor mid-audit.

## Classification

**WARN:** Per-strategy HTF joins appear correct where tested, but absence of a **single enforced shared adapter** means new strategies could reintroduce exact-timestamp joins or forward-fill leakage. Cross-asset path is strong; generic H4+D1AGG path relies on strategy discipline.

## Recommended follow-up

- Optional small `htf_align` module + migrate `regime_switcher` first
- Confluence grader must consume availability-aligned features only (already diagnostic-only)
