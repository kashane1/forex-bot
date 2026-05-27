# Signal Provenance Fields Remediation — Result

**Model:** `src/forex_bot/domain/signals.py`  
**Classification:** **PASS** (additive, optional)

## Fields added (all optional, default `None`)

- `campaign_id`
- `strategy_run_id`
- `decision_time`
- `available_data_cutoff`
- `source_candle_timestamp`
- `htf_feature_times`

`timestamp` retained for backward compatibility.

## Compatibility

Existing `Signal(...)` constructions unchanged. Frozen Pydantic models accept new optional fields.

## Validation

`validate_signal_provenance(signal)` — ensures `decision_time <= available_data_cutoff` and HTF times not after decision.

## Exporter changes

**Deferred** for trade CSV columns (would widen all campaign exports). Runners may pass provenance via `write_summary_json(..., **extras)` when needed.

## Tests

`tests/unit/test_signal_provenance_fields.py`

## Remaining migration

Populate fields in new campaign runners; backfill not required for historical artifacts.
