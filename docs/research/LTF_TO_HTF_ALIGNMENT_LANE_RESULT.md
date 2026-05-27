# LTF To HTF Alignment Lane Result

## Status

Implemented `src/forex_bot/features/ltf_htf_alignment.py` with tests in `tests/unit/test_ltf_htf_alignment.py`.

## Contract

- Execution timeframe defaults to `M15`.
- `M5` is supported but not the default.
- Context timeframes are `H1`, `H4`, and `D1AGG`.
- All context joins use `htf_align.align_last_completed`.
- Incomplete HTF rows are filtered before alignment.
- Output includes `available_data_cutoff` and per-context feature-time provenance fields:
  - `h1_feature_time`
  - `h4_feature_time`
  - `d1agg_feature_time`

## Availability Policy

An M5/M15 decision can use only completed context rows with feature time less than or equal to the decision time. Future or incomplete H1/H4/D1AGG context returns the existing `HTF_UNAVAILABLE` reason. Excessively old context returns `HTF_STALE` when `max_staleness` is configured.

## Tests

Added tests for:

- M15 at 10:15 cannot use an H1 candle timestamped 11:00
- M15 at 12:00 can use completed H1/H4 context timestamped 12:00
- M5/M15 cannot use incomplete H4/D1AGG context
- stale context returns `HTF_STALE`
- unavailable context returns `HTF_UNAVAILABLE`
- unsupported execution timeframe is refused

## Validation

```bash
pytest tests/unit/test_ltf_htf_alignment.py -q
ruff check src/forex_bot/features/ltf_htf_alignment.py tests/unit/test_ltf_htf_alignment.py
```

Both passed.

## Approval Statement

No strategy evidence was run and no strategy was approved.
