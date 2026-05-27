# Shared HTF Align Module — Result

**Module:** `src/forex_bot/features/htf_align.py`  
**Classification:** **PASS** (module + tests; limited migration)

## API

`align_last_completed(decision_times, htf_frame, value_columns, *, htf_time_column="time", complete_column="complete", max_staleness=None, prefix="htf")`

Returns aligned values, `{prefix}_{col}_time` provenance, `{prefix}_blocked_reason`, `{prefix}_is_stale`.

Constants: `HTF_UNAVAILABLE`, `HTF_STALE`.

`validate_signal_provenance()` / `validate_htf_provenance()` for signal-level checks.

## Contract

- Max `htf_time <= decision_time`
- Incomplete HTF rows excluded when `complete_column` present
- Missing → `HTF_UNAVAILABLE`; stale beyond `max_staleness` → `HTF_STALE`

## Tests

`tests/unit/test_htf_align.py` (5 tests)

## Migration status

**No production strategy migrated** this sprint (risk of behavior drift). Existing paths remain:

- `regime_switcher_atr_percentile` — inline `d1.time <= bar_ts` filter
- `research/cross_asset_features/alignment.py` — availability-shifted ffill

**Recommendation:** New strategies and refactors should use `htf_align`; precommit should require shared adapter or documented exception.
