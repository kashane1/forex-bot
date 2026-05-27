# M1 Data Quality Validator Result

## Status

Implemented `scripts/validate_m1_canonical_store.py` with synthetic tests in `tests/unit/test_validate_m1_canonical_store.py`.

## Reported Fields

- instrument
- date range
- expected M1 count, excluding weekend minutes
- actual M1 count
- missing minutes
- duplicate timestamps
- incomplete candles
- negative or zero spreads
- extreme spreads
- weekend gaps excluded flag
- first/last timestamp
- compact data hash
- generated M5/M15/H1/H4/D1AGG counts
- incomplete aggregate count by timeframe

## Output

The script emits compact JSON only. It does not print raw candles or broker payloads.

## Tests

Added tests for:

- missing minute detected
- duplicate timestamp detected
- incomplete candle detected
- negative spread detected
- aggregate counts expected
- weekend gap not treated as missing

## Validation

```bash
pytest tests/unit/test_validate_m1_canonical_store.py -q
ruff check scripts/validate_m1_canonical_store.py tests/unit/test_validate_m1_canonical_store.py
```

Both passed.

## Approval Statement

This validator is infrastructure only. No strategy evidence was run and no strategy was approved.
